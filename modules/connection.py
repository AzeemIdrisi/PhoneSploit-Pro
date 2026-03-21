import socket
import subprocess
import nmap
from rich.table import Table

from modules.config import AppConfig
from modules.console import console, print_error, print_success, print_null_input, confirm, adb, adb_output


def get_ip_address() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def connect(config: AppConfig) -> None:
    console.print(
        "\n[cyan]Enter target phone's IP Address       [yellow]Example : 192.168.1.23[/yellow][/cyan]"
    )
    ip = console.input("[prompt]> [/prompt]")
    if not ip:
        print_null_input()
        return

    if ip.count(".") != 3:
        print_error("Invalid IP Address\n[green] Going back to Main Menu[/green]")
        return

    if not confirm(
        "Connecting will [yellow]restart the ADB server[/yellow] and may disconnect "
        "other active ADB sessions on this computer. Continue?"
    ):
        return

    with console.status(f"[info]Restarting ADB server...[/info]"):
        subprocess.run(
            ["adb", "kill-server"],
            capture_output=True,
        )
        subprocess.run(
            ["adb", "start-server"],
            capture_output=True,
        )

    with console.status(f"[info]Connecting to {ip}:5555...[/info]"):
        result = adb(["connect", f"{ip}:5555"])

    output = result.stdout.strip()
    if "connected" in output.lower():
        print_success(output)
    else:
        print_error(output or result.stderr.strip())
    console.print()


def list_devices(config: AppConfig) -> None:
    with console.status("[info]Fetching connected devices...[/info]"):
        result = adb(["devices", "-l"])

    lines = result.stdout.strip().splitlines()
    if len(lines) <= 1:
        console.print("\n[yellow]No devices connected.[/yellow]\n")
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

    console.print()
    console.print(table)
    console.print()


def disconnect(config: AppConfig) -> None:
    if not confirm("Disconnect [bold]all[/bold] ADB devices?"):
        return
    with console.status("[info]Disconnecting all devices...[/info]"):
        result = adb(["disconnect"])
    console.print(f"\n[green]{result.stdout.strip()}[/green]\n")


def stop_adb(config: AppConfig) -> None:
    if not confirm(
        "Stop the ADB server? [yellow]All device connections will be lost[/yellow] until you start ADB again."
    ):
        return
    with console.status("[info]Stopping ADB server...[/info]"):
        adb(["kill-server"])
    print_success("ADB server stopped.")


def scan_network(config: AppConfig) -> None:
    ip = get_ip_address()
    subnet = ip + "/24"
    console.print(f"\n[green]Scanning [bold]{subnet}[/bold] for connected devices...[/green]\n")

    scanner = nmap.PortScanner()
    with console.status(f"[info]Scanning {subnet} (this may take a moment)...[/info]"):
        scanner.scan(hosts=subnet, arguments="-sn")

    hosts = [h for h in scanner.all_hosts() if scanner[h]["status"]["state"] == "up"]

    if not hosts:
        console.print("[yellow]No hosts found.[/yellow]\n")
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
        except Exception:
            hostname = ""
        table.add_row(host, vendor, hostname)

    console.print(table)
    console.print()
