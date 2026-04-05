"""Host-side adb forward / reverse (uses local adb binary, not adb shell)."""

import subprocess

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_null_input,
    get_adb_executable,
    submenu_row,
)


def _run_host(args: list[str]) -> subprocess.CompletedProcess:
    exe = get_adb_executable()
    if not exe:
        return subprocess.CompletedProcess(args=[], returncode=127, stdout="", stderr="no adb")
    return subprocess.run([exe] + args, capture_output=True, text=True)


def port_forward_menu(config: AppConfig) -> None:
    submenu_row(
        "Forward (PC port → device port)",
        "Reverse (device port → PC port)",
        "List rules",
        "Remove one rule",
        "Remove all rules",
    )
    choice = console.input("[prompt]> [/prompt]").strip()

    if choice == "1":
        local = console.input("[cyan]Local (PC) TCP port[/cyan]> ").strip()
        remote = console.input("[cyan]Remote (device) TCP port[/cyan]> ").strip()
        if not local.isdigit() or not remote.isdigit():
            print_null_input()
            return
        r = _run_host(["forward", f"tcp:{local}", f"tcp:{remote}"])
        out = (r.stdout + r.stderr).strip()
        if r.returncode == 0:
            print_success(out or f"Forwarded tcp:{local} → device tcp:{remote}")
        else:
            print_error(out or "forward failed")

    elif choice == "2":
        remote = console.input("[cyan]Device TCP port[/cyan]> ").strip()
        local = console.input("[cyan]Host TCP port[/cyan]> ").strip()
        if not remote.isdigit() or not local.isdigit():
            print_null_input()
            return
        r = _run_host(["reverse", f"tcp:{remote}", f"tcp:{local}"])
        out = (r.stdout + r.stderr).strip()
        if r.returncode == 0:
            print_success(out or f"Reverse tcp:{remote} → host tcp:{local}")
        else:
            print_error(out or "reverse failed")

    elif choice == "3":
        r = _run_host(["forward", "--list"])
        console.print((r.stdout + r.stderr).strip() or "[dim](no rules)[/dim]")

    elif choice == "4":
        spec = console.input(
            "[cyan]Rule spec to remove[/cyan] [dim](e.g. tcp:8080)[/dim]> "
        ).strip()
        if not spec:
            print_null_input()
            return
        r = _run_host(["forward", "--remove", spec])
        out = (r.stdout + r.stderr).strip()
        if r.returncode == 0:
            print_success(out or "Removed.")
        else:
            print_error(out or "remove failed")

    elif choice == "5":
        r = _run_host(["forward", "--remove-all"])
        out = (r.stdout + r.stderr).strip()
        if r.returncode == 0:
            print_success(out or "All forwarding rules removed.")
        else:
            print_error(out or "failed")

    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
