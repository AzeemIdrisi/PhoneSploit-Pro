"""WiFi utility services."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from modules.services.adb import ADBService, OperationResult
from modules.services.context import ServiceContext
from modules.wifi_utils import _collect_saved_ssids


def wifi_status_summary(adb: ADBService) -> OperationResult:
    raw = adb.output(["shell", "dumpsys", "wifi"])
    lines = []
    for line in raw.splitlines():
        s = line.strip()
        if any(
            k in s.lower()
            for k in (
                "ssid",
                "bssid",
                "ipaddress",
                "ip address",
                "rssi",
                "frequency",
                "state:",
                "mwifiinfo",
                "link speed",
            )
        ):
            lines.append(s)
    if not lines:
        lines = raw.splitlines()[:80]
    return OperationResult(True, "WiFi status", data=lines)


def wifi_status_save(ctx: ServiceContext) -> OperationResult:
    raw = ctx.adb.output(["shell", "dumpsys", "wifi"])
    out_dir = ctx.ensure_output_dir()
    path = out_dir / "dumpsys-wifi.txt"
    try:
        path.write_text(raw, encoding="utf-8", errors="replace")
    except OSError as e:
        return OperationResult(False, str(e))
    return OperationResult(True, f"Saved: {path}", data=str(path))


def wlan_ip(adb: ADBService) -> OperationResult:
    out = adb.output(["shell", "ip", "addr", "show", "wlan0"])
    if "does not exist" in out.lower() or not out.strip():
        out = adb.output(["shell", "ip", "addr"])
    return OperationResult(True, "WLAN IP info", data=out)


def wifi_toggle(adb: ADBService, mode: str) -> OperationResult:
    if mode not in ("enable", "disable"):
        return OperationResult(False, "Use enable or disable")
    r = adb.run(["shell", "svc", "wifi", mode])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        return OperationResult(True, out or f"WiFi {mode}d")
    return OperationResult(False, out or "failed")


def ping_connectivity(adb: ADBService, host: str = "8.8.8.8") -> OperationResult:
    r = adb.run(["shell", "ping", "-c", "4", host])
    text = (r.stdout + r.stderr).strip()
    return OperationResult(r.returncode == 0, text, data=text)


def saved_wifi_networks(adb: ADBService) -> OperationResult:
    ssids, note = _collect_saved_ssids()
    if not ssids:
        return OperationResult(
            False,
            "Could not detect saved networks from this device",
            error=note,
        )
    return OperationResult(
        True,
        f"{len(ssids)} network(s)",
        data={"ssids": ssids, "note": note},
    )
