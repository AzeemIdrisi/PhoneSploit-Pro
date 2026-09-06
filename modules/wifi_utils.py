"""WiFi-related ADB helpers (menu 57–61)."""

import re
from collections import OrderedDict

from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    confirm,
    task_status,
    show_options,
    go_back_to_main_menu,
    adb,
    adb_output,
    ensure_config_dir,
    ask,
)

# --- Saved-network parsing (formats vary by Android / OEM) ---

_CMD_WIFI_LINE_RES = (
    # Standard: Network Id 0  SSID "MyWifi"
    re.compile(r"Network\s+Id\s+\d+\s+SSID\s+\"([^\"]+)\"", re.I),
    # Variant spacing / casing
    re.compile(r"network[Ii]d\s*[:=]\s*\d+.*SSID\s*[:=]\s*\"([^\"]+)\"", re.I),
    re.compile(r"SSID\s*[:=]\s*\"([^\"]+)\"", re.I),
    # Unquoted SSID on list-networks (some builds; avoid MAC-like tokens)
    re.compile(r"SSID\s*[:=]\s*([A-Za-z0-9_\-_.]+)\s*(?:$|,|;)", re.I),
)

_DUMPSYS_RES = (
    re.compile(r'Network\s+Id\s+\d+\s+SSID\s+"([^"]+)"', re.I),
    re.compile(r'WifiConfiguration\{[^}]*?SSID\s*=\s*"([^"]+)"', re.I),
    re.compile(r'(?:^|\s)SSID:\s*"([^"]+)"', re.M),
    re.compile(r'mWifiSSID\s*=\s*"([^"]+)"', re.I),
    re.compile(r'"(?:WPA_PSK|WPA_EAP|SAE|WEP|PSK|OPEN|OWE)-([^"]+)"', re.I),
)

_CONFIG_KEY_RES = re.compile(r'ConfigKey\s*=\s*"([^"]+)"', re.I)

# Lines that look like scan / junk (not saved-profile names)
_JUNK_SSID = frozenset(
    {
        "null",
        "unknown",
        "any",
        "<unknown ssid>",
        "0x",
        "wifi",
        "wlan",
    }
)


def _is_plausible_saved_ssid(s: str) -> bool:
    s = s.strip()
    if len(s) < 1 or len(s) > 128:
        return False
    low = s.lower()
    if low in _JUNK_SSID:
        return False
    # MAC-like
    if re.match(r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$", s):
        return False
    return True


def _ordered_unique(items: list[str]) -> list[str]:
    out: "OrderedDict[str, None]" = OrderedDict()
    for x in items:
        x = x.strip()
        if x and _is_plausible_saved_ssid(x):
            out[x] = None
    return list(out.keys())


def _parse_cmd_wifi_list_networks(raw: str) -> list[str]:
    found: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for rx in _CMD_WIFI_LINE_RES:
            m = rx.search(line)
            if m:
                found.append(m.group(1))
                break
    return _ordered_unique(found)


def _ssid_from_config_key(ck: str) -> str | None:
    """Derive SSID from ConfigKey like WPA_PSK-MyNet-none or SAE-\"quoted\"."""
    ck = ck.strip()
    if not ck:
        return None
    for prefix in ("WPA_PSK-", "WPA_EAP-", "SAE-", "WEP-", "PSK-", "OPEN-", "OWE-"):
        if ck.startswith(prefix):
            rest = ck[len(prefix) :]
            rest = rest.strip('"')
            if rest.lower() in ("none", "null", "any"):
                return None
            # Some keys: WPA_PSK-MySSID-None (third field)
            parts = rest.rsplit("-", 1)
            if len(parts) == 2 and parts[1].lower() in ("none", "null"):
                rest = parts[0]
            return rest or None
    return None


def _parse_dumpsys_wifi(raw: str) -> list[str]:
    found: list[str] = []

    for rx in _DUMPSYS_RES:
        for m in rx.finditer(raw):
            g = m.group(1).strip()
            if g:
                found.append(g)

    for line in raw.splitlines():
        if "ConfigKey" not in line:
            continue
        m = _CONFIG_KEY_RES.search(line)
        if not m:
            continue
        ck = m.group(1)
        derived = _ssid_from_config_key(ck)
        if derived:
            found.append(derived)
        else:
            # Quoted SSID inside key only
            inner = re.search(r'"([^"]{1,64})"', ck)
            if inner and _is_plausible_saved_ssid(inner.group(1)):
                found.append(inner.group(1))

    # WifiConfiguration multiline blocks (SSID on next lines)
    in_block = False
    for line in raw.splitlines():
        ls = line.strip()
        if "WifiConfiguration" in ls or "WifiNetworkConfig" in ls:
            in_block = True
            continue
        if in_block and ls.startswith("SSID:"):
            m = re.search(r'SSID:\s*"([^"]+)"', ls) or re.search(r"SSID:\s*(\S+)", ls)
            if m:
                found.append(m.group(1))
            in_block = False

    return _ordered_unique(found)


def _merged_shell(args: list[str]) -> str:
    r = adb(args)
    return (r.stdout + r.stderr).strip()


def _collect_saved_ssids() -> tuple[list[str], str]:
    """
    Returns (ssids, debug_note). Tries cmd wifi, then dumpsys wifi, then grep helper.
    """
    notes: list[str] = []

    cmd_out = _merged_shell(["shell", "cmd", "wifi", "list-networks"])
    if cmd_out.strip():
        if "Unknown command" in cmd_out or "Invalid argument" in cmd_out:
            notes.append("cmd wifi list-networks: not supported")
        else:
            ssids = _parse_cmd_wifi_list_networks(cmd_out)
            if ssids:
                return ssids, ""

    # Alternative invocation (some devices)
    alt = _merged_shell(["shell", "cmd", "-w", "wifi", "list-networks"])
    if alt.strip() and "Unknown" not in alt[:120]:
        ssids = _parse_cmd_wifi_list_networks(alt)
        if ssids:
            return ssids, ""

    raw = _merged_shell(["shell", "dumpsys", "wifi"])
    ssids = _parse_dumpsys_wifi(raw)
    if ssids:
        return ssids, ""

    # Narrow grep on device — lines mentioning ConfigKey / WifiConfiguration / saved
    grep_out = _merged_shell(
        [
            "shell",
            "sh",
            "-c",
            "dumpsys wifi 2>/dev/null | grep -iE "
            "'ConfigKey|WifiConfiguration|Network Id|SSID' | head -200",
        ]
    )
    if grep_out.strip():
        ssids = _parse_dumpsys_wifi(grep_out)
        if ssids:
            return ssids, "(from filtered dumpsys lines)"

    notes.append("no SSID patterns matched")
    return [], " ".join(notes) if notes else ""


def wifi_status_dump(config: AppConfig) -> None:
    show_options(
        config,
        "Wi-Fi Status Dump",
        ["Summary lines", "Save full dumpsys wifi to file"],
    )
    mode = ask("[prompt]> [/prompt]").strip()
    with task_status("[info]Reading WiFi service…[/info]"):
        raw = adb_output(["shell", "dumpsys", "wifi"])
    if mode not in ("", "1", "2"):
        go_back_to_main_menu(config)
        return
    if mode == "2":
        out_dir = ensure_config_dir(config, "pull_location")
        path = out_dir / "dumpsys-wifi.txt"
        try:
            path.write_text(raw, encoding="utf-8", errors="replace")
        except OSError as e:
            print_error(str(e))
            return
        print_success(f"Saved: {path}")
        return
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
                "mWifiInfo",
                "link speed",
            )
        ):
            lines.append(s)
    if not lines:
        lines = raw.splitlines()[:80]
    console.print("[bold cyan]WiFi (filtered)[/bold cyan]")
    for ln in lines[:120]:
        console.print(f"  {ln}")


def wlan_ip(config: AppConfig) -> None:
    with task_status("[info]Reading wlan0…[/info]"):
        out = adb_output(["shell", "ip", "addr", "show", "wlan0"])
    if "does not exist" in out.lower() or not out.strip():
        out = adb_output(["shell", "ip", "addr"])
    console.print(out or "[dim]No output[/dim]")


def wifi_toggle(config: AppConfig) -> None:
    if not confirm("[bold yellow]Toggle WiFi radio via svc wifi?[/bold yellow]"):
        return
    mode = ask("[bold cyan]Type[/bold cyan] [dim]enable[/dim] or [dim]disable[/dim]> ").strip().lower()
    if mode not in ("enable", "disable"):
        print_error("Enter enable or disable.")
        return
    r = adb(["shell", "svc", "wifi", mode])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or f"WiFi {mode}d.")
    else:
        print_error(out or "failed")


def ping_connectivity(config: AppConfig) -> None:
    host = ask("[bold cyan]Host to ping[/bold cyan] [dim](default 8.8.8.8)[/dim]> ").strip() or "8.8.8.8"
    with task_status(f"[info]ping {host}…[/info]"):
        r = adb(["shell", "ping", "-c", "4", host])
    console.print((r.stdout + r.stderr).strip())


def saved_wifi_networks(config: AppConfig) -> None:
    """
    List saved Wi-Fi profiles without root: cmd wifi, dumpsys parsing, filtered grep.
    """
    with task_status("[info]Listing saved Wi-Fi networks…[/info]"):
        ssids, note = _collect_saved_ssids()

    if not ssids:
        print_error(
            "Could not detect saved networks from this device. "
            "Use [bold cyan]58[/bold cyan] and save full [bold]dumpsys wifi[/bold] to inspect OEM format, "
            "or ensure at least one Wi-Fi network is saved."
        )
        return

    table = Table(
        title="Saved Wi-Fi networks (SSID only — no passwords)"
        + (f" {note}" if note else ""),
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="bold green", justify="right")
    table.add_column("SSID", style="bold white")
    for i, s in enumerate(ssids, 1):
        table.add_row(str(i), s)
    console.print(table)
    print_success(f"{len(ssids)} network(s) listed.")
    console.print(
        "[dim]If the list includes nearby scan SSIDs, ignore those; "
        "saved-profile detection varies by ROM.[/dim]"
    )


def _parse_scan_results(raw: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if "=" not in line or "BSSID" not in line:
            continue
        entry: dict[str, str] = {}
        for token in line.split("|"):
            token = token.strip()
            if "=" not in token:
                continue
            key, _, value = token.partition("=")
            entry[key.strip().lower()] = value.strip().strip('"')
        if entry.get("bssid") or entry.get("ssid"):
            entry.setdefault("ssid", "")
            rows.append(entry)
    return rows


def nearby_wifi_scan(config: AppConfig) -> None:
    with task_status("[info]Triggering Wi-Fi scan…[/info]"):
        scan = adb(["shell", "cmd", "wifi", "start-scan"])
    scan_out = (scan.stdout + scan.stderr).strip()
    if scan.returncode != 0 or any(
        t in scan_out.lower() for t in ("unknown command", "exception", "denied")
    ):
        print_error(scan_out or "Wi-Fi scanning not supported on this device/ROM.")
        return
    console.print("[bold dim]Waiting for scan to complete…[/bold dim]")
    with task_status("[info]Reading scan results…[/info]"):
        raw = adb_output(["shell", "cmd", "wifi", "list-scan-results"])
    rows = _parse_scan_results(raw)
    if not rows:
        console.print(raw[:3000] or "[bold yellow]No scan results returned. Enable Wi-Fi and retry.[/bold yellow]")
        return
    table = Table(title="Nearby Wi-Fi Networks", show_header=True, header_style="bold cyan")
    table.add_column("SSID", style="bold yellow")
    table.add_column("BSSID", style="white")
    table.add_column("Freq (MHz)", style="white", justify="right")
    table.add_column("Signal (dBm)", style="white", justify="right")
    table.add_column("Capabilities", style="dim white")
    for entry in rows:
        table.add_row(
            entry.get("ssid") or "[dim]Hidden[/dim]",
            entry.get("bssid") or "—",
            entry.get("frequency") or "—",
            entry.get("signal") or entry.get("signal strength") or "—",
            entry.get("capabilities") or "—",
        )
    console.print(table)
    print_success(f"{len(rows)} network(s) found.")


def hotspot_start(config: AppConfig) -> None:
    if not confirm("Start a local-only hotspot on the device?"):
        return
    with task_status("[info]Starting local hotspot…[/info]"):
        r = adb(["shell", "cmd", "wifi", "start-local-only-hotspot"])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0 and not any(
        t in out.lower()
        for t in ("error", "exception", "unknown command", "denied", "permission")
    ):
        print_success(out or "Local hotspot started.")
        if out:
            console.print(f"[dim]{out}[/dim]")
    else:
        print_error(
            out
            or "Local hotspot is not available (may need location permission or a supported ROM)."
        )


def hotspot_stop(config: AppConfig) -> None:
    with task_status("[info]Stopping local hotspot…[/info]"):
        r = adb(["shell", "cmd", "wifi", "stop-local-only-hotspot"])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or "Local hotspot stopped.")
    else:
        print_error(out or "failed to stop hotspot")
