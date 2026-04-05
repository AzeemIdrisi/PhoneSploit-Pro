import subprocess
from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_warning,
    task_status,
    submenu_row,
    adb,
    adb_output,
    get_adb_executable,
)


def get_shell(config: AppConfig) -> None:
    console.print("[cyan]Opening interactive ADB shell…[/cyan] [dim](exit shell to return)[/dim]")
    exe = get_adb_executable()
    if not exe:
        print_error("ADB not available.")
        return
    subprocess.run([exe, "shell"])


def get_device_info(config: AppConfig) -> None:
    props = {
        "Model":            ["getprop", "ro.product.model"],
        "Manufacturer":     ["getprop", "ro.product.manufacturer"],
        "Chipset":          ["getprop", "ro.product.board"],
        "Android Version":  ["getprop", "ro.build.version.release"],
        "Security Patch":   ["getprop", "ro.build.version.security_patch"],
        "Device":           ["getprop", "ro.product.vendor.device"],
        "SIM Operator":     ["getprop", "gsm.sim.operator.alpha"],
        "Encryption":       ["getprop", "ro.crypto.state"],
        "Build Date":       ["getprop", "ro.build.date"],
        "SDK Version":      ["getprop", "ro.build.version.sdk"],
        "WiFi Interface":   ["getprop", "wifi.interface"],
    }

    with task_status("[info]Fetching device information…[/info]"):
        results = {label: adb_output(["shell"] + cmd) for label, cmd in props.items()}

    table = Table(title="Device Information", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="bold yellow")
    table.add_column("Value", style="white")

    for label, value in results.items():
        table.add_row(label, value or "[dim]N/A[/dim]")

    console.print(table)


def battery_info(config: AppConfig) -> None:
    with task_status("[info]Fetching battery information…[/info]"):
        raw = adb_output(["shell", "dumpsys", "battery"])

    table = Table(title="Battery Information", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="bold yellow")
    table.add_column("Value", style="white")

    for line in raw.splitlines():
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            table.add_row(key.strip(), value.strip())

    console.print(table)


def reboot(config: AppConfig, key: str) -> None:
    print_warning("Restarting will disconnect the device.")
    choice = console.input("[white]Continue? [bold]Y / N[/bold][/white] > ").lower()
    while choice not in ("y", "n", ""):
        choice = console.input("[error]Invalid![/error] Y or N > ").lower()
    if choice == "n":
        return

    if key == "system":
        with task_status("[info]Rebooting device…[/info]"):
            adb(["reboot"])
    else:
        submenu_row("Recovery", "Bootloader", "Fastboot")
        mode = console.input("[prompt]> [/prompt]")
        cmd_map = {"1": "recovery", "2": "bootloader", "3": "fastboot"}
        if mode not in cmd_map:
            print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
            return
        with task_status(f"[info]Rebooting to {cmd_map[mode]}…[/info]"):
            adb(["reboot", cmd_map[mode]])


def power_off(config: AppConfig) -> None:
    print_warning("Powering off will disconnect the device.")
    choice = console.input("[white]Continue? [bold]Y / N[/bold][/white] > ").lower()
    while choice not in ("y", "n", ""):
        choice = console.input("[error]Invalid![/error] Y or N > ").lower()
    if choice == "n":
        return
    with task_status("[info]Powering off…[/info]"):
        adb(["shell", "reboot", "-p"])


def unlock_device(config: AppConfig) -> None:
    password = console.input(
        "[yellow]Password or Enter for blank[/yellow]> "
    )
    with task_status("[info]Sending unlock sequence…[/info]"):
        adb(["shell", "input", "keyevent", "26"])
        adb(["shell", "input", "swipe", "200", "900", "200", "300", "200"])
        if password:
            adb(["shell", "input", "text", password])
        adb(["shell", "input", "keyevent", "66"])
    print_success("Device unlocked.")


def lock_device(config: AppConfig) -> None:
    with task_status("[info]Locking…[/info]"):
        adb(["shell", "input", "keyevent", "26"])
    print_success("Device locked.")
