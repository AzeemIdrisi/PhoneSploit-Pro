"""Additional ADB toolkit features (menu 47–57)."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

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
)


def force_stop_app(config: AppConfig) -> None:
    submenu_row("Pick from list", "Enter package name")
    mode = console.input("[prompt]> [/prompt]")
    if mode == "1":
        pkg = select_package_from_list()
    elif mode == "2":
        pkg = console.input("[cyan]Package name[/cyan]> ").strip()
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
    mode = console.input("[prompt]> [/prompt]")
    if mode == "1":
        pkg = select_package_from_list()
    elif mode == "2":
        pkg = console.input("[cyan]Package name[/cyan]> ").strip()
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
    n = console.input("[cyan]Last N lines[/cyan] [dim](default 500)[/dim]> ").strip()
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
    mode = console.input("[prompt]> [/prompt]").strip()
    if mode not in ("1", "2"):
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return
    pkg = console.input("[cyan]Package name[/cyan]> ").strip()
    perm = console.input(
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
    filt = console.input(
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
    raw = console.input("[cyan]APK paths[/cyan]> ").strip()
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
    mode = console.input("[prompt]> [/prompt]").strip()
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
        key = console.input("[cyan]Key[/cyan] [dim](global namespace)[/dim]> ").strip()
        val = console.input("[cyan]Value[/cyan]> ").strip()
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
    mode = console.input("[prompt]> [/prompt]").strip()
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
