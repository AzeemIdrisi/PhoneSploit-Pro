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
    print_submenu,
    parse_submenu_choice,
    adb,
    adb_output,
    get_adb_executable,
    ask,
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


def _print_battery_mock_status() -> None:
    with task_status("[info]Reading battery state…[/info]"):
        raw = adb_output(["shell", "dumpsys", "battery"])
    keys = ("level", "status", "AC powered", "USB powered", "Wireless powered")
    table = Table(title="Battery Mock Status", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="yellow")
    table.add_column("Value", style="white")
    for line in raw.splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key in keys:
            table.add_row(key, value.strip())
    console.print(table)


def mock_battery(config: AppConfig) -> None:
    print_warning("Battery mocking freezes real battery readings. Always use Reset when finished.")
    items = [
        "Set Battery Level",
        "Simulate Unplugged",
        "Simulate Plugged",
        "Reset",
        "Show Current Mock Status",
    ]

    def _render() -> None:
        print_submenu("Mock Battery", items)

    _render()
    while True:
        choice = ask("[red]\\[Mock Battery][/red] > ").strip().lower()
        action = parse_submenu_choice(choice, config, _render)
        if action == "exit":
            return
        if action == "redraw":
            continue
        if choice == "1":
            raw = ask("[cyan]Level[/cyan] [dim](0-100)[/dim]> ").strip()
            if not raw.isdigit() or not 0 <= int(raw) <= 100:
                print_error("Enter a number between 0 and 100.")
                continue
            with task_status("[info]Setting battery level…[/info]"):
                r = adb(["shell", "dumpsys", "battery", "set", "level", raw])
            out = (r.stdout + r.stderr).strip()
            if r.returncode == 0:
                print_success(out or "Battery level set.")
                _print_battery_mock_status()
            else:
                print_error(out or "failed")
        elif choice == "2":
            with task_status("[info]Simulating unplugged…[/info]"):
                r = adb(["shell", "dumpsys", "battery", "unplug"])
            out = (r.stdout + r.stderr).strip()
            if r.returncode == 0:
                print_success(out or "Unplugged simulated.")
                _print_battery_mock_status()
            else:
                print_error(out or "failed")
        elif choice == "3":
            with task_status("[info]Simulating plugged (charging)…[/info]"):
                adb(["shell", "dumpsys", "battery", "set", "ac", "1"])
                adb(["shell", "dumpsys", "battery", "set", "usb", "1"])
                r = adb(["shell", "dumpsys", "battery", "set", "status", "2"])
            out = (r.stdout + r.stderr).strip()
            if r.returncode == 0:
                print_success(out or "Plugged / charging simulated.")
                _print_battery_mock_status()
            else:
                print_error(out or "failed")
        elif choice == "4":
            with task_status("[info]Resetting battery readings…[/info]"):
                r = adb(["shell", "dumpsys", "battery", "reset"])
            out = (r.stdout + r.stderr).strip()
            if r.returncode == 0:
                print_success(out or "Battery readings reset.")
                _print_battery_mock_status()
            else:
                print_error(out or "failed")
        elif choice == "5":
            _print_battery_mock_status()
        else:
            print_error("Invalid selection")


def reboot(config: AppConfig, key: str) -> None:
    print_warning("Restarting will disconnect the device.")
    choice = ask("[white]Continue? [bold]Y / N[/bold][/white] > ").lower()
    while choice not in ("y", "n", ""):
        choice = ask("[error]Invalid![/error] Y or N > ").lower()
    if choice == "n":
        return

    if key == "system":
        with task_status("[info]Rebooting device…[/info]"):
            adb(["reboot"])
    else:
        submenu_row("Recovery", "Bootloader", "Fastboot")
        mode = ask("[prompt]> [/prompt]")
        cmd_map = {"1": "recovery", "2": "bootloader", "3": "fastboot"}
        if mode not in cmd_map:
            print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
            return
        with task_status(f"[info]Rebooting to {cmd_map[mode]}…[/info]"):
            adb(["reboot", cmd_map[mode]])


def power_off(config: AppConfig) -> None:
    print_warning("Powering off will disconnect the device.")
    choice = ask("[white]Continue? [bold]Y / N[/bold][/white] > ").lower()
    while choice not in ("y", "n", ""):
        choice = ask("[error]Invalid![/error] Y or N > ").lower()
    if choice == "n":
        return
    with task_status("[info]Powering off…[/info]"):
        adb(["shell", "reboot", "-p"])


def unlock_device(config: AppConfig) -> None:
    password = ask(
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
