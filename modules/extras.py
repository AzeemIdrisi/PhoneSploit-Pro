"""Additional ADB toolkit features (menu 36–55)."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from rich.panel import Panel
from rich.table import Table

from modules.app_manager import select_package_from_list
from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_null_input,
    confirm,
    task_status,
    submenu_row,
    ensure_config_dir,
    adb,
    adb_output,
    get_adb_executable,
    ask,
)


def force_stop_app(config: AppConfig) -> None:
    submenu_row("Pick from list", "Enter package name")
    mode = ask("[prompt]> [/prompt]")
    if mode == "1":
        pkg = select_package_from_list()
    elif mode == "2":
        pkg = ask("[bold cyan]Package name[/bold cyan]> ").strip()
    else:
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return
    if not pkg:
        return
    if not confirm(f"Force-stop [bold yellow]{pkg}[/bold yellow]?"):
        return
    with task_status(f"[info]Force-stopping {pkg}…[/info]"):
        r = adb(["shell", "am", "force-stop", pkg])
    if r.returncode == 0:
        print_success(f"Force-stopped: {pkg}")
    else:
        print_error((r.stdout + r.stderr).strip() or "failed")


def clear_app_data(config: AppConfig) -> None:
    submenu_row("Pick from list", "Enter package name")
    mode = ask("[prompt]> [/prompt]")
    if mode == "1":
        pkg = select_package_from_list()
    elif mode == "2":
        pkg = ask("[bold cyan]Package name[/bold cyan]> ").strip()
    else:
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return
    if not pkg:
        return
    if not confirm(
        f"[bold red]Clear all data[/bold red] for [bold yellow]{pkg}[/bold yellow]? "
        "This cannot be undone."
    ):
        return
    with task_status(f"[info]Clearing {pkg}…[/info]"):
        r = adb(["shell", "pm", "clear", pkg])
    out = (r.stdout + r.stderr).strip()
    if "Success" in out or r.returncode == 0:
        print_success(out or "Cleared.")
    else:
        print_error(out or "failed")


def save_logcat_snippet(config: AppConfig) -> None:
    n = ask("[bold cyan]Last N lines[/bold cyan] [dim](default 500)[/dim]> ").strip()
    lines = int(n) if n.isdigit() else 500
    out_dir = ensure_config_dir(config, "pull_location")
    name = f"logcat-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    path = out_dir / name
    with task_status("[info]Capturing logcat…[/info]"):
        r = adb(["logcat", "-d", "-t", str(lines)])
    text = r.stdout + r.stderr
    try:
        path.write_text(text, encoding="utf-8", errors="replace")
    except OSError as e:
        print_error(str(e))
        return
    print_success(f"Saved: {path}")


def grant_revoke_permission(config: AppConfig) -> None:
    submenu_row("Grant", "Revoke")
    mode = ask("[prompt]> [/prompt]").strip()
    if mode not in ("1", "2"):
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return
    pkg = ask("[bold cyan]Package name[/bold cyan]> ").strip()
    perm = ask(
        "[bold cyan]Permission[/bold cyan] [dim](e.g. android.permission.CAMERA)[/dim]> "
    ).strip()
    if not pkg or not perm:
        print_null_input()
        return
    verb = "grant" if mode == "1" else "revoke"
    if not confirm(f"{verb.capitalize()} [bold cyan]{perm}[/bold cyan] for [bold yellow]{pkg}[/bold yellow]?"):
        return
    with task_status(f"[info]pm {verb}…[/info]"):
        r = adb(["shell", "pm", verb, pkg, perm])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or "Done.")
    else:
        print_error(out or "failed (Android 6+ / valid permission required)")


def restart_app(config: AppConfig) -> None:
    pkg = select_package_from_list()
    if not pkg:
        return
    if not confirm(f"Restart [bold yellow]{pkg}[/bold yellow]?"):
        return
    with task_status("[info]Stopping…[/info]"):
        adb(["shell", "am", "force-stop", pkg])
    with task_status("[info]Launching…[/info]"):
        r = adb(
            [
                "shell",
                "monkey",
                "-p",
                pkg,
                "-c",
                "android.intent.category.LAUNCHER",
                "1",
            ]
        )
    if r.returncode == 0:
        print_success(f"Restarted: {pkg}")
    else:
        print_error((r.stdout + r.stderr).strip() or "launch failed")


def live_logcat(config: AppConfig) -> None:
    filt = ask(
        "[bold cyan]Optional filter[/bold cyan] [dim](empty=all, *:W, or TAG:S)[/dim]> "
    ).strip()
    console.print("[bold dim]Streaming logcat (Ctrl+C to stop)…[/bold dim]")
    exe = get_adb_executable()
    if not exe:
        print_error("ADB not available.")
        return
    args = [exe, "logcat", "-v", "time"]
    if filt:
        args.append(filt)
    try:
        subprocess.run(args)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Stopped.[/bold yellow]")


def network_snapshot(config: AppConfig) -> None:
    with task_status("[info]Collecting network info…[/info]"):
        ip_addr = adb_output(["shell", "ip", "addr"])
        if "not found" in ip_addr.lower() or not ip_addr.strip():
            ip_addr = adb_output(["shell", "ifconfig"])
        route = adb_output(["shell", "ip", "route"])
        dns = adb_output(["shell", "getprop", "net.dns1"])
    console.print("[bold cyan]Interfaces / addresses[/bold cyan]")
    console.print(ip_addr[:8000] + ("…" if len(ip_addr) > 8000 else ""))
    console.print("\n[bold cyan]Routes[/bold cyan]")
    console.print(route or "[dim]N/A[/dim]")
    console.print(f"\n[bold cyan]net.dns1[/bold cyan] [bold white]{dns or 'N/A'}[/bold white]")


def install_split_apks(config: AppConfig) -> None:
    console.print(
        "[dim]Enter absolute paths to APK files, comma-separated on one line.[/dim]"
    )
    raw = ask("[bold cyan]APK paths[/bold cyan]> ").strip()
    if not raw:
        print_null_input()
        return
    paths = [Path(p.strip().strip("'\"")) for p in raw.split(",") if p.strip()]
    for p in paths:
        if not p.is_file():
            print_error(f"Not a file: {p}")
            return
    if not confirm(f"Install [bold cyan]{len(paths)}[/bold cyan] APK(s) as one session?"):
        return
    args = ["install-multiple", "-r"] + [str(p) for p in paths]
    with task_status("[info]install-multiple…[/info]"):
        r = adb(args)
    out = (r.stdout + r.stderr).strip()
    if "Success" in out:
        print_success(out)
    else:
        print_error(out or "failed")


def developer_settings(config: AppConfig) -> None:
    submenu_row("Open Developer Options", "Read global settings", "Write global setting")
    mode = ask("[prompt]> [/prompt]").strip()
    if mode == "1":
        with task_status("[info]Opening Developer Options…[/info]"):
            r = adb(
                [
                    "shell",
                    "am",
                    "start",
                    "-a",
                    "android.settings.APPLICATION_DEVELOPMENT_SETTINGS",
                ]
            )
        out = (r.stdout + r.stderr).strip()
        if r.returncode == 0:
            print_success(out or "Opened Developer Options on the device.")
        else:
            print_error(out or "failed to open Developer Options")
    elif mode == "2":
        keys = [
            "animator_duration_scale",
            "transition_animation_scale",
            "window_animation_scale",
            "adb_enabled",
        ]
        table = Table(title="settings get global", show_header=True, header_style="bold cyan")
        table.add_column("Key", style="bold yellow")
        table.add_column("Value", style="white")
        for k in keys:
            v = adb_output(["shell", "settings", "get", "global", k])
            table.add_row(k, v or "[dim]empty[/dim]")
        console.print(table)
    elif mode == "3":
        key = ask("[bold cyan]Key[/bold cyan] [dim](global namespace)[/dim]> ").strip()
        val = ask("[bold cyan]Value[/bold cyan]> ").strip()
        if not key:
            print_null_input()
            return
        if not confirm(f"settings put global [bold yellow]{key}[/bold yellow] = [bold cyan]{val}[/bold cyan]?"):
            return
        r = adb(["shell", "settings", "put", "global", key, val])
        if r.returncode == 0:
            print_success("Updated.")
        else:
            print_error((r.stdout + r.stderr).strip())
    else:
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")


def locale_read(config: AppConfig) -> None:
    with task_status("[info]Reading locale…[/info]"):
        rows = [
            ("settings system system_locales", adb_output(["shell", "settings", "get", "system", "system_locales"])),
            ("persist.sys.locale", adb_output(["shell", "getprop", "persist.sys.locale"])),
            ("ro.product.locale", adb_output(["shell", "getprop", "ro.product.locale"])),
        ]
    table = Table(title="Locale", show_header=True, header_style="bold cyan")
    table.add_column("Source", style="bold yellow")
    table.add_column("Value", style="white")
    for label, val in rows:
        table.add_row(label, val or "[dim]N/A[/dim]")
    console.print(table)


def screen_stay_on(config: AppConfig) -> None:
    submenu_row("Stay on USB", "Stay on (all)", "Turn off stay-on")
    mode = ask("[prompt]> [/prompt]").strip()
    if mode == "1":
        target = "usb"
    elif mode == "2":
        target = "true"
    elif mode == "3":
        target = "false"
    else:
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return
    if not confirm(f"Set [bold cyan]svc power stayon {target}[/bold cyan]?"):
        return
    r = adb(["shell", "svc", "power", "stayon", target])
    if r.returncode == 0:
        print_success("Done. Use option 3 to turn off when finished.")
    else:
        print_error((r.stdout + r.stderr).strip())


# ---------------------------------------------------------------------------
# Radio toggles, sound & display, notifications (menu 68, 70, 71)
# ---------------------------------------------------------------------------

def _adb_command_failed(r: subprocess.CompletedProcess[str]) -> bool:
    out = (r.stdout + r.stderr).strip()
    lowered = out.lower()
    if r.returncode != 0:
        return True
    return any(
        t in lowered
        for t in (
            "unknown command",
            "securityexception",
            "permission denial",
            "not found",
            "inaccessible or not found",
            "not allowed",
            "exception:",
            "usage: cmd",
        )
    )


def _run_shell(args: list[str], label: str, *, confirm_msg: str | None = None) -> bool:
    if confirm_msg and not confirm(confirm_msg):
        return False
    with task_status(f"[info]{label}…[/info]"):
        r = adb(args)
    out = (r.stdout + r.stderr).strip()
    if _adb_command_failed(r):
        print_error(out or "command failed")
        return False
    print_success(out or "Done.")
    return True


def _toggle_radio(subcommand: str, on: bool) -> bool:
    verb = "enable" if on else "disable"
    label = f"{subcommand.replace('_', ' ').title()} {'on' if on else 'off'}"
    with task_status(f"[info]Toggling {label}…[/info]"):
        if subcommand == "airplane":
            state = "1" if on else "0"
            flag = "true" if on else "false"
            r1 = adb(["shell", "settings", "put", "global", "airplane_mode_on", state])
            r2 = adb(
                [
                    "shell",
                    "am",
                    "broadcast",
                    "-a",
                    "android.intent.action.AIRPLANE_MODE",
                    "--ez",
                    "state",
                    flag,
                ]
            )
            if _adb_command_failed(r1) and _adb_command_failed(r2):
                print_error(
                    (r1.stdout + r1.stderr + r2.stdout + r2.stderr).strip()
                    or "airplane toggle failed"
                )
                return False
            return True
        if subcommand == "data":
            r = adb(["shell", "svc", "data", verb])
            if not _adb_command_failed(r):
                return True
            print_error((r.stdout + r.stderr).strip() or "mobile data toggle failed")
            return False
        if subcommand == "bluetooth":
            r = adb(["shell", "svc", "bluetooth", verb])
            if not _adb_command_failed(r):
                return True
            r2 = adb(["shell", "cmd", "bluetooth_manager", verb])
            if not _adb_command_failed(r2):
                return True
            print_error(
                "Bluetooth toggle blocked by the shell user on this Android version. "
                "Toggle manually from quick settings."
            )
            return False
        if subcommand == "nfc":
            r = adb(["shell", "svc", "nfc", verb])
            if _adb_command_failed(r):
                print_error((r.stdout + r.stderr).strip() or "NFC toggle failed")
                return False
            return True
    return False


def _radio_on_off(config: AppConfig, label: str, subcommand: str) -> None:
    submenu_row("On", "Off")
    state = ask("[prompt]> [/prompt]").strip().lower()
    if state == "0":
        return
    if state not in ("1", "2"):
        print_error("Invalid selection")
        return
    if _toggle_radio(subcommand, state == "1"):
        print_success(f"{label} {'enabled' if state == '1' else 'disabled'}.")


def radio_data(config: AppConfig) -> None:
    _radio_on_off(config, "Mobile Data", "data")


def radio_bluetooth(config: AppConfig) -> None:
    _radio_on_off(config, "Bluetooth", "bluetooth")


def radio_nfc(config: AppConfig) -> None:
    _radio_on_off(config, "NFC", "nfc")


def radio_airplane(config: AppConfig) -> None:
    _radio_on_off(config, "Airplane Mode", "airplane")


def _media_volume_show() -> None:
    with task_status("[info]Reading media volume…[/info]"):
        for args in (
            ["shell", "cmd", "media", "volume", "--show", "--stream", "3"],
            ["shell", "cmd", "media", "volume", "--get", "--stream", "3"],
        ):
            r = adb(args)
            out = (r.stdout + r.stderr).strip()
            if not _adb_command_failed(r) and out:
                console.print(Panel(out, title="[bold cyan]Media Volume (stream 3)[/bold cyan]", border_style="bold cyan"))
                return
    print_error("Volume query not supported (cmd media unavailable on this ROM).")


def _media_volume_set(level: str) -> None:
    attempts = [
        ["shell", "cmd", "media", "volume", "--stream", "3", "--set", level],
        ["shell", "cmd", "media_session", "volume", "--stream", "3", "--set", level],
    ]
    for args in attempts:
        with task_status("[info]Setting media volume…[/info]"):
            r = adb(args)
        out = (r.stdout + r.stderr).strip()
        if not _adb_command_failed(r):
            print_success(out or f"Media volume set to {level}.")
            return
    print_error(
        "Volume control not supported (cmd media / media_session unavailable on this ROM)."
    )


def _set_brightness() -> None:
    raw = ask("[bold cyan]Brightness[/bold cyan] [dim](0-255, empty = auto)[/dim]> ").strip()
    if not raw:
        _run_shell(
            ["shell", "settings", "put", "system", "screen_brightness_mode", "1"],
            "Enabling auto brightness",
        )
        return
    if not raw.isdigit() or not 0 <= int(raw) <= 255:
        print_error("Enter a number between 0 and 255.")
        return
    with task_status("[info]Disabling auto brightness…[/info]"):
        adb(["shell", "settings", "put", "system", "screen_brightness_mode", "0"])
    _run_shell(["shell", "settings", "put", "system", "screen_brightness", raw], "Setting brightness")


def _set_timeout() -> None:
    seconds = ask("[bold cyan]Screen timeout[/bold cyan] [dim](seconds)[/dim]> ").strip()
    if not seconds.isdigit():
        print_error("Enter a number in seconds.")
        return
    _run_shell(
        ["shell", "settings", "put", "system", "screen_off_timeout", str(int(seconds) * 1000)],
        "Setting screen timeout",
    )


def _set_dnd(config: AppConfig) -> None:
    submenu_row("Off", "Alarms Only", "Priority Only", "Total Silence")
    choice = ask("[prompt]> [/prompt]").strip()
    modes = {"1": "0", "2": "1", "3": "2", "4": "3"}
    mode = modes.get(choice)
    if not choice or choice == "0":
        return
    if mode is None:
        print_error("Invalid selection")
        return
    _run_shell(["shell", "settings", "put", "secure", "zen_mode", mode], "Setting Do Not Disturb mode")


def _run_statusbar(args: list[str], label: str) -> None:
    with task_status(f"[info]{label}…[/info]"):
        r = adb(["shell", "cmd", "statusbar", *args])
    out = (r.stdout + r.stderr).strip()
    if _adb_command_failed(r):
        print_error(out or "not supported on this Android version")
    else:
        print_success(out or "Done.")


def notif_post(config: AppConfig) -> None:
    title = ask("[bold cyan]Title[/bold cyan]> ").strip()
    message = ask("[bold cyan]Message[/bold cyan]> ").strip()
    tag = f"phonesploit-{datetime.now().strftime('%H%M%S')}"
    if not title and not message:
        print_error("Null input")
        return
    with task_status("[info]Posting notification…[/info]"):
        r = adb(
            [
                "shell",
                "cmd",
                "notification",
                "post",
                "-S",
                "bigtext",
                "-t",
                title,
                tag,
                message,
            ]
        )
    out = (r.stdout + r.stderr).strip()
    if _adb_command_failed(r) or "permission" in out.lower():
        print_error(
            "Posting failed (shell user denied on most devices). "
            "Status bar expand/collapse may still work."
        )
    else:
        print_success(out or "Notification posted.")


def notif_expand(config: AppConfig) -> None:
    _run_statusbar(["expand-notifications"], "Expanding notifications panel")


def notif_expand_qs(config: AppConfig) -> None:
    _run_statusbar(["expand-settings"], "Expanding quick settings")


def notif_collapse(config: AppConfig) -> None:
    _run_statusbar(["collapse"], "Collapsing panel")


def sound_volume_show(config: AppConfig) -> None:
    _media_volume_show()


def sound_volume_set(config: AppConfig) -> None:
    raw = ask("[bold cyan]Media volume[/bold cyan] [dim](0-15)[/dim]> ").strip()
    if not raw.isdigit() or not 0 <= int(raw) <= 15:
        print_error("Enter a number between 0 and 15.")
        return
    _media_volume_set(raw)


def sound_brightness(config: AppConfig) -> None:
    _set_brightness()


def sound_timeout(config: AppConfig) -> None:
    _set_timeout()


def sound_dnd(config: AppConfig) -> None:
    _set_dnd(config)
