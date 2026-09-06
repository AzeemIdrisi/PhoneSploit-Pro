import ipaddress
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
    go_back_to_main_menu,
    adb,
    get_adb_executable,
    ask,
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


def _sort_ipv4(hosts: list[str]) -> list[str]:
    return sorted(hosts, key=lambda h: int(ipaddress.IPv4Address(h)))


def _adb_port_summary(host_data: dict) -> str:
    """Describe open 5555/5554 and any -sV fingerprint (e.g. Android Debug Bridge)."""
    tcp = host_data.get("tcp") or {}
    lines: list[str] = []
    for port in (5555, 5554):
        pinfo = tcp.get(port)
        if not pinfo or pinfo.get("state") != "open":
            continue
        product = (pinfo.get("product") or "").strip()
        version = (pinfo.get("version") or "").strip()
        extra = (pinfo.get("extrainfo") or "").strip()
        name = (pinfo.get("name") or "").strip()
        bits: list[str] = [f"{port}/tcp open"]
        if product:
            bits.append(product)
        elif name and name != "unknown":
            bits.append(name)
        if version:
            bits.append(version)
        if extra and extra not in product:
            bits.append(extra)
        lines.append(" ".join(bits))
    return " · ".join(lines) if lines else ""


def _android_hint(adb_summary: str) -> str:
    """Interpret ADB port probe only (no MAC/hostname/OUI)."""
    if not adb_summary:
        return ""
    a = adb_summary.lower()
    if "android debug bridge" in a or "free adb" in a:
        return "Strong: ADB fingerprint"
    if "5555/tcp open" in adb_summary or "5554/tcp open" in adb_summary:
        return "Strong: ADB port open (wireless/emulator)"
    if "adb" in a and "open" in a:
        return "Likely: ADB-related port"
    return ""


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
    exe = get_adb_executable()
    if not exe:
        return []
    result = subprocess.run([exe, "devices"], capture_output=True, text=True)
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


def prompt_select_device_if_multiple(config: AppConfig) -> None:
    """
    Set ANDROID_SERIAL for this process when multiple USB/network devices are connected.
    adb honors ANDROID_SERIAL as the default target (see Android platform-tools docs).
    """
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
    table.add_column("Serial", style="bold white")
    for i, s in enumerate(serials, 1):
        table.add_row(str(i), s)

    console.print(table)
    console.print("[bold yellow]Choose default device for this session.[/bold yellow]")
    choice = ask(
        f"[prompt]Enter 1–{len(serials)} (Enter = first) > [/prompt]"
    ).strip()
    idx = 0
    if choice.isdigit():
        n = int(choice)
        if 1 <= n <= len(serials):
            idx = n - 1
    os.environ["ANDROID_SERIAL"] = serials[idx]
    console.print(f"[bold green]Using device[/bold green] [bold white]{serials[idx]}[/bold white]")


def connect(config: AppConfig) -> None:
    console.print(
        "[bold cyan]Target phone IP[/bold cyan] [dim](e.g. 192.168.1.23)[/dim]"
    )
    ip = ask("[prompt]> [/prompt]").strip()
    if not ip:
        print_null_input()
        return

    if not is_valid_ipv4(ip):
        go_back_to_main_menu(config, "Invalid IPv4 address")
        return

    with task_status(f"[info]Connecting to {ip}:5555…[/info]"):
        result = adb(["connect", f"{ip}:5555"])

    output = result.stdout.strip()
    if "connected" in output.lower():
        print_success(output)
        prompt_select_device_if_multiple(config)
    else:
        print_error(output or result.stderr.strip())


def list_devices(config: AppConfig) -> None:
    with task_status("[info]Fetching connected devices…[/info]"):
        result = adb(["devices", "-l"])

    lines = result.stdout.strip().splitlines()
    if len(lines) <= 1:
        console.print("[bold yellow]No devices connected.[/bold yellow]")
        return

    table = Table(title="Connected Devices", show_header=True, header_style="bold cyan")
    table.add_column("Device", style="bold white")
    table.add_column("State", style="bold green")
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
    if not confirm("Disconnect [bold white]all[/bold white] ADB devices?"):
        return
    with task_status("[info]Disconnecting…[/info]"):
        result = adb(["disconnect"])
    os.environ.pop("ANDROID_SERIAL", None)
    console.print(f"[bold green]{result.stdout.strip()}[/bold green]")


def stop_adb(config: AppConfig) -> None:
    if not confirm(
        "Stop the ADB server? [bold yellow]All device connections will be lost[/bold yellow] until you start ADB again."
    ):
        return
    with task_status("[info]Stopping ADB server…[/info]"):
        adb(["kill-server"])
    os.environ.pop("ANDROID_SERIAL", None)
    print_success("ADB server stopped.")


def restart_adb(config: AppConfig) -> None:
    if not confirm(
        "Restart the ADB server? [bold yellow]Active ADB sessions on this computer "
        "may be disconnected[/bold yellow] until the server restarts."
    ):
        return
    adb_exe = get_adb_executable()
    if not adb_exe:
        print_error("ADB executable not available.")
        return
    with task_status("[info]Restarting ADB server…[/info]"):
        subprocess.run([adb_exe, "kill-server"], capture_output=True)
        subprocess.run([adb_exe, "start-server"], capture_output=True)
    os.environ.pop("ANDROID_SERIAL", None)
    print_success("ADB server restarted.")
    prompt_select_device_if_multiple(config)


def _port_scanner(config: AppConfig) -> nmap.PortScanner:
    """Use the same nmap binary as startup resolution when available."""
    if config.nmap_path:
        return nmap.PortScanner(nmap_search_path=(config.nmap_path,))
    return nmap.PortScanner()


def scan_network(config: AppConfig) -> None:
    ip = get_ip_address()
    if ip is None:
        print_error(
            "Could not detect a local IP address. Check your network connection and try again."
        )
        return
    subnet = ip + "/24"

    discover = _port_scanner(config)
    with task_status(f"[info]Discovering hosts on {subnet}…[/info]"):
        discover.scan(hosts=subnet, arguments="-sn")

    hosts = [
        h
        for h in discover.all_hosts()
        if discover[h]["status"]["state"] == "up"
    ]
    hosts = _sort_ipv4(hosts)

    if not hosts:
        console.print("[bold yellow]No hosts found.[/bold yellow]")
        return

    ports_scan = _port_scanner(config)
    with task_status(
        "[info]Probing ADB ports 5555/5554 (TCP + service probe) on live hosts…[/info]"
    ):
        try:
            ports_scan.scan(
                hosts=" ".join(hosts),
                arguments="-p 5555,5554 -sT -sV --version-intensity 1 -T4",
            )
        except nmap.PortScannerError as e:
            print_error(f"ADB port scan failed: {e}")
            ports_scan = None

    table = Table(title=f"Network Scan — {subnet}", show_header=True, header_style="bold cyan")
    table.add_column("IP Address", style="bold green")
    table.add_column("ADB 5555 / 5554", style="bold cyan")
    table.add_column("Android?", style="bold yellow")

    for host in hosts:
        adb_summary = ""
        if ports_scan and host in ports_scan.all_hosts():
            adb_summary = _adb_port_summary(ports_scan[host])
        hint = _android_hint(adb_summary)
        table.add_row(
            host,
            adb_summary or "—",
            hint or "—",
        )

    console.print(table)


def _wireless_pair() -> None:
    addr = ask(
        "[bold cyan]Pairing address[/bold cyan] [dim](IP:port from Wireless Debugging)[/dim]> "
    ).strip()
    if not addr:
        print_null_input()
        return
    code = ask("[bold cyan]6-digit pairing code[/bold cyan]> ").strip()
    if not code:
        print_null_input()
        return
    exe = get_adb_executable()
    if not exe:
        print_error("ADB executable not available.")
        return
    with task_status(f"[info]Pairing with {addr}…[/info]"):
        result = subprocess.run([exe, "pair", addr, code], capture_output=True, text=True)
    out = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        print_success(out or "Paired. Use Connect with the other IP:port shown on the device.")
    else:
        print_error(out or f"Pairing failed (exit code {result.returncode}).")


def _wireless_connect(config: AppConfig) -> None:
    addr = ask("[bold cyan]Address[/bold cyan] [dim](IP:port or IP, default :5555)[/dim]> ").strip()
    if not addr:
        print_null_input()
        return
    if ":" not in addr:
        addr = f"{addr}:5555"
    with task_status(f"[info]Connecting to {addr}…[/info]"):
        r = adb(["connect", addr])
    out = (r.stdout + r.stderr).strip()
    if "connected" in out.lower():
        print_success(out)
        prompt_select_device_if_multiple(config)
    else:
        print_error(out or "connect failed")


def _wireless_tcpip() -> None:
    port = ask("[bold cyan]Port[/bold cyan] [dim](Enter=5555)[/dim]> ").strip() or "5555"
    if not port.isdigit():
        print_error("Port must be a number.")
        return
    if not confirm("Restart adb in TCP/IP listening mode?"):
        return
    with task_status("[info]Switching to TCP/IP mode…[/info]"):
        r = adb(["tcpip", port])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or f"adb now listening on TCP port {port}.")
    else:
        print_error(out or "failed")


def _wireless_usb() -> None:
    if not confirm("Switch adb back to USB mode?"):
        return
    with task_status("[info]Switching to USB mode…[/info]"):
        r = adb(["usb"])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        print_success(out or "adb now listening on USB.")
    else:
        print_error(out or "failed")


def wireless_pair() -> None:
    _wireless_pair()


def wireless_connect(config: AppConfig) -> None:
    _wireless_connect(config)


def wireless_tcpip() -> None:
    _wireless_tcpip()


def wireless_usb() -> None:
    _wireless_usb()



