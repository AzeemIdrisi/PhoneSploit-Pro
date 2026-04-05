import os
import platform
import random
import subprocess
from pathlib import Path

from rich.panel import Panel

from modules import banner, color
from modules.config import AppConfig
from modules.console import console, confirm, set_adb_executable
from modules.tools import (
    resolve_external_tools,
    require_adb,
    require_metasploit,
    require_nmap,
    require_scrcpy,
)


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


def check_packages(config: AppConfig) -> None:
    missing: list[str] = []
    if not config.adb_path:
        missing.append("ADB")
    if not config.msfvenom_path or not config.msfconsole_path:
        missing.append("Metasploit-Framework (msfvenom & msfconsole)")
    if not config.scrcpy_path:
        missing.append("Scrcpy")
    if not config.nmap_path:
        missing.append("Nmap")

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
    resolve_external_tools(config)
    set_adb_executable(config.adb_path)
    check_packages(config)


# ---------------------------------------------------------------------------
# Menu display
# ---------------------------------------------------------------------------

_selected_banner: str = ""


def _pick_banner() -> str:
    c = random.choice(color.color_list)
    return f"[bold {c}]{random.choice(banner.banner_list)}[/bold {c}]"


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
    elif direction == "n" and config.page_number < 4:
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


# ---------------------------------------------------------------------------
# Main dispatch loop
# ---------------------------------------------------------------------------

def main(config: AppConfig) -> None:
    from modules import (
        connection, device, app_manager, file_manager,
        media, data_extraction, communication, security, input_control,
        extras, port_forward, wifi_utils, root_check,
    )

    console.print("[dim]  99:[/dim] Clear   [dim]0:[/dim] Exit")
    console.print("[red]\\[Main Menu][/red] > ", end="")
    option = input().strip().lower()

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
            if not require_adb(config):
                return
            connection.connect(config)
        case "2":
            if not require_adb(config):
                return
            connection.list_devices(config)
        case "3":
            if not require_adb(config):
                return
            connection.disconnect(config)
        case "4":
            if not require_nmap(config):
                return
            connection.scan_network(config)
        case "5":
            if not require_scrcpy(config):
                return
            media.mirror(config)
        case "6":
            if not require_adb(config):
                return
            media.get_screenshot(config)
        case "7":
            if not require_adb(config):
                return
            media.screenrecord(config)
        case "8":
            if not require_adb(config):
                return
            file_manager.pull_file(config)
        case "9":
            if not require_adb(config):
                return
            file_manager.push_file(config)
        case "10":
            if not require_adb(config):
                return
            app_manager.launch_app(config)
        case "11":
            if not require_adb(config):
                return
            app_manager.install_app(config)
        case "12":
            if not require_adb(config):
                return
            app_manager.uninstall_app(config)
        case "13":
            if not require_adb(config):
                return
            app_manager.list_apps(config)
        case "14":
            if not require_adb(config):
                return
            device.get_shell(config)
        case "15":
            if not require_adb(config):
                return
            if not require_metasploit(config):
                return
            security.hack(config)
        case "16":
            if not require_adb(config):
                return
            file_manager.list_files(config)
        case "17":
            if not require_adb(config):
                return
            communication.send_sms(config)
        case "18":
            if not require_adb(config):
                return
            file_manager.copy_whatsapp(config)
        case "19":
            if not require_adb(config):
                return
            file_manager.copy_screenshots(config)
        case "20":
            if not require_adb(config):
                return
            file_manager.copy_camera(config)
        case "21":
            if not require_adb(config):
                return
            media.anonymous_screenshot(config)
        case "22":
            if not require_adb(config):
                return
            media.anonymous_screenrecord(config)
        case "23":
            if not require_adb(config):
                return
            communication.open_link(config)
        case "24":
            if not require_adb(config):
                return
            media.open_photo(config)
        case "25":
            if not require_adb(config):
                return
            media.open_audio(config)
        case "26":
            if not require_adb(config):
                return
            media.open_video(config)
        case "27":
            if not require_adb(config):
                return
            device.get_device_info(config)
        case "28":
            if not require_adb(config):
                return
            device.battery_info(config)
        case "29":
            if not require_adb(config):
                return
            device.reboot(config, "system")
        case "30":
            if not require_adb(config):
                return
            device.reboot(config, "advanced")
        case "31":
            if not require_adb(config):
                return
            device.unlock_device(config)
        case "32":
            if not require_adb(config):
                return
            device.lock_device(config)
        case "33":
            if not require_adb(config):
                return
            data_extraction.dump_sms(config)
        case "34":
            if not require_adb(config):
                return
            data_extraction.dump_contacts(config)
        case "35":
            if not require_adb(config):
                return
            data_extraction.dump_call_logs(config)
        case "36":
            if not require_adb(config):
                return
            app_manager.extract_apk(config)
        case "37":
            if not require_adb(config):
                return
            connection.stop_adb(config)
        case "38":
            if not require_adb(config):
                return
            device.power_off(config)
        case "39":
            if not require_adb(config):
                return
            input_control.use_keycode(config)
        case "40":
            if not require_scrcpy(config):
                return
            media.stream_audio(config, "mic")
        case "41":
            if not require_scrcpy(config):
                return
            media.record_audio(config, "mic")
        case "42":
            if not require_scrcpy(config):
                return
            media.stream_audio(config, "device")
        case "43":
            if not require_scrcpy(config):
                return
            media.record_audio(config, "device")
        case "44":
            if not require_adb(config):
                return
            port_forward.port_forward_menu(config)
        case "45":
            if not require_adb(config):
                return
            extras.force_stop_app(config)
        case "46":
            if not require_adb(config):
                return
            extras.clear_app_data(config)
        case "47":
            if not require_adb(config):
                return
            extras.save_logcat_snippet(config)
        case "48":
            if not require_adb(config):
                return
            extras.grant_revoke_permission(config)
        case "49":
            if not require_adb(config):
                return
            extras.restart_app(config)
        case "50":
            if not require_adb(config):
                return
            extras.live_logcat(config)
        case "51":
            if not require_adb(config):
                return
            extras.network_snapshot(config)
        case "52":
            if not require_adb(config):
                return
            extras.install_split_apks(config)
        case "53":
            if not require_adb(config):
                return
            extras.developer_settings(config)
        case "54":
            if not require_adb(config):
                return
            extras.locale_read(config)
        case "55":
            if not require_adb(config):
                return
            extras.screen_stay_on(config)
        case "56":
            if not require_adb(config):
                return
            wifi_utils.wifi_status_dump(config)
        case "57":
            if not require_adb(config):
                return
            wifi_utils.wlan_ip(config)
        case "58":
            if not require_adb(config):
                return
            wifi_utils.wifi_toggle(config)
        case "59":
            if not require_adb(config):
                return
            wifi_utils.ping_connectivity(config)
        case "60":
            if not require_adb(config):
                return
            wifi_utils.saved_wifi_networks(config)
        case "61":
            if not require_adb(config):
                return
            root_check.root_heuristics(config)
        case "62":
            update_me(config)
        case _:
            console.print("\n[red]Invalid selection![/red]\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> None:
    global _selected_banner
    from modules import connection

    config = AppConfig()
    start(config)

    _selected_banner = _pick_banner()
    connection.prompt_select_device_if_multiple(config)
    clear_screen(config)

    while config.run:
        try:
            main(config)
        except KeyboardInterrupt:
            config.run = False
            console.print("\n[white]Exiting...[/white]\n")
