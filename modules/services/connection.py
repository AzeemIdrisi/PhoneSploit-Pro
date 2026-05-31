"""Connection and network scan services."""

from __future__ import annotations

import ipaddress
import os
import socket
from dataclasses import dataclass

import nmap

from modules.config import AppConfig
from modules.services.adb import ADBService, OperationResult


@dataclass
class DeviceInfo:
    serial: str
    state: str
    info: str = ""


def get_ip_address() -> str | None:
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


def _sort_ipv4(hosts: list[str]) -> list[str]:
    return sorted(hosts, key=lambda h: int(ipaddress.IPv4Address(h)))


def _adb_port_summary(host_data: dict) -> str:
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


def list_ready_serials(adb: ADBService) -> list[str]:
    if not adb.available():
        return []
    result = adb.run(["devices"], host_level=True)
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


def list_devices(adb: ADBService) -> OperationResult:
    if not adb.available():
        return OperationResult(False, "ADB not available", error="no adb")
    result = adb.run(["devices", "-l"], host_level=True)
    devices: list[DeviceInfo] = []
    for line in result.stdout.strip().splitlines()[1:]:
        if not line.strip():
            continue
        parts = line.split()
        devices.append(
            DeviceInfo(
                serial=parts[0] if parts else "",
                state=parts[1] if len(parts) > 1 else "",
                info=" ".join(parts[2:]) if len(parts) > 2 else "",
            )
        )
    return OperationResult(True, f"{len(devices)} device(s)", data=devices)


def connect_device(adb: ADBService, host: str, port: int = 5555) -> OperationResult:
    if not is_valid_ipv4(host):
        return OperationResult(False, "Invalid IPv4 address", error="invalid ip")
    if not adb.available():
        return OperationResult(False, "ADB not available", error="no adb")

    adb.run(["kill-server"], host_level=True)
    adb.run(["start-server"], host_level=True)
    result = adb.run(["connect", f"{host}:{port}"], host_level=True)
    output = result.stdout.strip() or result.stderr.strip()
    if "connected" in output.lower():
        serials = list_ready_serials(adb)
        return OperationResult(
            True,
            output,
            data={"serials": serials, "host": host, "port": port},
        )
    return OperationResult(False, output or "Connection failed", error=output)


def disconnect_all(adb: ADBService) -> OperationResult:
    if not adb.available():
        return OperationResult(False, "ADB not available")
    result = adb.run(["disconnect"], host_level=True)
    os.environ.pop("ANDROID_SERIAL", None)
    return OperationResult(True, result.stdout.strip() or "Disconnected")


def stop_adb_server(adb: ADBService) -> OperationResult:
    if not adb.available():
        return OperationResult(False, "ADB not available")
    adb.run(["kill-server"], host_level=True)
    os.environ.pop("ANDROID_SERIAL", None)
    return OperationResult(True, "ADB server stopped")


def _port_scanner(config: AppConfig) -> nmap.PortScanner:
    if config.nmap_path:
        return nmap.PortScanner(nmap_search_path=(config.nmap_path,))
    return nmap.PortScanner()


@dataclass
class ScanHost:
    ip: str
    adb_summary: str
    android_hint: str


def scan_network(config: AppConfig) -> OperationResult:
    ip = get_ip_address()
    if ip is None:
        return OperationResult(
            False,
            "Could not detect local IP address",
            error="no local ip",
        )
    subnet = ip + "/24"
    discover = _port_scanner(config)
    discover.scan(hosts=subnet, arguments="-sn")
    hosts = [
        h for h in discover.all_hosts() if discover[h]["status"]["state"] == "up"
    ]
    hosts = _sort_ipv4(hosts)
    if not hosts:
        return OperationResult(True, "No hosts found", data=[])

    ports_scan = None
    try:
        ports_scan = _port_scanner(config)
        ports_scan.scan(
            hosts=" ".join(hosts),
            arguments="-p 5555,5554 -sT -sV --version-intensity 1 -T4",
        )
    except nmap.PortScannerError as e:
        return OperationResult(
            False,
            f"ADB port scan failed: {e}",
            data=[],
            error=str(e),
        )

    results: list[ScanHost] = []
    for host in hosts:
        adb_summary = ""
        if ports_scan and host in ports_scan.all_hosts():
            adb_summary = _adb_port_summary(ports_scan[host])
        results.append(
            ScanHost(
                ip=host,
                adb_summary=adb_summary or "—",
                android_hint=_android_hint(adb_summary) or "—",
            )
        )
    return OperationResult(True, f"Scanned {subnet}", data=results)
