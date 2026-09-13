import re
import subprocess
from typing import Any

from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_warning,
    confirm,
    task_status,
    show_options,
    go_back_to_main_menu,
    adb,
    adb_output,
    get_adb_executable,
    ask,
)


def get_shell(config: AppConfig) -> None:
    console.print("[bold cyan]Opening interactive ADB shell…[/bold cyan] [dim](exit shell to return)[/dim]")
    exe = get_adb_executable()
    if not exe:
        print_error("ADB not available.")
        return
    subprocess.run([exe, "shell"])


def lookup_mac_vendor(mac: str) -> str | None:
    """Offline IEEE OUI lookup; returns None if the library is missing or unknown."""
    mac = (mac or "").strip()
    if not mac:
        return None
    try:
        from mac_vendor_lookup import MacLookup

        return MacLookup().lookup(mac)
    except Exception:
        return None


def _lookup_mcc_mnc(plmn: str) -> list[dict[str, Any]]:
    plmn = re.sub(r"\D", "", plmn or "")
    if len(plmn) < 5:
        return []
    mcc, mnc = plmn[:3], plmn[3:]
    try:
        from mccmnc import find_matches

        matches = find_matches(user_mcc=mcc, user_mnc=mnc)
        if not matches:
            return []
        return [m if isinstance(m, dict) else {"raw": str(m)} for m in matches]
    except Exception:
        return []


def _access_style(access: str) -> str:
    low = (access or "").lower()
    if "available" in low:
        return "[green]Available[/green]"
    if "restricted" in low:
        return "[yellow]Restricted[/yellow]"
    return "[dim]Not on this Android[/dim]"


def _collect_imei() -> str | None:
    from modules.data_extraction import _decoded_imei, _imei_from_dumpsys

    dumpsys = adb_output(["shell", "dumpsys", "iphonesubinfo"])
    imei = _imei_from_dumpsys(dumpsys) if dumpsys.strip() else None
    if not imei:
        imei = _decoded_imei()
    if not imei:
        for prop in (
            "persist.radio.imei",
            "ril.IMEI",
            "gsm.imei",
            "ro.ril.oem.imei",
        ):
            val = adb_output(["shell", "getprop", prop]).strip()
            if val and val.lower() not in ("", "unknown", "null"):
                imei = val
                break
    return imei


def _parse_accounts(raw: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    email_re = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    for line in raw.splitlines():
        line = line.strip()
        if "type=" in line.lower() or "Account {" in line:
            acc_type = ""
            name = ""
            m_type = re.search(r"type=([^,\s}]+)", line)
            m_name = re.search(r"name=([^,}]+)", line)
            if m_type:
                acc_type = m_type.group(1).strip()
            if m_name:
                name = m_name.group(1).strip()
            if acc_type or name:
                rows.append({"type": acc_type, "name": name})
        for email in email_re.findall(line):
            rows.append({"type": "(email in dump)", "name": email})
    dedup: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for r in rows:
        key = (r.get("type", ""), r.get("name", ""))
        if key not in seen:
            seen.add(key)
            dedup.append(r)
    return dedup


def get_device_info(config: AppConfig) -> None:
    props = {
        "Model":            ["getprop", "ro.product.model"],
        "Manufacturer":     ["getprop", "ro.product.manufacturer"],
        "Chipset":          ["getprop", "ro.product.board"],
        "Android Version":  ["getprop", "ro.build.version.release"],
        "Security Patch":   ["getprop", "ro.build.version.security_patch"],
        "Device":           ["getprop", "ro.product.vendor.device"],
        "SIM Operator":     ["getprop", "gsm.sim.operator.alpha"],
        "Encryption":       ["getprop", "ro.crypto.state"],
        "Build Date":       ["getprop", "ro.build.date"],
        "SDK Version":      ["getprop", "ro.build.version.sdk"],
        "WiFi Interface":   ["getprop", "wifi.interface"],
    }

    with task_status("[info]Fetching device information…[/info]"):
        results = {label: adb_output(["shell"] + cmd) for label, cmd in props.items()}
        imei = _collect_imei()
        serial = adb_output(["shell", "getprop", "ro.serialno"]).strip()
        boot_serial = adb_output(["shell", "getprop", "ro.boot.serialno"]).strip()
        android_id = adb_output(["shell", "settings", "get", "secure", "android_id"]).strip()

    table = Table(title="Device Information", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="bold yellow")
    table.add_column("Value", style="white")

    for label, value in results.items():
        table.add_row(label, value or "[dim]N/A[/dim]")

    imei_display = imei or "[yellow]Not accessible via ADB on this Android version[/yellow]"
    table.add_row("IMEI", imei_display)
    table.add_row("Serial", serial or "[dim]N/A[/dim]")
    table.add_row("Boot Serial", boot_serial or "[dim]N/A[/dim]")
    table.add_row("Android ID", android_id or "[dim]N/A[/dim]")

    console.print(table)


def accounts_on_device(config: AppConfig) -> None:
    if not confirm("List account types/names from dumpsys account (no tokens)?"):
        return
    with task_status("[info]Reading accounts…[/info]"):
        raw = adb_output(["shell", "dumpsys", "account"])
        rows = _parse_accounts(raw) if raw.strip() else []
    access = "Available" if rows else "Restricted"
    console.print(f"Access: {_access_style(access)}")
    if not rows:
        print_error("No account data parsed on this device.")
        return
    table = Table(title="Accounts on device", show_header=True, header_style="bold cyan")
    table.add_column("Type", style="bold yellow")
    table.add_column("Name / hint", style="white")
    for row in rows:
        table.add_row(row.get("type", ""), row.get("name", ""))
    console.print(table)


def sim_operator_info(config: AppConfig) -> None:
    keys = {
        "sim_operator_alpha": "gsm.sim.operator.alpha",
        "sim_operator_numeric": "gsm.sim.operator.numeric",
        "sim_country": "gsm.sim.operator.iso-country",
        "network_operator_alpha": "gsm.operator.alpha",
        "network_operator_numeric": "gsm.operator.numeric",
        "network_country": "gsm.operator.iso-country",
    }
    with task_status("[info]Reading SIM / operator props…[/info]"):
        values: dict[str, str] = {}
        for label, prop in keys.items():
            val = adb_output(["shell", "getprop", prop]).strip()
            values[label] = val if val and val.lower() not in ("", "unknown") else ""
    access = "Available" if any(values.values()) else "Not on this Android / no SIM"
    console.print(f"Access: {_access_style(access)}")
    table = Table(title="SIM / operator", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="bold yellow")
    table.add_column("Value", style="white")
    for k, v in values.items():
        table.add_row(k, v or "—")
        if k.endswith("_numeric") and v:
            matches = _lookup_mcc_mnc(v)
            if matches:
                table.add_row("  ↳ MCC-MNC lookup", str(matches[0]))
    console.print(table)


def bluetooth_devices(config: AppConfig) -> None:
    with task_status("[info]Reading Bluetooth dump…[/info]"):
        raw = adb_output(["shell", "dumpsys", "bluetooth_manager"])
        if not raw.strip():
            raw = adb_output(["shell", "dumpsys", "bluetooth"])
    devices: list[dict[str, str]] = []
    mac_re = re.compile(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}")
    for line in raw.splitlines():
        if mac_re.search(line):
            mac = mac_re.search(line).group(0)
            name = ""
            m_name = re.search(r"name[=:]\s*([^\s,]+)", line, re.I)
            if m_name:
                name = m_name.group(1).strip('"')
            devices.append({"address": mac, "name": name})
    dedup: list[dict[str, str]] = []
    seen_macs: set[str] = set()
    for d in devices:
        mac = d["address"].upper()
        if mac in seen_macs:
            continue
        seen_macs.add(mac)
        dedup.append(d)
    access = "Available" if dedup else ("Not on this Android" if not raw.strip() else "Restricted")
    console.print(f"Access: {_access_style(access)}")
    if not dedup:
        print_error("No Bluetooth devices parsed.")
        return
    table = Table(title="Bluetooth devices", show_header=True, header_style="bold cyan")
    table.add_column("Address", style="white")
    table.add_column("Name", style="bold yellow")
    table.add_column("Vendor (OUI)", style="white")
    for d in dedup[:50]:
        vendor = lookup_mac_vendor(d.get("address", "")) or "—"
        table.add_row(d.get("address", ""), d.get("name", "") or "—", vendor)
    console.print(table)


def battery_info(config: AppConfig) -> None:
    with task_status("[info]Fetching battery information…[/info]"):
        raw = adb_output(["shell", "dumpsys", "battery"])

    table = Table(title="Battery Information", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="bold yellow")
    table.add_column("Value", style="white")

    for line in raw.splitlines():
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            table.add_row(key.strip(), value.strip())

    console.print(table)


def _print_battery_mock_status() -> None:
    with task_status("[info]Reading battery state…[/info]"):
        raw = adb_output(["shell", "dumpsys", "battery"])
    keys = ("level", "status", "AC powered", "USB powered", "Wireless powered")
    table = Table(title="Battery Mock Status", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="bold yellow")
    table.add_column("Value", style="white")
    for line in raw.splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key in keys:
            table.add_row(key, value.strip())
    console.print(table)


def mock_battery_set(config: AppConfig) -> None:
    raw = ask("[bold cyan]Level[/bold cyan] [dim](0-100)[/dim]> ").strip()
    if not raw.isdigit() or not 0 <= int(raw) <= 100:
        print_error("Enter a number between 0 and 100.")
        return
    with task_status("[info]Setting battery level…[/info]"):
        r = adb(["shell", "dumpsys", "battery", "set", "level", raw])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or "Battery level set.")
        _print_battery_mock_status()
    else:
        print_error(out or "failed")


def mock_battery_unplug(config: AppConfig) -> None:
    with task_status("[info]Simulating unplugged…[/info]"):
        r = adb(["shell", "dumpsys", "battery", "unplug"])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or "Unplugged simulated.")
        _print_battery_mock_status()
    else:
        print_error(out or "failed")


def mock_battery_plug(config: AppConfig) -> None:
    with task_status("[info]Simulating plugged (charging)…[/info]"):
        adb(["shell", "dumpsys", "battery", "set", "ac", "1"])
        adb(["shell", "dumpsys", "battery", "set", "usb", "1"])
        r = adb(["shell", "dumpsys", "battery", "set", "status", "2"])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or "Plugged / charging simulated.")
        _print_battery_mock_status()
    else:
        print_error(out or "failed")


def mock_battery_reset(config: AppConfig) -> None:
    with task_status("[info]Resetting battery readings…[/info]"):
        r = adb(["shell", "dumpsys", "battery", "reset"])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or "Battery readings reset.")
        _print_battery_mock_status()
    else:
        print_error(out or "failed")


def mock_battery_status(config: AppConfig) -> None:
    _print_battery_mock_status()


def reboot(config: AppConfig, key: str) -> None:
    print_warning("Restarting will disconnect the device.")
    if not confirm("Continue?"):
        return

    if key == "system":
        with task_status("[info]Rebooting device…[/info]"):
            adb(["reboot"])
    else:
        show_options(
            config,
            "Advanced Reboot Options",
            ["Recovery", "Bootloader", "Fastboot"],
        )
        mode = ask("[prompt]> [/prompt]")
        cmd_map = {"1": "recovery", "2": "bootloader", "3": "fastboot"}
        if mode not in cmd_map:
            go_back_to_main_menu(config)
            return
        with task_status(f"[info]Rebooting to {cmd_map[mode]}…[/info]"):
            adb(["reboot", cmd_map[mode]])


def power_off(config: AppConfig) -> None:
    print_warning("Powering off will disconnect the device.")
    if not confirm("Continue?"):
        return
    with task_status("[info]Powering off…[/info]"):
        adb(["shell", "reboot", "-p"])


def unlock_device(config: AppConfig) -> None:
    password = ask(
        "[bold yellow]Password or Enter for blank[/bold yellow]> "
    )
    with task_status("[info]Sending unlock sequence…[/info]"):
        adb(["shell", "input", "keyevent", "26"])
        adb(["shell", "input", "swipe", "200", "900", "200", "300", "200"])
        if password:
            adb(["shell", "input", "text", password])
        adb(["shell", "input", "keyevent", "66"])
    print_success("Device unlocked.")


def lock_device(config: AppConfig) -> None:
    with task_status("[info]Locking…[/info]"):
        adb(["shell", "input", "keyevent", "26"])
    print_success("Device locked.")
