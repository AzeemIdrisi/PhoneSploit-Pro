"""Single-page main menu with specialized one-level hubs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Require = Literal["adb", "scrcpy", "nmap", "metasploit"] | None


@dataclass(frozen=True)
class MenuItem:
    id: str
    label: str
    requires: Require = "adb"
    children: tuple[MenuItem, ...] | None = None
    submenu: bool = False

    @property
    def is_hub(self) -> bool:
        return self.children is not None

    @property
    def display_label(self) -> str:
        if self.is_hub or self.submenu:
            return f"{self.label} ›"
        return self.label


def _leaf(
    id: str,
    label: str,
    requires: Require = "adb",
    *,
    submenu: bool = False,
) -> MenuItem:
    return MenuItem(id=id, label=label, requires=requires, submenu=submenu)


# ---------------------------------------------------------------------------
# Hub definitions
# ---------------------------------------------------------------------------

HUB_CONNECT = MenuItem(
    id="hub_connect",
    label="Device Connection",
    children=(
        _leaf("connect", "Connect a Device"),
        _leaf("list_devices", "List Connected Devices"),
        _leaf("disconnect", "Disconnect All Devices"),
        _leaf("scan_network", "Scan Network for Devices", "nmap"),
    ),
)

HUB_WIRELESS = MenuItem(
    id="hub_wireless",
    label="ADB & Wireless Debugging",
    children=(
        _leaf("wireless_pair", "Pair Device"),
        _leaf("wireless_connect", "Connect Wireless"),
        _leaf("wireless_tcpip", "Enable TCP/IP Mode"),
        _leaf("wireless_usb", "Switch Back to USB Debugging"),
        _leaf("stop_adb", "Stop ADB Server"),
        _leaf("restart_adb", "Restart ADB Server"),
    ),
)


HUB_KEYCODES = MenuItem(
    id="hub_keycodes",
    label="Send Keycode Inputs",
    children=(
        _leaf("keycode_text", "Keyboard Text Input"),
        _leaf("keycode_home", "Home"),
        _leaf("keycode_back", "Back"),
        _leaf("keycode_recent", "Recent Apps"),
        _leaf("keycode_power", "Power Button"),
        _leaf("keycode_dpad_up", "DPAD Up"),
        _leaf("keycode_dpad_down", "DPAD Down"),
        _leaf("keycode_dpad_left", "DPAD Left"),
        _leaf("keycode_dpad_right", "DPAD Right"),
        _leaf("keycode_delete", "Delete / Backspace"),
        _leaf("keycode_enter", "Enter"),
        _leaf("keycode_vol_up", "Volume Up"),
        _leaf("keycode_vol_down", "Volume Down"),
        _leaf("keycode_media_play", "Media Play"),
        _leaf("keycode_media_pause", "Media Pause"),
        _leaf("keycode_tab", "Tab"),
        _leaf("keycode_esc", "Esc"),
    ),
)

HUB_SCREEN_CAPTURE = MenuItem(
    id="hub_screen_capture",
    label="Screen Capture",
    children=(
        _leaf("screenshot", "Take Screenshot"),
        _leaf("screenrecord", "Screen Record"),
        _leaf("anon_screenshot", "Anonymous Screenshot"),
        _leaf("anon_screenrecord", "Anonymous Screen Record"),
    ),
)

HUB_AUDIO = MenuItem(
    id="hub_audio",
    label="Microphone & Device Audio",
    children=(
        _leaf("stream_mic", "Listen Microphone Audio", "scrcpy"),
        _leaf("record_mic", "Record Microphone Audio", "scrcpy"),
        _leaf("stream_device_audio", "Listen Device Audio", "scrcpy"),
        _leaf("record_device_audio", "Record Device Audio", "scrcpy"),
    ),
)

HUB_MEDIA = MenuItem(
    id="hub_media",
    label="Open URL & Media on Device",
    children=(
        _leaf("open_link", "Open URL on Device"),
        _leaf("open_photo", "Display Photo on Device"),
        _leaf("open_audio", "Play Audio file on Device"),
        _leaf("open_video", "Play Video file on Device"),
    ),
)

HUB_PHONE = MenuItem(
    id="hub_phone",
    label="Messages, Calls & Contacts",
    children=(
        _leaf("send_sms", "Send SMS"),
        _leaf("dump_sms", "Dump All SMS"),
        _leaf("dump_contacts", "Dump All Contacts"),
        _leaf("dump_call_logs", "Dump Call Logs"),
    ),
)

HUB_NOTIFICATIONS = MenuItem(
    id="hub_notifications",
    label="Notifications",
    children=(
        _leaf("notif_post", "Post a Notification"),
        _leaf("notif_expand", "Expand Notifications Panel"),
        _leaf("notif_expand_qs", "Expand Quick Settings"),
        _leaf("notif_collapse", "Collapse Panel"),
    ),
)

HUB_DEVICE_POWER = MenuItem(
    id="hub_device_power",
    label="Power, Reboot & Lock",
    children=(
        _leaf("unlock", "Unlock Device"),
        _leaf("lock", "Lock Device"),
        _leaf("reboot", "Restart Device"),
        _leaf("reboot_advanced", "Advanced Reboot Options"),
        _leaf("power_off", "Power Off Device"),
    ),
)

HUB_CLIPBOARD = MenuItem(
    id="hub_clipboard",
    label="Clipboard Control",
    children=(
        _leaf("clipboard_read", "Read Clipboard"),
        _leaf("clipboard_set", "Set Clipboard"),
        _leaf("clipboard_clear", "Clear Clipboard"),
    ),
)


HUB_FILE_TRANSFER = MenuItem(
    id="hub_file_transfer",
    label="File Transfer",
    children=(
        _leaf("list_files", "List All Folders & Files"),
        _leaf("pull_file", "Pull File/Folder from Device"),
        _leaf("push_file", "Send File/Folder to Device"),
    ),
)

HUB_COPY_MEDIA = MenuItem(
    id="hub_copy_media",
    label="Copy Media Files",
    children=(
        _leaf("copy_whatsapp", "Copy WhatsApp Data"),
        _leaf("copy_screenshots", "Copy All Screenshots"),
        _leaf("copy_camera", "Copy All Camera Photos"),
    ),
)

HUB_APP_INSTALL = MenuItem(
    id="hub_app_install",
    label="App Management",
    children=(
        _leaf("list_apps", "List Installed Apps"),
        _leaf("install_app", "Install an App"),
        _leaf("uninstall_app", "Uninstall an App"),
        _leaf("install_split_apks", "Install Split APKs"),
        _leaf("extract_apk", "Extract APK from Installed App"),
        _leaf("launch_app", "Run an App"),
        _leaf("restart_app", "Restart App"),
        _leaf("force_stop_app", "Force Stop App"),
        _leaf("clear_app_data", "Clear App Data"),
        _leaf("usage_stats", "App Usage Statistics"),
    ),
)


HUB_APP_STATES = MenuItem(
    id="hub_app_states",
    label="App State Control",
    children=(
        _leaf("disable_app", "Disable App"),
        _leaf("enable_app", "Enable App"),
        _leaf("suspend_app", "Suspend App"),
        _leaf("unsuspend_app", "Unsuspend App"),
        _leaf("grant_revoke", "Grant/Revoke Permission"),
        _leaf("battery_whitelist", "Whitelist App from Battery Optimization"),
        _leaf("battery_unwhitelist", "Un-whitelist App from Battery Optimization"),
        _leaf("battery_whitelist_show", "Show Battery Whitelist"),
        _leaf("set_home_app", "Set Default Home App"),
        _leaf("show_home_app", "Show Current Home App"),
    ),
)


HUB_DEVICE_INFO = MenuItem(
    id="hub_device_info",
    label="Device Information",
    children=(
        _leaf("device_info", "Get Device Information"),
        _leaf("identifiers", "Get IMEI / Identifiers"),
        _leaf("locale_read", "Read Locale"),
    ),
)

HUB_BATTERY = MenuItem(
    id="hub_battery",
    label="Battery Info & Mocking",
    children=(
        _leaf("battery_info", "Get Battery Information"),
        _leaf("mock_battery_set", "Set Battery Level"),
        _leaf("mock_battery_unplug", "Simulate Unplugged"),
        _leaf("mock_battery_plug", "Simulate Plugged"),
        _leaf("mock_battery_reset", "Reset Battery"),
        _leaf("mock_battery_status", "Show Mock Status"),
    ),
)

HUB_DISPLAY = MenuItem(
    id="hub_display",
    label="Display Resolution & Size",
    children=(
        _leaf("display_view", "View Current Display Settings"),
        _leaf("display_resolution", "Set Resolution"),
        _leaf("display_density", "Set Display Size / Density"),
        _leaf("display_scaling", "Toggle Display Scaling"),
        _leaf("display_reset", "Reset Resolution & Density"),
    ),
)

HUB_SCREEN_BRIGHTNESS = MenuItem(
    id="hub_screen_brightness",
    label="Brightness Controls",
    children=(
        _leaf("sound_brightness", "Set Screen Brightness"),
        _leaf("sound_timeout", "Set Screen Timeout"),
        _leaf("screen_stay_on", "Screen Stay-On"),
    ),
)

HUB_SOUND = MenuItem(
    id="hub_sound",
    label="Sound Controls",
    children=(
        _leaf("sound_volume_show", "Show Media Volume"),
        _leaf("sound_volume_set", "Set Media Volume"),
        _leaf("sound_dnd", "Do Not Disturb Mode"),
    ),
)

HUB_WIFI = MenuItem(
    id="hub_wifi",
    label="Wi-Fi Tools",
    children=(
        _leaf("wifi_toggle", "Wi-Fi Radio Toggle"),
        _leaf("nearby_wifi", "Nearby Wi-Fi Scan"),
        _leaf("saved_wifi", "Saved Wi-Fi Networks"),
        _leaf("wifi_status", "Wi-Fi Status Dump"),
        _leaf("wlan_ip", "WLAN IP Info"),
    ),
)

HUB_HOTSPOT = MenuItem(
    id="hub_hotspot",
    label="Wi-Fi Hotspot",
    children=(
        _leaf("hotspot_start", "Start Local Wi-Fi Hotspot"),
        _leaf("hotspot_stop", "Stop Local Wi-Fi Hotspot"),
    ),
)

HUB_RADIOS = MenuItem(
    id="hub_radios",
    label="Radio Toggles",
    children=(
        _leaf("radio_data", "Mobile Data"),
        _leaf("wifi_toggle", "Wi-Fi"),
        _leaf("radio_bluetooth", "Bluetooth"),
        _leaf("radio_nfc", "NFC"),
        _leaf("radio_airplane", "Airplane Mode"),
    ),
)

HUB_NETWORK_TESTING = MenuItem(
    id="hub_network_testing",
    label="Network Diagnostics",
    children=(
        _leaf("ping", "Ping Connectivity"),
        _leaf("network_snapshot", "Network Snapshot"),
    ),
)

HUB_PORT_FORWARD = MenuItem(
    id="hub_port_forward",
    label="Port Forwarding",
    children=(
        _leaf("port_forward_add", "Forward Port"),
        _leaf("port_forward_reverse", "Reverse Port"),
        _leaf("port_forward_list", "List Rules"),
        _leaf("port_forward_remove", "Remove Rule"),
        _leaf("port_forward_remove_all", "Remove All Rules"),
    ),
)

HUB_DIAGNOSTICS = MenuItem(
    id="hub_diagnostics",
    label="Device Diagnostics",
    children=(
        _leaf("logcat_snippet", "Save Logcat Snippet"),
        _leaf("live_logcat", "Live Logcat Stream"),
        _leaf("root_heuristics", "Root Heuristics"),
    ),
)

# ---------------------------------------------------------------------------
# Single-page main menu
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Ordered top-level entries (hubs + leaves interleaved on the single page)
# ---------------------------------------------------------------------------

MAIN_ITEMS: tuple[MenuItem, ...] = (
    HUB_CONNECT,
    HUB_WIRELESS,
    _leaf("metasploit", "Launch Metasploit Attack", "metasploit"),
    _leaf("mirror", "Mirror & Control Device", "scrcpy"),
    _leaf("camera_live", "Camera Live Stream", "scrcpy"),
    _leaf("shell", "Access Device Shell"),
    HUB_SCREEN_CAPTURE,
    HUB_AUDIO,
    HUB_MEDIA,
    HUB_FILE_TRANSFER,
    HUB_COPY_MEDIA,
    HUB_PHONE,
    HUB_NOTIFICATIONS,
    HUB_DEVICE_POWER,
    HUB_CLIPBOARD,
    HUB_APP_INSTALL,
    HUB_APP_STATES,
    HUB_DEVICE_INFO,
    _leaf("location", "Get Device Location"),
    HUB_BATTERY,
    HUB_DISPLAY,
    HUB_SCREEN_BRIGHTNESS,
    HUB_SOUND,
    HUB_WIFI,
    HUB_HOTSPOT,
    HUB_RADIOS,
    HUB_NETWORK_TESTING,
    HUB_KEYCODES,
    HUB_DIAGNOSTICS,
    HUB_PORT_FORWARD,
    _leaf("developer_settings", "Developer Settings"),
    _leaf("set_wallpaper", "Set Wallpaper"),
)

MAIN_MENU: tuple[MenuItem, ...] = MAIN_ITEMS


def all_menu_items() -> list[MenuItem]:
    """All top-level entries (hubs + leaves) for single-page rendering."""
    return list(MAIN_ITEMS)


def item_by_index(n: int) -> MenuItem | None:
    """Resolve 1-based index to a MenuItem."""
    items = all_menu_items()
    if 1 <= n <= len(items):
        return items[n - 1]
    return None


def total_features() -> int:
    """Count all runnable leaf features across the entire menu."""
    count = 0
    for item in all_menu_items():
        if item.is_hub:
            count += len(item.children)
        else:
            count += 1
    return count
