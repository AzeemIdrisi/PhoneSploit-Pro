import os
import platform
import random
import subprocess
from pathlib import Path

from rich.panel import Panel

from modules import banner
from modules.config import AppConfig
from modules.console import console, print_success, confirm


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

def _detect_platform(config: AppConfig) -> None:
    config.operating_system = platform.system()
    if config.operating_system == "Windows":
        config.clear_cmd = "cls"
        config.opener = "start"
    elif config.operating_system == "Darwin":
        config.opener = "open"
    # Linux default: clear_cmd="clear", opener="xdg-open"

    if config.operating_system != "Windows":
        import readline  # noqa: F401  — enables arrow keys in input


def check_packages() -> None:
    tools = {
        "ADB":                  "adb",
        "Metasploit-Framework": "msfconsole",
        "Scrcpy":               "scrcpy",
        "Nmap":                 "nmap",
    }

    missing = [
        name for name, cmd in tools.items()
        if subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0
    ]

    if not missing:
        return

    items = "\n".join(f"  [bold yellow]{i + 1}.[/bold yellow] [white]{name}[/white]"
                      for i, name in enumerate(missing))
    console.print(
        Panel(
            f"[red]The following required tools are NOT installed:[/red]\n\n{items}\n\n"
            "[cyan]Please install the above listed software.[/cyan]",
            title="[bold red]Missing Dependencies[/bold red]",
            border_style="red",
        )
    )

    choice = console.input(
        "\n[green]Do you still want to continue to PhoneSploit Pro?[/green]     [bold]Y / N[/bold] > "
    ).lower()
    while choice not in ("y", "n", ""):
        choice = console.input("[red]Invalid choice![/red] Press Y or N > ").lower()

    if choice == "n":
        raise SystemExit(0)


def start(config: AppConfig) -> None:
    Path("Downloaded-Files").mkdir(exist_ok=True)
    _detect_platform(config)
    if config.operating_system != "Windows":
        check_packages()


# ---------------------------------------------------------------------------
# Menu display
# ---------------------------------------------------------------------------

_selected_banner: str = ""


def _pick_banner() -> str:
    colors = ["[red]", "[green]", "[yellow]", "[purple]", "[cyan]", "[white]"]
    color = random.choice(colors)
    art = random.choice(banner.banner_list)
    return f"{color}{art}[/{color.strip('[').rstrip(']')}]"


def display_menu(config: AppConfig) -> None:
    global _selected_banner
    console.print(_selected_banner)
    console.print(banner.menu[config.page_number])


def clear_screen(config: AppConfig) -> None:
    os.system(config.clear_cmd)
    display_menu(config)


def change_page(config: AppConfig, direction: str) -> None:
    if direction == "p" and config.page_number > 0:
        config.page_number -= 1
    elif direction == "n" and config.page_number < 2:
        config.page_number += 1
    clear_screen(config)


# ---------------------------------------------------------------------------
# Misc actions
# ---------------------------------------------------------------------------

def update_me(config: AppConfig) -> None:
    if not confirm(
        "Run [cyan]git fetch[/cyan] and [cyan]git rebase[/cyan] to update PhoneSploit-Pro? "
        "Uncommitted local changes may conflict or be lost."
    ):
        return
    console.print("[yellow]Updating PhoneSploit-Pro...[/yellow]")
    console.print("[green]Fetching latest updates from GitHub...[/green]")
    subprocess.run(["git", "fetch"])
    console.print("[green]Applying changes...[/green]")
    subprocess.run(["git", "rebase"])
    console.print("[cyan]Please restart PhoneSploit-Pro.[/cyan]")
    config.run = False


def visit_github(config: AppConfig) -> None:
    subprocess.run([config.opener, "https://github.com/AzeemIdrisi/PhoneSploit-Pro"])
    console.print()


# ---------------------------------------------------------------------------
# Main dispatch loop
# ---------------------------------------------------------------------------

def main(config: AppConfig) -> None:
    from modules import (
        connection, device, app_manager, file_manager,
        media, data_extraction, communication, security, input_control,
    )

    console.print(f"\n [cyan]99: Clear Screen                0: Exit[/cyan]")
    option = console.input(f"\n[red]\\[Main Menu][/red] [white]Enter selection > [/white]").lower()

    match option:
        case "p":
            change_page(config, "p")
        case "n":
            change_page(config, "n")
        case "0":
            config.run = False
            console.print("\n[white]Exiting...[/white]\n")
        case "99":
            clear_screen(config)
        case "1":
            connection.connect(config)
        case "2":
            connection.list_devices(config)
        case "3":
            connection.disconnect(config)
        case "4":
            connection.scan_network(config)
        case "5":
            media.mirror(config)
        case "6":
            media.get_screenshot(config)
        case "7":
            media.screenrecord(config)
        case "8":
            file_manager.pull_file(config)
        case "9":
            file_manager.push_file(config)
        case "10":
            app_manager.launch_app(config)
        case "11":
            app_manager.install_app(config)
        case "12":
            app_manager.uninstall_app(config)
        case "13":
            app_manager.list_apps(config)
        case "14":
            device.get_shell(config)
        case "15":
            security.hack(config)
        case "16":
            file_manager.list_files(config)
        case "17":
            communication.send_sms(config)
        case "18":
            file_manager.copy_whatsapp(config)
        case "19":
            file_manager.copy_screenshots(config)
        case "20":
            file_manager.copy_camera(config)
        case "21":
            media.anonymous_screenshot(config)
        case "22":
            media.anonymous_screenrecord(config)
        case "23":
            communication.open_link(config)
        case "24":
            media.open_photo(config)
        case "25":
            media.open_audio(config)
        case "26":
            media.open_video(config)
        case "27":
            device.get_device_info(config)
        case "28":
            device.battery_info(config)
        case "29":
            device.reboot(config, "system")
        case "30":
            device.reboot(config, "advanced")
        case "31":
            device.unlock_device(config)
        case "32":
            device.lock_device(config)
        case "33":
            data_extraction.dump_sms(config)
        case "34":
            data_extraction.dump_contacts(config)
        case "35":
            data_extraction.dump_call_logs(config)
        case "36":
            app_manager.extract_apk(config)
        case "37":
            connection.stop_adb(config)
        case "38":
            device.power_off(config)
        case "39":
            input_control.use_keycode(config)
        case "40":
            media.stream_audio(config, "mic")
        case "41":
            media.record_audio(config, "mic")
        case "42":
            media.stream_audio(config, "device")
        case "43":
            media.record_audio(config, "device")
        case "44":
            update_me(config)
        case "45":
            visit_github(config)
        case _:
            console.print("\n[red]Invalid selection![/red]\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> None:
    global _selected_banner
    config = AppConfig()
    start(config)

    _selected_banner = _pick_banner()
    clear_screen(config)

    while config.run:
        try:
            main(config)
        except KeyboardInterrupt:
            config.run = False
            console.print("\n[white]Exiting...[/white]\n")
