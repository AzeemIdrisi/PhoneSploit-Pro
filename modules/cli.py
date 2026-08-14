import os
import platform
import random
import shutil
import subprocess
from pathlib import Path

from rich.panel import Panel

from modules import banner, color
from modules.config import AppConfig
from modules.console import console, print_error, set_adb_executable, ask
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


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _collect_missing_tools(config: AppConfig) -> list[tuple[str, str]]:
    """Return list of (display name, installer component key)."""
    missing: list[tuple[str, str]] = []
    if not config.adb_path:
        missing.append(("ADB", "adb"))
    if not config.msfvenom_path or not config.msfconsole_path:
        missing.append(("Metasploit-Framework (msfvenom & msfconsole)", "metasploit"))
    if not config.scrcpy_path:
        missing.append(("Scrcpy", "scrcpy"))
    if not config.nmap_path:
        missing.append(("Nmap", "nmap"))
    return missing


def _run_dependency_installer(config: AppConfig, component_keys: list[str]) -> None:
    """Run install.sh (Unix) or install.ps1 (Windows) for the given component keys."""
    root = _project_root()
    keys = list(dict.fromkeys(component_keys + ["pip"]))
    joined = ",".join(keys)

    if config.operating_system == "Windows":
        ps = shutil.which("pwsh") or shutil.which("powershell") or shutil.which("powershell.exe")
        script = root / "install.ps1"
        if not script.is_file():
            print_error(f"Installer not found: {script}")
            return
        if not ps:
            print_error("PowerShell not found on PATH. Install dependencies manually (see README).")
            return
        subprocess.run(
            [
                ps,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-Components",
                joined,
                "-NonInteractive",
            ],
            cwd=str(root),
        )
    else:
        script = root / "install.sh"
        if not script.is_file():
            print_error(f"Installer not found: {script}")
            return
        subprocess.run(
            ["bash", str(script), "--yes", "--components", joined],
            cwd=str(root),
        )

    console.print(
        "[dim]If tools are still not detected, open a new terminal and run PhoneSploit Pro again "
        "(PATH may need a refresh).[/dim]"
    )


def check_packages(config: AppConfig) -> None:
    while True:
        missing = _collect_missing_tools(config)
        if not missing:
            return

        names = [name for name, _ in missing]
        items = "\n".join(
            f"  [bold yellow]{i + 1}.[/bold yellow] [white]{name}[/white]"
            for i, name in enumerate(names)
        )
        console.print(
            Panel(
                f"[red]The following required tools are NOT installed:[/red]\n\n{items}\n\n"
                "[cyan]Install them manually (see README) or use the automatic installer.[/cyan]",
                title="[bold red]Missing Dependencies[/bold red]",
                border_style="red",
            )
        )

        prompt = (
            "\n[yellow]Press [bold]I[/bold] to install missing tools automatically · "
            "[bold]Y[/bold] continue anyway · [bold]N[/bold] exit[/yellow] > "
        )
        choice = ask(prompt).strip().lower()

        while choice not in ("i", "y", "n", "", "yes", "no"):
            choice = ask("[red]Invalid choice![/red] Press I, Y, or N > ").strip().lower()

        if choice in ("n", "no"):
            raise SystemExit(0)
        if choice in ("i",):
            keys = [k for _, k in missing]
            _run_dependency_installer(config, keys)
            resolve_external_tools(config)
            set_adb_executable(config.adb_path)
            continue
        if choice in ("y", "", "yes"):
            return


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
    elif direction == "n" and config.page_number < 5:
        config.page_number += 1
    clear_screen(config)


# ---------------------------------------------------------------------------
# Main dispatch loop
# ---------------------------------------------------------------------------

def main(config: AppConfig) -> None:
    from modules import (
        connection, device, app_manager, file_manager,
        media, data_extraction, communication, security, input_control,
        extras, port_forward, wifi_utils, root_check, display,
    )

    console.print("[dim]  99:[/dim] Clear   [dim]0:[/dim] Exit")
    option = ask("[red]\\[Main Menu][/red] > ").strip().lower()

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
            if not require_nmap(config):
                return
            connection.scan_network(config)
        case "4":
            if not require_adb(config):
                return
            connection.disconnect(config)
        case "5":
            if not require_adb(config):
                return
            connection.stop_adb(config)
        case "6":
            if not require_adb(config):
                return
            if not require_metasploit(config):
                return
            security.hack(config)
        case "7":
            if not require_scrcpy(config):
                return
            media.mirror(config)
        case "8":
            if not require_adb(config):
                return
            media.get_screenshot(config)
        case "9":
            if not require_adb(config):
                return
            media.screenrecord(config)
        case "10":
            if not require_adb(config):
                return
            media.anonymous_screenshot(config)
        case "11":
            if not require_adb(config):
                return
            media.anonymous_screenrecord(config)
        case "12":
            if not require_scrcpy(config):
                return
            media.camera_live(config)
        case "13":
            if not require_scrcpy(config):
                return
            media.stream_audio(config, "mic")
        case "14":
            if not require_scrcpy(config):
                return
            media.record_audio(config, "mic")
        case "15":
            if not require_scrcpy(config):
                return
            media.stream_audio(config, "device")
        case "16":
            if not require_scrcpy(config):
                return
            media.record_audio(config, "device")
        case "17":
            if not require_adb(config):
                return
            data_extraction.dump_sms(config)
        case "18":
            if not require_adb(config):
                return
            data_extraction.dump_contacts(config)
        case "19":
            if not require_adb(config):
                return
            data_extraction.dump_call_logs(config)
        case "20":
            if not require_adb(config):
                return
            device.get_shell(config)
        case "21":
            if not require_adb(config):
                return
            communication.send_sms(config)
        case "22":
            if not require_adb(config):
                return
            communication.open_link(config)
        case "23":
            if not require_adb(config):
                return
            media.open_photo(config)
        case "24":
            if not require_adb(config):
                return
            media.open_audio(config)
        case "25":
            if not require_adb(config):
                return
            media.open_video(config)
        case "26":
            if not require_adb(config):
                return
            file_manager.pull_file(config)
        case "27":
            if not require_adb(config):
                return
            file_manager.push_file(config)
        case "28":
            if not require_adb(config):
                return
            file_manager.list_files(config)
        case "29":
            if not require_adb(config):
                return
            file_manager.copy_whatsapp(config)
        case "30":
            if not require_adb(config):
                return
            file_manager.copy_screenshots(config)
        case "31":
            if not require_adb(config):
                return
            file_manager.copy_camera(config)
        case "32":
            if not require_adb(config):
                return
            app_manager.install_app(config)
        case "33":
            if not require_adb(config):
                return
            app_manager.uninstall_app(config)
        case "34":
            if not require_adb(config):
                return
            app_manager.launch_app(config)
        case "35":
            if not require_adb(config):
                return
            app_manager.list_apps(config)
        case "36":
            if not require_adb(config):
                return
            extras.install_split_apks(config)
        case "37":
            if not require_adb(config):
                return
            app_manager.extract_apk(config)
        case "38":
            if not require_adb(config):
                return
            extras.force_stop_app(config)
        case "39":
            if not require_adb(config):
                return
            extras.restart_app(config)
        case "40":
            if not require_adb(config):
                return
            extras.clear_app_data(config)
        case "41":
            if not require_adb(config):
                return
            extras.grant_revoke_permission(config)
        case "42":
            if not require_adb(config):
                return
            input_control.use_keycode(config)
        case "43":
            if not require_adb(config):
                return
            device.unlock_device(config)
        case "44":
            if not require_adb(config):
                return
            device.lock_device(config)
        case "45":
            if not require_adb(config):
                return
            device.get_device_info(config)
        case "46":
            if not require_adb(config):
                return
            device.battery_info(config)
        case "47":
            if not require_adb(config):
                return
            device.reboot(config, "system")
        case "48":
            if not require_adb(config):
                return
            device.reboot(config, "advanced")
        case "49":
            if not require_adb(config):
                return
            device.power_off(config)
        case "50":
            if not require_adb(config):
                return
            extras.save_logcat_snippet(config)
        case "51":
            if not require_adb(config):
                return
            extras.live_logcat(config)
        case "52":
            if not require_adb(config):
                return
            extras.network_snapshot(config)
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
            root_check.root_heuristics(config)
        case "57":
            if not require_adb(config):
                return
            wifi_utils.wifi_status_dump(config)
        case "58":
            if not require_adb(config):
                return
            wifi_utils.wlan_ip(config)
        case "59":
            if not require_adb(config):
                return
            wifi_utils.wifi_toggle(config)
        case "60":
            if not require_adb(config):
                return
            wifi_utils.ping_connectivity(config)
        case "61":
            if not require_adb(config):
                return
            wifi_utils.saved_wifi_networks(config)
        case "62":
            if not require_adb(config):
                return
            port_forward.port_forward_menu(config)
        case "63":
            if not require_adb(config):
                return
            display.display_menu(config)
        case "64":
            if not require_adb(config):
                return
            data_extraction.clipboard_menu(config)
        case "65":
            if not require_adb(config):
                return
            data_extraction.get_location(config)
        case "66":
            if not require_adb(config):
                return
            data_extraction.get_identifiers(config)
        case "67":
            if not require_adb(config):
                return
            data_extraction.usage_stats(config)
        case "68":
            if not require_adb(config):
                return
            extras.radio_toggles(config)
        case "69":
            if not require_adb(config):
                return
            device.mock_battery(config)
        case "70":
            if not require_adb(config):
                return
            extras.sound_display(config)
        case "71":
            if not require_adb(config):
                return
            extras.notifications_menu(config)
        case "72":
            if not require_adb(config):
                return
            media.set_wallpaper(config)
        case "73":
            if not require_adb(config):
                return
            wifi_utils.nearby_wifi_scan(config)
        case "74":
            if not require_adb(config):
                return
            wifi_utils.local_hotspot(config)
        case "75":
            if not require_adb(config):
                return
            connection.wireless_menu(config)
        case "76":
            if not require_adb(config):
                return
            app_manager.enable_disable_app(config)
        case "77":
            if not require_adb(config):
                return
            app_manager.suspend_unsuspend_app(config)
        case "78":
            if not require_adb(config):
                return
            app_manager.ignore_battery_optimization(config)
        case "79":
            if not require_adb(config):
                return
            app_manager.set_home_app(config)
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
