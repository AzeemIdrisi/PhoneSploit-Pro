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
    print_submenu,
    parse_submenu_choice,
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
        pkg = ask("[cyan]Package name[/cyan]> ").strip()
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return
    if not pkg:
        return
    if not confirm(f"Force-stop [yellow]{pkg}[/yellow]?"):
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
        pkg = ask("[cyan]Package name[/cyan]> ").strip()
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return
    if not pkg:
        return
    if not confirm(
        f"[bold red]Clear all data[/bold red] for [yellow]{pkg}[/yellow]? "
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
    n = ask("[cyan]Last N lines[/cyan] [dim](default 500)[/dim]> ").strip()
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
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return
    pkg = ask("[cyan]Package name[/cyan]> ").strip()
    perm = ask(
        "[cyan]Permission[/cyan] [dim](e.g. android.permission.CAMERA)[/dim]> "
    ).strip()
    if not pkg or not perm:
        print_null_input()
        return
    verb = "grant" if mode == "1" else "revoke"
    if not confirm(f"{verb.capitalize()} [cyan]{perm}[/cyan] for [yellow]{pkg}[/yellow]?"):
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
    if not confirm(f"Restart [yellow]{pkg}[/yellow]?"):
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
        "[cyan]Optional filter[/cyan] [dim](empty=all, *:W, or TAG:S)[/dim]> "
    ).strip()
    console.print("[dim]Streaming logcat (Ctrl+C to stop)…[/dim]")
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
        console.print("\n[yellow]Stopped.[/yellow]")


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
    console.print(f"\n[bold cyan]net.dns1[/bold cyan] [white]{dns or 'N/A'}[/white]")


def install_split_apks(config: AppConfig) -> None:
    console.print(
        "[dim]Enter absolute paths to APK files, comma-separated on one line.[/dim]"
    )
    raw = ask("[cyan]APK paths[/cyan]> ").strip()
    if not raw:
        print_null_input()
        return
    paths = [Path(p.strip().strip("'\"")) for p in raw.split(",") if p.strip()]
    for p in paths:
        if not p.is_file():
            print_error(f"Not a file: {p}")
            return
    if not confirm(f"Install [cyan]{len(paths)}[/cyan] APK(s) as one session?"):
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
    submenu_row("Read global settings", "Write global setting")
    mode = ask("[prompt]> [/prompt]").strip()
    if mode == "1":
        keys = [
            "animator_duration_scale",
            "transition_animation_scale",
            "window_animation_scale",
            "adb_enabled",
        ]
        table = Table(title="settings get global", show_header=True, header_style="bold cyan")
        table.add_column("Key", style="yellow")
        table.add_column("Value", style="white")
        for k in keys:
            v = adb_output(["shell", "settings", "get", "global", k])
            table.add_row(k, v or "[dim]empty[/dim]")
        console.print(table)
    elif mode == "2":
        key = ask("[cyan]Key[/cyan] [dim](global namespace)[/dim]> ").strip()
        val = ask("[cyan]Value[/cyan]> ").strip()
        if not key:
            print_null_input()
            return
        if not confirm(f"settings put global [yellow]{key}[/yellow] = [cyan]{val}[/cyan]?"):
            return
        r = adb(["shell", "settings", "put", "global", key, val])
        if r.returncode == 0:
            print_success("Updated.")
        else:
            print_error((r.stdout + r.stderr).strip())
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")


def locale_read(config: AppConfig) -> None:
    with task_status("[info]Reading locale…[/info]"):
        rows = [
            ("settings system system_locales", adb_output(["shell", "settings", "get", "system", "system_locales"])),
            ("persist.sys.locale", adb_output(["shell", "getprop", "persist.sys.locale"])),
            ("ro.product.locale", adb_output(["shell", "getprop", "ro.product.locale"])),
        ]
    table = Table(title="Locale", show_header=True, header_style="bold cyan")
    table.add_column("Source", style="yellow")
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
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return
    if not confirm(f"Set [cyan]svc power stayon {target}[/cyan]?"):
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


def radio_toggles(config: AppConfig) -> None:
    items = ["Mobile Data", "Bluetooth", "NFC", "Airplane Mode"]
    radios = {"1": "data", "2": "bluetooth", "3": "nfc", "4": "airplane"}

    def _render() -> None:
        print_submenu("Radio Toggles", items)

    _render()
    while True:
        radio = ask("[red]\\[Radio Toggles][/red] > ").strip().lower()
        action = parse_submenu_choice(radio, config, _render)
        if action == "exit":
            return
        if action == "redraw":
            continue
        sub = radios.get(radio)
        if not sub:
            print_error("Invalid selection")
            continue
        while True:
            console.print(
                f"\n[bold cyan]{sub.replace('_', ' ').title()}[/bold cyan]\n"
                "  [dim]1.[/dim] On\n"
                "  [dim]2.[/dim] Off\n"
                "  [dim]0.[/dim] Back\n"
            )
            state = ask("[prompt]> [/prompt]").strip().lower()
            if state == "0":
                break
            if state == "1":
                if _toggle_radio(sub, True):
                    print_success(f"{sub.replace('_', ' ').title()} enabled.")
            elif state == "2":
                if _toggle_radio(sub, False):
                    print_success(f"{sub.replace('_', ' ').title()} disabled.")
            else:
                print_error("Invalid selection")


def _media_volume_show() -> None:
    with task_status("[info]Reading media volume…[/info]"):
        for args in (
            ["shell", "cmd", "media", "volume", "--show", "--stream", "3"],
            ["shell", "cmd", "media", "volume", "--get", "--stream", "3"],
        ):
            r = adb(args)
            out = (r.stdout + r.stderr).strip()
            if not _adb_command_failed(r) and out:
                console.print(Panel(out, title="Media Volume (stream 3)", border_style="cyan"))
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


def _media_volume_menu() -> None:
    vol_items = ["Show volume levels", "Set media volume"]
    while True:
        print_submenu("Media Volume", vol_items)
        mode = ask("[red]\\[Media Volume][/red] > ").strip().lower()
        if mode == "0":
            return
        if mode == "1":
            _media_volume_show()
        elif mode == "2":
            raw = ask("[cyan]Media volume[/cyan] [dim](0-15)[/dim]> ").strip()
            if not raw.isdigit() or not 0 <= int(raw) <= 15:
                print_error("Enter a number between 0 and 15.")
                continue
            _media_volume_set(raw)
        else:
            print_error("Invalid selection")


def _set_brightness() -> None:
    raw = ask("[cyan]Brightness[/cyan] [dim](0-255, empty = auto)[/dim]> ").strip()
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
    seconds = ask("[cyan]Screen timeout[/cyan] [dim](seconds)[/dim]> ").strip()
    if not seconds.isdigit():
        print_error("Enter a number in seconds.")
        return
    _run_shell(
        ["shell", "settings", "put", "system", "screen_off_timeout", str(int(seconds) * 1000)],
        "Setting screen timeout",
    )


def _set_dnd() -> None:
    dnd_items = ["Off", "Alarms Only", "Priority Only", "Total Silence"]
    print_submenu("Do Not Disturb", dnd_items)
    choice = ask("[red]\\[DND][/red] > ").strip()
    modes = {"1": "0", "2": "1", "3": "2", "4": "3"}
    mode = modes.get(choice)
    if choice == "0":
        return
    if mode is None:
        print_error("Invalid selection")
        return
    _run_shell(["shell", "settings", "put", "secure", "zen_mode", mode], "Setting Do Not Disturb mode")


def sound_display(config: AppConfig) -> None:
    items = [
        "Set Media Volume",
        "Set Screen Brightness",
        "Set Screen Timeout",
        "Do Not Disturb Mode",
    ]

    def _render() -> None:
        print_submenu("Sound & Display", items)

    _render()
    while True:
        choice = ask("[red]\\[Sound & Display][/red] > ").strip().lower()
        action = parse_submenu_choice(choice, config, _render)
        if action == "exit":
            return
        if action == "redraw":
            continue
        if choice == "1":
            _media_volume_menu()
        elif choice == "2":
            _set_brightness()
        elif choice == "3":
            _set_timeout()
        elif choice == "4":
            _set_dnd()
        else:
            print_error("Invalid selection")


def _run_statusbar(args: list[str], label: str) -> None:
    with task_status(f"[info]{label}…[/info]"):
        r = adb(["shell", "cmd", "statusbar", *args])
    out = (r.stdout + r.stderr).strip()
    if _adb_command_failed(r):
        print_error(out or "not supported on this Android version")
    else:
        print_success(out or "Done.")


def notifications_menu(config: AppConfig) -> None:
    items = [
        "Post a Notification",
        "Expand Notifications Panel",
        "Expand Quick Settings",
        "Collapse Panel",
    ]

    def _render() -> None:
        print_submenu("Notifications", items)

    _render()
    while True:
        choice = ask("[red]\\[Notifications][/red] > ").strip().lower()
        action = parse_submenu_choice(choice, config, _render)
        if action == "exit":
            return
        if action == "redraw":
            continue
        if choice == "1":
            title = ask("[cyan]Title[/cyan]> ").strip()
            message = ask("[cyan]Message[/cyan]> ").strip()
            tag = f"phonesploit-{datetime.now().strftime('%H%M%S')}"
            if not title and not message:
                print_error("Null input")
                continue
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
        elif choice == "2":
            _run_statusbar(["expand-notifications"], "Expanding notifications panel")
        elif choice == "3":
            _run_statusbar(["expand-settings"], "Expanding quick settings")
        elif choice == "4":
            _run_statusbar(["collapse"], "Collapsing panel")
        else:
            print_error("Invalid selection")
