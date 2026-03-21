import os
import socket
import subprocess
import nmap
from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_null_input,
    confirm,
    task_status,
    adb,
    adb_output,
)


def get_ip_address() -> str | None:
    """Best-effort LAN IP for LHOST / scanning. Returns None if offline or unreachable."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(3.0)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return None


def is_valid_ipv4(address: str) -> bool:
    parts = address.strip().split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def _list_ready_device_serials() -> list[str]:
    """Serial numbers of devices in the `device` state (authorized, ready)."""
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    serials: list[str] = []
    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if not line or "\t" not in line:
            continue
        serial, _, rest = line.partition("\t")
        serial = serial.strip()
        state = rest.split()[0] if rest.split() else ""
        if state == "device":
            serials.append(serial)
    return serials


def prompt_select_device_if_multiple() -> None:
    """
    Set ANDROID_SERIAL for this process when multiple USB/network devices are connected.
    adb honors ANDROID_SERIAL as the default target (see Android platform-tools docs).
    """
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
    console.print(
        "[cyan]Target phone IP[/cyan] [dim](e.g. 192.168.1.23)[/dim]"
    )
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

    with task_status("[info]Restarting ADB server…[/info]"):
        subprocess.run(
            ["adb", "kill-server"],
            capture_output=True,
        )
        subprocess.run(
            ["adb", "start-server"],
            capture_output=True,
        )

    with task_status(f"[info]Connecting to {ip}:5555…[/info]"):
        result = adb(["connect", f"{ip}:5555"])

    output = result.stdout.strip()
    if "connected" in output.lower():
        print_success(output)
        prompt_select_device_if_multiple()
    else:
        print_error(output or result.stderr.strip())


def list_devices(config: AppConfig) -> None:
    with task_status("[info]Fetching connected devices…[/info]"):
        result = adb(["devices", "-l"])

    lines = result.stdout.strip().splitlines()
    if len(lines) <= 1:
        console.print("[yellow]No devices connected.[/yellow]")
        return

    table = Table(title="Connected Devices", show_header=True, header_style="bold cyan")
    table.add_column("Device", style="white")
    table.add_column("State", style="green")
    table.add_column("Info", style="dim white")

    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split()
        device = parts[0] if len(parts) > 0 else ""
        state = parts[1] if len(parts) > 1 else ""
        info = " ".join(parts[2:]) if len(parts) > 2 else ""
        table.add_row(device, state, info)

    console.print(table)


def disconnect(config: AppConfig) -> None:
    if not confirm("Disconnect [bold]all[/bold] ADB devices?"):
        return
    with task_status("[info]Disconnecting…[/info]"):
        result = adb(["disconnect"])
    os.environ.pop("ANDROID_SERIAL", None)
    console.print(f"[green]{result.stdout.strip()}[/green]")


def stop_adb(config: AppConfig) -> None:
    if not confirm(
        "Stop the ADB server? [yellow]All device connections will be lost[/yellow] until you start ADB again."
    ):
        return
    with task_status("[info]Stopping ADB server…[/info]"):
        adb(["kill-server"])
    os.environ.pop("ANDROID_SERIAL", None)
    print_success("ADB server stopped.")


def scan_network(config: AppConfig) -> None:
    ip = get_ip_address()
    if ip is None:
        print_error(
            "Could not detect a local IP address. Check your network connection and try again."
        )
        return
    subnet = ip + "/24"

    scanner = nmap.PortScanner()
    with task_status(f"[info]Scanning {subnet}…[/info]"):
        scanner.scan(hosts=subnet, arguments="-sn")

    hosts = [h for h in scanner.all_hosts() if scanner[h]["status"]["state"] == "up"]

    if not hosts:
        console.print("[yellow]No hosts found.[/yellow]")
        return

    table = Table(title=f"Network Scan — {subnet}", show_header=True, header_style="bold cyan")
    table.add_column("IP Address", style="bold green")
    table.add_column("Vendor / MAC", style="white")
    table.add_column("Hostname", style="dim white")

    for host in hosts:
        vendor_info = scanner[host].get("vendor", {})
        vendor = ", ".join(vendor_info.values()) if vendor_info else ""
        try:
            hostname = socket.gethostbyaddr(host)[0]
        except OSError:
            hostname = ""
        table.add_row(host, vendor, hostname)

    console.print(table)
