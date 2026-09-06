import os
import platform
import random
import shutil
import subprocess
from pathlib import Path

from rich.panel import Panel

from modules import banner, color
from modules.config import AppConfig
from modules.menu import MAIN_ITEMS, MenuItem
from modules.console import (
    console,
    print_error,
    set_adb_executable,
    ask,
    render_main_menu,
    render_submenu_screen,
    submenu_prompt,
    parse_submenu_choice,
    clear_terminal,
)
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
        "[bold dim]If tools are still not detected, open a new terminal and run PhoneSploit Pro again "
        "(PATH may need a refresh).[/bold dim]"
    )


def check_packages(config: AppConfig) -> None:
    while True:
        missing = _collect_missing_tools(config)
        if not missing:
            return

        names = [name for name, _ in missing]
        items = "\n".join(
            f"  [bold yellow]{i + 1:>2}.[/bold yellow] [bold white]{name}[/bold white]"
            for i, name in enumerate(names)
        )
        console.print(
            Panel(
                f"[bold red]The following required tools are NOT installed:[/bold red]\n\n{items}\n\n"
                "[bold cyan]Install them manually (see README) or use the automatic installer.[/bold cyan]",
                title="[bold red]Missing Dependencies[/bold red]",
                border_style="bold red",
            )
        )

        prompt = (
            "\n[bold yellow]Press [bold]I[/bold] to install missing tools automatically · "
            "[bold]Y[/bold] continue anyway · [bold]N[/bold] exit[/bold yellow] > "
        )
        choice = ask(prompt).strip().lower()

        while choice not in ("i", "y", "n", "", "yes", "no"):
            choice = ask("[bold red]Invalid choice![/bold red] Press I, Y, or N > ").strip().lower()

        os.system(config.clear_cmd)

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
    return f"[{c}]{random.choice(banner.banner_list)}[/{c}]"


def display_menu(config: AppConfig) -> None:
    global _selected_banner
    console.print(_selected_banner)
    console.print()
    entries: list[tuple[int, str]] = [
        (i + 1, item.display_label) for i, item in enumerate(all_menu_items())
    ]
    render_main_menu(entries)


def all_menu_items() -> list[MenuItem]:
    return list(MAIN_ITEMS)


def clear_screen(config: AppConfig) -> None:
    os.system(config.clear_cmd)
    display_menu(config)


# ---------------------------------------------------------------------------
# Feature handlers registry
# ---------------------------------------------------------------------------

def _build_handlers() -> dict[str, object]:
    from modules import (
        app_manager,
        communication,
        connection,
        data_extraction,
        device,
        display,
        extras,
        file_manager,
        input_control,
        media,
        port_forward,
        root_check,
        security,
        wifi_utils,
    )

    return {
        "connect": connection.connect,
        "list_devices": connection.list_devices,
        "scan_network": connection.scan_network,
        "disconnect": connection.disconnect,
        "stop_adb": connection.stop_adb,
        "restart_adb": connection.restart_adb,
        "metasploit": security.hack,
        "mirror": media.mirror,
        "shell": device.get_shell,
        "send_sms": communication.send_sms,
        "open_link": communication.open_link,
        "wireless_pair": lambda c: connection.wireless_pair(),
        "wireless_connect": connection.wireless_connect,
        "wireless_tcpip": lambda c: connection.wireless_tcpip(),
        "wireless_usb": lambda c: connection.wireless_usb(),
        "screenshot": media.get_screenshot,
        "screenrecord": media.screenrecord,
        "anon_screenshot": media.anonymous_screenshot,
        "anon_screenrecord": media.anonymous_screenrecord,
        "camera_live": media.camera_live,
        "stream_mic": lambda c: media.stream_audio(c, "mic"),
        "record_mic": lambda c: media.record_audio(c, "mic"),
        "stream_device_audio": lambda c: media.stream_audio(c, "device"),
        "record_device_audio": lambda c: media.record_audio(c, "device"),
        "open_photo": media.open_photo,
        "open_audio": media.open_audio,
        "open_video": media.open_video,
        "set_wallpaper": media.set_wallpaper,
        "keycode_text": input_control.keycode_text,
        "keycode_home": lambda c: input_control.keycode(c, "3", "Home"),
        "keycode_back": lambda c: input_control.keycode(c, "4", "Back"),
        "keycode_recent": lambda c: input_control.keycode(c, "187", "Recent apps"),
        "keycode_power": lambda c: input_control.keycode(c, "26", "Power"),
        "keycode_dpad_up": lambda c: input_control.keycode(c, "19", "DPAD up"),
        "keycode_dpad_down": lambda c: input_control.keycode(c, "20", "DPAD down"),
        "keycode_dpad_left": lambda c: input_control.keycode(c, "21", "DPAD left"),
        "keycode_dpad_right": lambda c: input_control.keycode(c, "22", "DPAD right"),
        "keycode_delete": lambda c: input_control.keycode(c, "67", "Delete"),
        "keycode_enter": lambda c: input_control.keycode(c, "66", "Enter"),
        "keycode_vol_up": lambda c: input_control.keycode(c, "24", "Volume up"),
        "keycode_vol_down": lambda c: input_control.keycode(c, "25", "Volume down"),
        "keycode_media_play": lambda c: input_control.keycode(c, "126", "Media play"),
        "keycode_media_pause": lambda c: input_control.keycode(c, "127", "Media pause"),
        "keycode_tab": lambda c: input_control.keycode(c, "61", "Tab"),
        "keycode_esc": lambda c: input_control.keycode(c, "111", "Esc"),
        "unlock": device.unlock_device,
        "lock": device.lock_device,
        "reboot": lambda c: device.reboot(c, "system"),
        "reboot_advanced": lambda c: device.reboot(c, "advanced"),
        "power_off": device.power_off,
        "screen_stay_on": extras.screen_stay_on,
        "device_info": device.get_device_info,
        "battery_info": device.battery_info,
        "dump_sms": data_extraction.dump_sms,
        "dump_contacts": data_extraction.dump_contacts,
        "dump_call_logs": data_extraction.dump_call_logs,
        "clipboard_read": data_extraction.clipboard_read,
        "clipboard_set": data_extraction.clipboard_set,
        "clipboard_clear": data_extraction.clipboard_clear,
        "location": data_extraction.get_location,
        "identifiers": data_extraction.get_identifiers,
        "pull_file": file_manager.pull_file,
        "push_file": file_manager.push_file,
        "list_files": file_manager.list_files,
        "copy_whatsapp": file_manager.copy_whatsapp,
        "copy_screenshots": file_manager.copy_screenshots,
        "copy_camera": file_manager.copy_camera,
        "install_app": app_manager.install_app,
        "uninstall_app": app_manager.uninstall_app,
        "launch_app": app_manager.launch_app,
        "list_apps": app_manager.list_apps,
        "install_split_apks": extras.install_split_apks,
        "extract_apk": app_manager.extract_apk,
        "force_stop_app": extras.force_stop_app,
        "restart_app": extras.restart_app,
        "clear_app_data": extras.clear_app_data,
        "grant_revoke": extras.grant_revoke_permission,
        "usage_stats": data_extraction.usage_stats,
        "disable_app": app_manager.disable_app,
        "enable_app": app_manager.enable_app,
        "suspend_app": app_manager.suspend_app,
        "unsuspend_app": app_manager.unsuspend_app,
        "battery_whitelist": app_manager.battery_whitelist,
        "battery_unwhitelist": app_manager.battery_unwhitelist,
        "battery_whitelist_show": app_manager.battery_whitelist_show,
        "set_home_app": app_manager.set_home_app,
        "show_home_app": app_manager.show_home_app,
        "developer_settings": extras.developer_settings,
        "locale_read": extras.locale_read,
        "mock_battery_set": device.mock_battery_set,
        "mock_battery_unplug": device.mock_battery_unplug,
        "mock_battery_plug": device.mock_battery_plug,
        "mock_battery_reset": device.mock_battery_reset,
        "mock_battery_status": device.mock_battery_status,
        "display_view": display.show_current_settings,
        "display_resolution": display.set_resolution,
        "display_density": display.set_density,
        "display_scaling": display.toggle_scaling,
        "display_reset": display.reset_all,
        "sound_volume_show": extras.sound_volume_show,
        "sound_volume_set": extras.sound_volume_set,
        "sound_brightness": extras.sound_brightness,
        "sound_timeout": extras.sound_timeout,
        "sound_dnd": extras.sound_dnd,
        "notif_post": extras.notif_post,
        "notif_expand": extras.notif_expand,
        "notif_expand_qs": extras.notif_expand_qs,
        "notif_collapse": extras.notif_collapse,
        "wifi_status": wifi_utils.wifi_status_dump,
        "wlan_ip": wifi_utils.wlan_ip,
        "wifi_toggle": wifi_utils.wifi_toggle,
        "ping": wifi_utils.ping_connectivity,
        "saved_wifi": wifi_utils.saved_wifi_networks,
        "nearby_wifi": wifi_utils.nearby_wifi_scan,
        "hotspot_start": wifi_utils.hotspot_start,
        "hotspot_stop": wifi_utils.hotspot_stop,
        "radio_data": extras.radio_data,
        "radio_bluetooth": extras.radio_bluetooth,
        "radio_nfc": extras.radio_nfc,
        "radio_airplane": extras.radio_airplane,
        "port_forward_add": port_forward.port_forward_add,
        "port_forward_reverse": port_forward.port_forward_reverse,
        "port_forward_list": port_forward.port_forward_list,
        "port_forward_remove": port_forward.port_forward_remove,
        "port_forward_remove_all": port_forward.port_forward_remove_all,
        "logcat_snippet": extras.save_logcat_snippet,
        "live_logcat": extras.live_logcat,
        "network_snapshot": extras.network_snapshot,
        "root_heuristics": root_check.root_heuristics,
    }


_HANDLERS: dict[str, object] | None = None


def _handlers() -> dict[str, object]:
    global _HANDLERS
    if _HANDLERS is None:
        _HANDLERS = _build_handlers()
    return _HANDLERS


def _check_require(require: str | None, config: AppConfig) -> bool:
    if require is None or require == "adb":
        return require_adb(config)
    if require == "scrcpy":
        return require_scrcpy(config)
    if require == "nmap":
        return require_nmap(config)
    if require == "metasploit":
        if not require_adb(config):
            return False
        return require_metasploit(config)
    return True


def _run_handler(config: AppConfig, item: MenuItem) -> None:
    handler = _handlers().get(item.id)
    if handler is None:
        print_error(f"No handler registered for '{item.id}'.")
        return
    handler(config)  # type: ignore[operator]


def run_hub(config: AppConfig, hub: MenuItem, breadcrumb: list[str]) -> bool:
    """Interactive hub submenu loop. Returns True when a handler asked to pop
    all the way back to the main menu (the caller renders it without
    clearing so the handler's message stays visible)."""
    assert hub.children is not None
    labels = [child.display_label for child in hub.children]
    crumbs = breadcrumb + [hub.label]
    columns = 2 if len(labels) > 6 else 1

    def _render(*, clear: bool = False) -> None:
        if clear:
            clear_terminal(config)
        render_submenu_screen(hub.label, labels, breadcrumb=crumbs, columns=columns)

    _render(clear=True)
    prompt = submenu_prompt(crumbs)
    while True:
        choice = ask(prompt).strip().lower()
        action = parse_submenu_choice(choice, config, lambda: _render())
        if action == "exit":
            return False
        if action == "redraw":
            continue
        if not choice.isdigit():
            print_error("Invalid selection")
            continue
        idx = int(choice)
        if idx < 1 or idx > len(hub.children):
            print_error("Invalid selection")
            continue
        child = hub.children[idx - 1]
        if child.is_hub:
            if run_hub(config, child, crumbs):
                return True
            _render(clear=True)
            continue
        if not _check_require(child.requires, config):
            continue
        _run_handler(config, child)
        if config.return_to_main:
            config.return_to_main = False
            return True
        console.print()
        _render()


def _dispatch_item(config: AppConfig, item: MenuItem) -> None:
    if item.is_hub:
        if run_hub(config, item, ["Main Menu"]):
            display_menu(config)
        else:
            clear_screen(config)
        return
    if not _check_require(item.requires, config):
        return
    _run_handler(config, item)
    config.return_to_main = False
    # Always re-render (without clearing) so the handler's output stays
    # visible and the menu is on screen for the next prompt.
    display_menu(config)


# ---------------------------------------------------------------------------
# Main dispatch loop
# ---------------------------------------------------------------------------

def main(config: AppConfig) -> None:
    option = ask("[bold red]\\[Main Menu][/bold red] > ").strip().lower()

    if option == "0":
        config.run = False
        console.print("\n[bold white]Exiting...[/bold white]\n")
        return
    if option == "99":
        clear_screen(config)
        return
    if not option.isdigit():
        print_error("Invalid selection")
        return

    item = None
    try:
        item = all_menu_items()[int(option) - 1]
    except (ValueError, IndexError):
        pass
    if item is None:
        print_error("Invalid selection")
        return
    _dispatch_item(config, item)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run() -> None:
    global _selected_banner
    from modules import connection

    config = AppConfig()
    os.system("cls" if platform.system() == "Windows" else "clear")
    start(config)

    _selected_banner = _pick_banner()
    connection.prompt_select_device_if_multiple(config)
    clear_screen(config)

    while config.run:
        try:
            main(config)
        except KeyboardInterrupt:
            config.run = False
            console.print("\n[bold white]Exiting...[/bold white]\n")