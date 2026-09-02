from __future__ import annotations

import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

from rich.panel import Panel
from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    print_success,
    print_error,
    print_info,
    confirm,
    task_status,
    submenu_row,
    ensure_config_dir,
    adb,
    adb_output,
    ask,
)


def _adb_command_error(out: str, returncode: int) -> bool:
    """True when adb/shell rejected the command — not when payload text contains keywords."""
    if returncode != 0:
        return True
    lowered = (out or "").lower()
    return any(
        marker in lowered
        for marker in (
            "unknown command",
            "securityexception",
            "permission denial",
            "not found",
            "inaccessible or not found",
            "java.lang.",
            "exception:",
            "usage: cmd clipboard",
        )
    )


def _adb_failed(out: str, returncode: int = 0) -> bool:
    lowered = (out or "").lower()
    return returncode != 0 or any(
        token in lowered
        for token in ("unknown command", "exception", "error", "not found", "invalid", "denied")
    )


def _timestamp() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}"


def _write_dump(dest: Path, result: subprocess.CompletedProcess[str]) -> None:
    """Persist adb output: stdout only on success; on failure, record stderr in a sibling file."""
    if result.returncode != 0:
        err_msg = result.stderr.strip() or "(no stderr from adb)"
        print_error(f"Dump failed: {err_msg}")
        err_dest = dest.with_suffix(".error.txt")
        detail = result.stderr.strip() or f"adb exited with code {result.returncode} (no stderr output)."
        try:
            err_dest.write_text(detail, encoding="utf-8")
        except OSError as e:
            print_error(f"Could not save error details to {err_dest}: {e}")
        return
    try:
        dest.write_text(result.stdout, encoding="utf-8")
    except OSError as e:
        print_error(f"Could not write dump file {dest}: {e}")
        return
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    print_success(f"Saved {len(lines)} records to: {dest}")


def dump_sms(config: AppConfig) -> None:
    if not confirm(
        "Export all SMS messages from the device to a file on this computer? "
        "This accesses private communications."
    ):
        return
    save_dir = ensure_config_dir(config, "pull_location")
    file_name = f"sms_dump-{_timestamp()}.txt"
    dest = Path(save_dir) / file_name

    with task_status("[info]Dumping SMS…[/info]"):
        result = adb(
            [
                "shell", "content", "query",
                "--uri", "content://sms/",
                "--projection", "address:date:body",
            ]
        )

    _write_dump(dest, result)


def dump_contacts(config: AppConfig) -> None:
    if not confirm(
        "Export all contacts from the device to a file on this computer? "
        "This accesses private contact data."
    ):
        return
    save_dir = ensure_config_dir(config, "pull_location")
    file_name = f"contacts_dump-{_timestamp()}.txt"
    dest = Path(save_dir) / file_name

    with task_status("[info]Dumping contacts…[/info]"):
        result = adb(
            [
                "shell", "content", "query",
                "--uri", "content://contacts/phones/",
                "--projection", "display_name:number",
            ]
        )

    _write_dump(dest, result)


def dump_call_logs(config: AppConfig) -> None:
    if not confirm(
        "Export all call logs from the device to a file on this computer? "
        "This accesses private call history."
    ):
        return
    save_dir = ensure_config_dir(config, "pull_location")
    file_name = f"call_logs_dump-{_timestamp()}.txt"
    dest = Path(save_dir) / file_name

    with task_status("[info]Dumping call logs…[/info]"):
        result = adb(
            [
                "shell", "content", "query",
                "--uri", "content://call_log/calls",
                "--projection", "name:number:duration:date",
            ]
        )

    _write_dump(dest, result)


# ---------------------------------------------------------------------------
# Clipboard, location, identifiers, usage stats (menu 64–67)
# ---------------------------------------------------------------------------

def _parcel_text(out: str) -> str | None:
    """Extract readable text from a `service call` parcel dump."""
    readable = ""
    for match in re.finditer(r"'([^']*)'", out):
        fragment = match.group(1).replace(".", "").replace(" ", "")
        if fragment:
            readable += fragment
    return readable or None


def _clipboard_get() -> tuple[str | None, str | None]:
    """Return (content, error_message). content None + error set = denied; ('', None) = empty."""
    with task_status("[info]Reading clipboard…[/info]"):
        r = adb(["shell", "cmd", "clipboard", "get"])
    out = (r.stdout + r.stderr).strip()
    if not _adb_command_error(out, r.returncode) and r.returncode == 0:
        return out, None

    legacy = adb(["shell", "service", "call", "clipboard", "1"])
    lout = (legacy.stdout + legacy.stderr).strip()
    if not _adb_command_error(lout, legacy.returncode):
        text = _parcel_text(lout)
        if text is not None:
            return text, None

    if any(x in out.lower() for x in ("securityexception", "permission", "denied")):
        return None, "Shell cannot read clipboard on this Android version."
    return None, out or lout or "Clipboard read failed."


def _clipboard_set(text: str) -> tuple[bool, str | None]:
    """Return (success, error_message)."""
    attempts: list[list[str]] = [
        ["shell", "cmd", "clipboard", "set", text],
        ["shell", "cmd", "clipboard", "set-text", text],
    ]
    last_err = ""
    for args in attempts:
        with task_status("[info]Setting clipboard…[/info]"):
            r = adb(args)
        out = (r.stdout + r.stderr).strip()
        if not _adb_command_error(out, r.returncode):
            return True, None
        last_err = out

    with task_status("[info]Trying legacy clipboard API…[/info]"):
        legacy = adb(
            ["shell", "service", "call", "clipboard", "2", "i32", "1", "i32", "1", "s16", text]
        )
    lout = (legacy.stdout + legacy.stderr).strip()
    if not _adb_command_error(lout, legacy.returncode):
        return True, None

    if any(x in (last_err + lout).lower() for x in ("securityexception", "permission", "denied")):
        return False, "Shell cannot set clipboard on this Android version."
    return False, last_err or lout or "Clipboard set failed."


def clipboard_read(config: AppConfig) -> None:
    content, err = _clipboard_get()
    if err:
        print_error(err)
    elif content:
        console.print(Panel(content, title="[bold cyan]Clipboard[/bold cyan]", border_style="bold cyan"))
    else:
        console.print(Panel("[dim]empty[/dim]", title="[bold cyan]Clipboard[/bold cyan]", border_style="bold cyan"))


def clipboard_set(config: AppConfig) -> None:
    text = ask("[bold cyan]Text to copy to clipboard[/bold cyan]> ")
    if not text:
        print_error("Null input")
        return
    ok, err = _clipboard_set(text)
    if ok:
        print_success("Clipboard updated.")
    else:
        print_error(err or "failed")


def clipboard_clear(config: AppConfig) -> None:
    if not confirm("Clear the clipboard?"):
        return
    ok, err = _clipboard_set("")
    if ok:
        print_success("Clipboard cleared.")
    else:
        print_error(err or "failed")


def get_location(config: AppConfig) -> None:
    with task_status("[info]Reading last known location…[/info]"):
        raw = adb_output(["shell", "dumpsys", "location"])

    rows: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    loc_re = re.compile(
        r"Location\[(\w+)\s+(-?\d+\.?\d*),(-?\d+\.?\d*)",
        re.IGNORECASE,
    )
    for match in loc_re.finditer(raw):
        provider, lat, lng = match.group(1), match.group(2), match.group(3)
        key = (provider, lat, lng)
        if key not in seen:
            seen.add(key)
            rows.append(key)

    for line in raw.splitlines():
        line = line.strip()
        if not any(k in line.lower() for k in ("latitude", "longitude", "lat=", "lng=")):
            continue
        lat_m = re.search(r"(?:latitude|lat)\s*[=:]\s*(-?\d+\.?\d*)", line, re.I)
        lng_m = re.search(r"(?:longitude|lng)\s*[=:]\s*(-?\d+\.?\d*)", line, re.I)
        if lat_m and lng_m:
            provider = line.split(":")[0].strip() if ":" in line else "location"
            key = (provider, lat_m.group(1), lng_m.group(1))
            if key not in seen:
                seen.add(key)
                rows.append(key)

    if not rows:
        print_error(
            "No last known location found. Open a map app (e.g. Google Maps) once so the "
            "device caches a location, then try again."
        )
        return

    table = Table(title="Last Known Location", show_header=True, header_style="bold cyan")
    table.add_column("Provider", style="bold yellow")
    table.add_column("Latitude", style="white")
    table.add_column("Longitude", style="white")
    for provider, lat, lng in rows[:25]:
        table.add_row(provider, lat, lng)
    console.print(table)


def _decoded_imei() -> str | None:
    attempts = [
        ["shell", "service", "call", "iphonesubinfo", "1", "s16", "com.android.shell"],
        ["shell", "service", "call", "iphonesubinfo", "1", "i64", "0"],
        ["shell", "service", "call", "iphonesubinfo", "1"],
    ]
    for args in attempts:
        r = adb(args)
        out = (r.stdout + r.stderr).strip()
        if _adb_failed(out, r.returncode):
            continue
        text = _parcel_text(out)
        if text:
            digits = re.sub(r"[^0-9]", "", text)
            if 14 <= len(digits) <= 17:
                return digits
    return None


def _imei_from_dumpsys(raw: str) -> str | None:
    for pattern in (
        r"Device ID\s*=\s*([0-9]{14,17})",
        r"IMEI\s*[=:]\s*([0-9]{14,17})",
        r"mImei\s*[=:]\s*([0-9]{14,17})",
    ):
        match = re.search(pattern, raw, re.I)
        if match:
            return match.group(1)
    return None


def get_identifiers(config: AppConfig) -> None:
    with task_status("[info]Gathering device identifiers…[/info]"):
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
        serial = adb_output(["shell", "getprop", "ro.serialno"]).strip()
        boot_serial = adb_output(["shell", "getprop", "ro.boot.serialno"]).strip()
        android_id = adb_output(["shell", "settings", "get", "secure", "android_id"]).strip()
        model = adb_output(["shell", "getprop", "ro.product.model"]).strip()

    imei_display = imei or "[yellow]Not accessible via ADB shell on this Android version[/yellow]"

    table = Table(title="Device Identifiers", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="bold yellow")
    table.add_column("Value", style="white")
    table.add_row("IMEI", imei_display)
    table.add_row("Serial", serial or "[dim]N/A[/dim]")
    table.add_row("Boot Serial", boot_serial or "[dim]N/A[/dim]")
    table.add_row("Android ID", android_id or "[dim]N/A[/dim]")
    table.add_row("Model", model or "[dim]N/A[/dim]")
    console.print(table)


def usage_stats(config: AppConfig) -> None:
    submenu_row("Last 1 day", "Last 7 days", "All time")
    window = ask("[prompt]> [/prompt]").strip().lower()
    days_map = {"1": 1, "2": 7, "3": None}
    if window not in days_map:
        print_error("Invalid selection")
        return
    days = days_map[window]
    cutoff_ms = 0 if days is None else int((time.time() - days * 86400) * 1000)

    with task_status("[info]Collecting app usage statistics…[/info]"):
        raw = adb_output(["shell", "dumpsys", "usagestats"])

    entries: list[tuple[str, int, int]] = []
    for line in raw.splitlines():
        line = line.strip()
        if "lastTimeUsed" not in line:
            continue
        pkg = line.split()[0] if line.split() else ""
        last_m = re.search(r"lastTimeUsed=(\d+)", line)
        if not last_m:
            continue
        last_used = int(last_m.group(1))
        if last_used < cutoff_ms:
            continue
        fg_m = re.search(r"totalTimeInForeground=(\d+)", line)
        vis_m = re.search(r"totalTimeVisible=(\d+)", line)
        visible = int(fg_m.group(1)) if fg_m else (int(vis_m.group(1)) if vis_m else 0)
        entries.append((pkg, last_used, visible))

    entries.sort(key=lambda e: e[1], reverse=True)
    if not entries:
        console.print(raw[:4000] or "[dim]No usage data available.[/dim]")
        return

    label = {1: "1 day", 2: "7 days", 3: "all time"}.get(int(window), "all time")
    table = Table(
        title=f"App Usage ({label}, most recent first)",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Package", style="bold yellow")
    table.add_column("Last Used", style="white")
    table.add_column("Foreground Time", style="white")
    now = time.time()
    for pkg, last_used, visible in entries[:40]:
        ago_min = max(0, int((now - last_used / 1000) / 60))
        table.add_row(
            pkg,
            f"{ago_min} min ago",
            f"{visible // 60000} min",
        )
    console.print(table)
    print_info(f"{min(len(entries), 40)} of {len(entries)} packages shown (first 40).")
