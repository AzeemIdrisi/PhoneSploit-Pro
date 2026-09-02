"""Host-side adb forward / reverse (uses local adb binary, not adb shell)."""

import subprocess

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_null_input,
    get_adb_executable,
    ask,
)


def _run_host(args: list[str]) -> subprocess.CompletedProcess:
    exe = get_adb_executable()
    if not exe:
        return subprocess.CompletedProcess(args=[], returncode=127, stdout="", stderr="no adb")
    return subprocess.run([exe] + args, capture_output=True, text=True)


def _prompt_ports(title: str) -> tuple[str, str] | None:
    local = ask(f"[bold cyan]{title}[/bold cyan] [dim](TCP port)[/dim]> ").strip()
    remote = ask("[bold cyan]Remote (device) TCP port[/bold cyan]> ").strip()
    if not local.isdigit() or not remote.isdigit():
        print_null_input()
        return None
    return local, remote


def port_forward_add(config: AppConfig) -> None:
    ports = _prompt_ports("Local (PC) TCP port")
    if ports is None:
        return
    local, remote = ports
    r = _run_host(["forward", f"tcp:{local}", f"tcp:{remote}"])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or f"Forwarded tcp:{local} → device tcp:{remote}")
    else:
        print_error(out or "forward failed")


def port_forward_reverse(config: AppConfig) -> None:
    ports = _prompt_ports("Device TCP port")
    if ports is None:
        return
    remote, local = ports
    r = _run_host(["reverse", f"tcp:{remote}", f"tcp:{local}"])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or f"Reverse tcp:{remote} → host tcp:{local}")
    else:
        print_error(out or "reverse failed")


def port_forward_list(config: AppConfig) -> None:
    r = _run_host(["forward", "--list"])
    console.print((r.stdout + r.stderr).strip() or "[dim](no rules)[/dim]")


def port_forward_remove(config: AppConfig) -> None:
    spec = ask("[bold cyan]Rule spec to remove[/bold cyan] [dim](e.g. tcp:8080)[/dim]> ").strip()
    if not spec:
        print_null_input()
        return
    r = _run_host(["forward", "--remove", spec])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or "Removed.")
    else:
        print_error(out or "remove failed")


def port_forward_remove_all(config: AppConfig) -> None:
    r = _run_host(["forward", "--remove-all"])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or "All forwarding rules removed.")
    else:
        print_error(out or "failed")