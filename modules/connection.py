"""CLI adapters for connection — delegates to service layer."""

import os
from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_null_input,
    confirm,
    task_status,
    get_adb_executable,
)
from modules.services.adb import ADBService
from modules.services import connection as conn_svc

# Re-export for other modules
get_ip_address = conn_svc.get_ip_address
is_valid_ipv4 = conn_svc.is_valid_ipv4


def _adb() -> ADBService:
    return ADBService(get_adb_executable())


def _list_ready_device_serials() -> list[str]:
    return conn_svc.list_ready_serials(_adb())


def prompt_select_device_if_multiple(config: AppConfig) -> None:
    if not config.adb_path:
        os.environ.pop("ANDROID_SERIAL", None)
        return

    serials = _list_ready_device_serials()
    if not serials:
        os.environ.pop("ANDROID_SERIAL", None)
        return
    if len(serials) == 1:
        os.environ["ANDROID_SERIAL"] = serials[0]
        return

    table = Table(
        title="Multiple devices detected",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="bold green", justify="right")
    table.add_column("Serial", style="white")
    for i, s in enumerate(serials, 1):
        table.add_row(str(i), s)

    console.print(table)
    console.print("[yellow]Choose default device for this session.[/yellow]")
    choice = console.input(
        f"[prompt]Enter 1–{len(serials)} (Enter = first) > [/prompt]"
    ).strip()
    idx = 0
    if choice.isdigit():
        n = int(choice)
        if 1 <= n <= len(serials):
            idx = n - 1
    os.environ["ANDROID_SERIAL"] = serials[idx]
    console.print(f"[green]Using device[/green] [white]{serials[idx]}[/white]")


def connect(config: AppConfig) -> None:
    console.print("[cyan]Target phone IP[/cyan] [dim](e.g. 192.168.1.23)[/dim]")
    ip = console.input("[prompt]> [/prompt]").strip()
    if not ip:
        print_null_input()
        return

    if not is_valid_ipv4(ip):
        print_error("Invalid IPv4 address\n[green] Going back to Main Menu[/green]")
        return

    if not confirm(
        "Connecting will [yellow]restart the ADB server[/yellow] and may disconnect "
        "other active ADB sessions on this computer. Continue?"
    ):
        return

    with task_status(f"[info]Connecting to {ip}:5555…[/info]"):
        result = conn_svc.connect_device(_adb(), ip)

    if result.success:
        print_success(result.message)
        prompt_select_device_if_multiple(config)
    else:
        print_error(result.message or result.error or "Connection failed")


def list_devices(config: AppConfig) -> None:
    with task_status("[info]Fetching connected devices…[/info]"):
        result = conn_svc.list_devices(_adb())

    devices = result.data or []
    if not devices:
        console.print("[yellow]No devices connected.[/yellow]")
        return

    table = Table(title="Connected Devices", show_header=True, header_style="bold cyan")
    table.add_column("Device", style="white")
    table.add_column("State", style="green")
    table.add_column("Info", style="dim white")

    for d in devices:
        table.add_row(d.serial, d.state, d.info)

    console.print(table)


def disconnect(config: AppConfig) -> None:
    if not confirm("Disconnect [bold]all[/bold] ADB devices?"):
        return
    with task_status("[info]Disconnecting…[/info]"):
        result = conn_svc.disconnect_all(_adb())
    console.print(f"[green]{result.message}[/green]")


def stop_adb(config: AppConfig) -> None:
    if not confirm(
        "Stop the ADB server? [yellow]All device connections will be lost[/yellow] until you start ADB again."
    ):
        return
    with task_status("[info]Stopping ADB server…[/info]"):
        result = conn_svc.stop_adb_server(_adb())
    if result.success:
        print_success(result.message)


def scan_network(config: AppConfig) -> None:
    with task_status("[info]Scanning network…[/info]"):
        result = conn_svc.scan_network(config)

    if not result.success and not result.data:
        print_error(result.message)
        return

    hosts = result.data or []
    if not hosts:
        console.print("[yellow]No hosts found.[/yellow]")
        return

    ip = get_ip_address() or "?"
    table = Table(
        title=f"Network Scan — {ip}/24",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("IP Address", style="bold green")
    table.add_column("ADB 5555 / 5554", style="cyan")
    table.add_column("Android?", style="yellow")

    for h in hosts:
        table.add_row(h.ip, h.adb_summary, h.android_hint)

    console.print(table)
