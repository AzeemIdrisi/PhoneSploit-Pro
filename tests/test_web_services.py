"""Parsers, catalog coverage, and artifact path guards. No device required."""

from modules.services.catalog import build_catalog, feature_ids
from modules.services.dispatch import missing_handlers
from modules.services.parse import (
    parse_battery,
    parse_content_rows,
    parse_devices_list,
    parse_location,
    parse_ls,
    parse_packages,
    parse_usage,
    safe_artifact_relative,
)
from modules.services.runner import AdbError, validate_package, validate_remote_path, validate_serial


def test_catalog_covers_every_handler() -> None:
    assert missing_handlers() == []
    ids = feature_ids()
    assert "webui" not in ids
    assert "metasploit" in ids
    assert "shell" in ids
    catalog = build_catalog()
    metasploit = next(item for item in catalog["features"] if item["id"] == "metasploit")
    assert metasploit["tier"] == "terminal"
    mirror = next(item for item in catalog["features"] if item["id"] == "mirror")
    assert mirror["tier"] == "screen"
    camera = next(item for item in catalog["features"] if item["id"] == "camera_live")
    assert camera["tier"] == "host_process"
    wifi = [item for item in catalog["features"] if item["id"] == "wifi_toggle"]
    assert len(wifi) == 2


def test_parse_devices_and_packages() -> None:
    raw = "List of devices attached\nABC123\tdevice product:foo model:Pixel\n192.168.1.5:5555\tdevice\n"
    devices = parse_devices_list(raw)
    assert devices[0]["serial"] == "ABC123"
    assert devices[0]["transport"] == "usb"
    assert devices[1]["transport"] == "wifi"
    assert parse_packages("package:com.android.settings\npackage:com.example.app\n") == [
        "com.android.settings",
        "com.example.app",
    ]


def test_parse_battery_location_usage_ls() -> None:
    battery = parse_battery("  level: 80\n  status: 2\n")
    assert battery["level"] == "80"
    locations = parse_location("last Location[gps 12.9716,77.5946 hAcc=1]")
    assert locations[0]["provider"] == "gps"
    usage = parse_usage("com.example  lastTimeUsed=5000 totalTimeInForeground=60000")
    assert usage[0]["package"] == "com.example"
    entries = parse_ls("Download/\nphoto.jpg\n")
    assert entries[0] == {"name": "Download", "kind": "dir"}
    assert entries[1]["kind"] == "file"
    rows = parse_content_rows("Row: 0 address=+1, body=hello")
    assert rows[0]["address"] == "+1"


def test_path_and_serial_guards() -> None:
    assert validate_serial("emulator-5554") == "emulator-5554"
    assert validate_serial("192.168.1.9:5555")
    try:
        validate_serial("bad serial")
        raise AssertionError("expected rejection")
    except AdbError:
        pass
    assert validate_package("com.android.settings")
    assert validate_remote_path("/sdcard/Download")
    try:
        validate_remote_path("/sdcard/../etc")
        raise AssertionError("expected rejection")
    except AdbError:
        pass
    assert safe_artifact_relative("Downloaded-Files", "sms.txt")
    assert not safe_artifact_relative("Downloaded-Files", "../secrets")


_PROBE_ARGUMENTS = "-p 5555,5554 -sT -sV --version-intensity 1 -T4"
_LIVE_HOSTS = ("192.168.1.5", "192.168.1.20")
_ADB_HOST = {
    "tcp": {
        5555: {
            "state": "open",
            "product": "Android Debug Bridge",
            "version": "",
            "extrainfo": "",
            "name": "adb",
        }
    }
}


class _FakePortScanner:
    def __init__(self, calls: list[tuple[str, str]], probes: dict[str, object]) -> None:
        self._calls = calls
        self._probes = probes
        self._hosts: dict[str, dict] = {}

    def scan(self, hosts: str = "", arguments: str = "") -> None:
        self._calls.append((hosts, arguments))
        if "-sn" in arguments.split():
            self._hosts = {
                "192.168.1.20": {"status": {"state": "up"}},
                "192.168.1.5": {"status": {"state": "up"}},
                "192.168.1.40": {"status": {"state": "down"}},
            }
            return
        ip = str(hosts).split()[0]
        scripted = self._probes.get(ip, {"tcp": {}})
        if scripted == "raise":
            raise RuntimeError("probe failed")
        self._hosts = {ip: scripted}  # type: ignore[dict-item]

    def all_hosts(self) -> list[str]:
        return list(self._hosts)

    def __getitem__(self, host: str) -> dict:
        return self._hosts[host]


def _patch_scanner(monkeypatch, probes: dict[str, object]) -> list[tuple[str, str]]:
    from modules.services import operations as ops

    calls: list[tuple[str, str]] = []

    def factory(_config: object) -> _FakePortScanner:
        return _FakePortScanner(calls, probes)

    monkeypatch.setattr(ops, "_port_scanner", factory)
    monkeypatch.setattr(ops, "get_ip_address", lambda: "192.168.1.10")
    return calls


def test_scan_network_streams_hosts_and_progress(monkeypatch) -> None:
    from modules.services import operations as ops

    calls = _patch_scanner(monkeypatch, {"192.168.1.5": _ADB_HOST, "192.168.1.20": {"tcp": {}}})
    events: list[dict] = []

    def on_event(event: dict) -> None:
        events.append(
            {
                "phase": event["phase"],
                "progress": event["progress"],
                "hosts": [dict(row) for row in event.get("hosts") or []],
                "message": event.get("message"),
            }
        )
        raise RuntimeError("listener failed")

    result = ops.scan_network(object(), on_event=on_event, should_cancel=lambda: False)

    assert result["ok"] is True
    assert result["data"]["cancelled"] is False
    assert result["data"]["subnet"] == "192.168.1.10/24"
    rows = result["data"]["hosts"]
    assert [row["ip"] for row in rows] == list(_LIVE_HOSTS)
    assert rows[0]["adb"] == "5555/tcp open Android Debug Bridge"
    assert rows[0]["hint"] == "Strong: ADB fingerprint"
    assert rows[1]["adb"] == ""
    assert rows[1]["hint"] == ""
    for row in rows:
        assert {"ip", "adb", "hint"} <= set(row)

    assert [event["progress"] for event in events] == [0, 0.5, 1.0]
    assert events[0]["phase"] == "discover"
    assert "192.168.1.10/24" in events[0]["message"]
    assert [len(event["hosts"]) for event in events if event["phase"] == "probe"] == [1, 2]
    assert events[1]["hosts"][0]["ip"] == "192.168.1.5"
    assert [row["ip"] for row in events[2]["hosts"]] == list(_LIVE_HOSTS)
    assert calls == [
        ("192.168.1.10/24", "-sn"),
        ("192.168.1.5", _PROBE_ARGUMENTS),
        ("192.168.1.20", _PROBE_ARGUMENTS),
    ]


def test_scan_network_cancel_returns_partial_hosts(monkeypatch) -> None:
    from modules.services import operations as ops

    calls = _patch_scanner(monkeypatch, {"192.168.1.5": _ADB_HOST, "192.168.1.20": _ADB_HOST})
    events: list[dict] = []
    checks = {"n": 0}

    def should_cancel() -> bool:
        checks["n"] += 1
        return checks["n"] >= 2

    result = ops.scan_network(
        object(),
        on_event=events.append,
        should_cancel=should_cancel,
    )

    assert result["ok"] is True
    assert result["data"]["cancelled"] is True
    assert "cancel" in result["message"].lower()
    assert [row["ip"] for row in result["data"]["hosts"]] == ["192.168.1.5"]
    assert {"ip", "adb", "hint"} <= set(result["data"]["hosts"][0])
    assert [event["progress"] for event in events] == [0, 0.5]
    assert len(events[1]["hosts"]) == 1
    assert calls == [
        ("192.168.1.10/24", "-sn"),
        ("192.168.1.5", _PROBE_ARGUMENTS),
    ]


def test_scan_network_continues_after_probe_error(monkeypatch) -> None:
    from modules.services import operations as ops

    calls = _patch_scanner(monkeypatch, {"192.168.1.5": _ADB_HOST, "192.168.1.20": "raise"})
    result = ops.scan_network(object())
    assert result["ok"] is True
    assert result["data"]["cancelled"] is False
    assert result["data"]["hosts"][0]["hint"] == "Strong: ADB fingerprint"
    assert result["data"]["hosts"][1] == {"ip": "192.168.1.20", "adb": "", "hint": ""}
    assert len(calls) == 3


def test_scan_network_requires_local_ip(monkeypatch) -> None:
    from modules.services import operations as ops

    def scanner(_config: object) -> None:
        raise AssertionError("scanner should not run")

    monkeypatch.setattr(ops, "get_ip_address", lambda: None)
    monkeypatch.setattr(ops, "_port_scanner", scanner)
    result = ops.scan_network(object())
    assert result["ok"] is False
    assert "local IP" in result["message"]


def test_job_progress_publishes_and_cancel() -> None:
    from server.state import JOBS

    job = JOBS.create("scan_network")
    assert job.to_dict()["progress"] is None
    queue = JOBS.subscribe()
    try:
        JOBS.update(
            job,
            status="running",
            message="Probing",
            progress=0.5,
            data={"subnet": "10.0.0.0/24", "hosts": [{"ip": "10.0.0.2", "adb": "", "hint": ""}]},
        )
        payload = queue.get_nowait()
        assert payload["progress"] == 0.5
        assert payload["data"]["hosts"][0]["ip"] == "10.0.0.2"
        assert payload["message"] == "Probing"
        JOBS.update(job, message="Still going")
        merged = queue.get_nowait()
        assert merged["progress"] == 0.5
        assert merged["data"]["subnet"] == "10.0.0.0/24"
        assert merged["message"] == "Still going"
        assert merged["status"] == "running"
    finally:
        JOBS.unsubscribe(queue)
    assert JOBS.cancel(job.id) is True
    assert JOBS.is_cancelled(job.id) is True
    assert JOBS.cancel("missing-job") is False
    assert JOBS.is_cancelled("missing-job") is False


def test_cancel_job_endpoint() -> None:
    from fastapi.testclient import TestClient

    from server.app import app
    from server.state import JOBS

    job = JOBS.create("scan_network")
    with TestClient(app) as client:
        missing = client.post("/api/jobs/missing-job/cancel")
        assert missing.status_code == 404
        found = client.post(f"/api/jobs/{job.id}/cancel")
    assert found.status_code == 200
    assert found.json() == {"ok": True}
    assert JOBS.is_cancelled(job.id)
