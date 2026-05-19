import os
import platform
import subprocess
from pathlib import Path

from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_warning,
    adb,
    get_adb_executable,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUTO_ADB_TOOL_DIR = PROJECT_ROOT / "tools" / "auto-adb-apk"
AUTO_ADB_SCRIPT = AUTO_ADB_TOOL_DIR / "install_and_grant_permissions.ps1"
AUTO_ADB_APK = AUTO_ADB_TOOL_DIR / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"


def _ready_adb_devices() -> list[dict[str, str]]:
    result = adb(["devices", "-l"])
    devices: list[dict[str, str]] = []
    if result.returncode != 0:
        return devices

    for raw_line in (result.stdout or "").splitlines()[1:]:
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2 or parts[1] != "device":
            continue
        serial = parts[0]
        info = " ".join(parts[2:])
        transport = "Wireless" if ":" in serial else "USB"
        devices.append({"serial": serial, "transport": transport, "info": info})
    return devices


def _show_devices(devices: list[dict[str, str]]) -> None:
    table = Table(title="Ready ADB Devices", show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold yellow", no_wrap=True)
    table.add_column("Serial", style="white")
    table.add_column("Transport", style="cyan")
    table.add_column("Info", style="dim")
    for index, device in enumerate(devices, start=1):
        table.add_row(str(index), device["serial"], device["transport"], device["info"])
    console.print(table)


def _selected_or_prompted_serial() -> str | None:
    devices = _ready_adb_devices()
    selected = os.environ.get("ANDROID_SERIAL", "").strip()
    ready_serials = {device["serial"] for device in devices}

    if selected and selected in ready_serials:
        transport = "Wireless" if ":" in selected else "USB"
        console.print(f"[cyan]Using {transport} device[/cyan] [white]{selected}[/white]")
        return selected

    if len(devices) == 1:
        device = devices[0]
        console.print(
            f"[cyan]Using {device['transport']} device[/cyan] [white]{device['serial']}[/white]"
        )
        return device["serial"]

    usb_devices = [device for device in devices if device["transport"] == "USB"]

    if not devices:
        print_error("No ready ADB device found. Connect the phone with USB or wireless ADB first.")
        return None

    print_warning("Several ADB devices are ready. Choose the one to configure.")
    _show_devices(devices)
    default = selected if selected in ready_serials else usb_devices[0]["serial"] if usb_devices else devices[0]["serial"]
    prompt = "[prompt]Device serial"
    if default:
        prompt += f" (Enter = {default})"
    prompt += " > [/prompt]"
    serial = console.input(prompt).strip() or default
    if not serial:
        print_error("No device serial selected.")
        return None
    return serial


def _script_environment(config: AppConfig) -> dict[str, str]:
    env = os.environ.copy()
    adb_exe = config.adb_path or get_adb_executable()
    if adb_exe:
        env["ADB"] = adb_exe
        adb_dir = str(Path(adb_exe).resolve().parent)
        env["PATH"] = adb_dir + os.pathsep + env.get("PATH", "")
    return env


def wifi_persistence(config: AppConfig) -> None:
    if platform.system() != "Windows":
        print_error("Persistance WiFi uses a PowerShell setup script and currently runs on Windows.")
        return

    if not AUTO_ADB_SCRIPT.is_file():
        print_error(f"Missing imported setup script: {AUTO_ADB_SCRIPT}")
        return

    if not AUTO_ADB_APK.is_file():
        print_error(f"Missing imported Auto WiFi APK: {AUTO_ADB_APK}")
        return

    serial = _selected_or_prompted_serial()
    if not serial:
        return

    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        ".\\install_and_grant_permissions.ps1",
        "-DeviceSerial",
        serial,
        "-SetupShizuku",
        "-HideShizuku",
        "-EnableTcpAdb",
    ]

    console.print("[cyan]Persistance WiFi[/cyan] [dim](Auto WiFi + Shizuku + ADB TCP/IP)[/dim]")
    console.print(
        "[dim]powershell -ExecutionPolicy Bypass -File .\\install_and_grant_permissions.ps1 "
        f"-DeviceSerial {serial} -SetupShizuku -HideShizuku -EnableTcpAdb[/dim]"
    )
    if ":" in serial:
        print_warning("Running over wireless ADB. Keep the phone reachable on the network while setup runs.")
    else:
        print_warning("Keep the phone plugged in USB while the setup runs.")

    result = subprocess.run(
        command,
        cwd=AUTO_ADB_TOOL_DIR,
        env=_script_environment(config),
    )

    if result.returncode == 0:
        print_success("Persistance WiFi setup finished.")
    else:
        print_error(f"Persistance WiFi setup failed with exit code {result.returncode}.")
