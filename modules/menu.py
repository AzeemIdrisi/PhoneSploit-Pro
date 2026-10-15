"""Single-page main menu with specialized one-level hubs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Require = (
    Literal[
        "adb",
        "scrcpy",
        "nmap",
        "metasploit",
        "hardax",
        "lockknife",
        "drozer",
        "frida",
        "objection",
        "aleapp",
        "mobsf",
        "none",
    ]
    | None
)


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
        _leaf("device_accounts", "Accounts on Device"),
        _leaf("device_sim", "SIM / Operator Info"),
        _leaf("device_bluetooth", "Bluetooth Devices"),
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

HUB_VULNERABILITY = MenuItem(
    id="hub_vulnerability",
    label="Vulnerability Analysis",
    children=(
        _leaf("vuln_full_audit", "Full Device Audit", "hardax"),
        _leaf("vuln_patch_cve", "Security Patch & CVE Exposure", "hardax"),
        _leaf("vuln_hardening", "Hardening & Config Checks", "hardax"),
        _leaf("vuln_app_surface", "App Attack Surface", "hardax"),
        _leaf("vuln_export_report", "Export Last Report", "none"),
    ),
)

HUB_LOCKKNIFE = MenuItem(
    id="hub_lockknife",
    label="Investigate with LockKnife",
    children=(
        _leaf("lk_case", "Case workspace", "lockknife", submenu=True),
        _leaf("lk_crack", "Crack (PIN, password, gesture)", "lockknife", submenu=True),
        _leaf("lk_extract", "Extract extras (browser, messaging)", "lockknife", submenu=True),
        _leaf("lk_forensics", "Forensics & timeline", "lockknife", submenu=True),
        _leaf("lk_apk", "APK quick scan", "lockknife", submenu=True),
        _leaf("lk_report", "Forensic reports", "lockknife", submenu=True),
        _leaf("lk_security", "Security, network, wallet", "lockknife", submenu=True),
        _leaf("lk_usb", "USB exploit (official CLI)", "lockknife", submenu=True),
        _leaf("lk_interactive", "LockKnife interactive TUI", "lockknife"),
    ),
)

HUB_DROZER = MenuItem(
    id="hub_drozer",
    label="Assess IPC with drozer",
    children=(
        _leaf("dz_setup", "Install agent & start server", "drozer"),
        _leaf("dz_assess", "Assessment modules", "drozer", submenu=True),
        _leaf("dz_deploy", "Deploy / exploit builder", "drozer", submenu=True),
    ),
)

HUB_FRIDA = MenuItem(
    id="hub_frida",
    label="Instrument Apps with Frida",
    children=(
        _leaf("fr_setup", "Setup (frida-server / patchapk)", "frida", submenu=True),
        _leaf("fr_actions", "Runtime actions (objection)", "objection", submenu=True),
    ),
)

HUB_SHIZUKU = MenuItem(
    id="hub_shizuku",
    label="Elevate Access with Shizuku",
    children=(
        _leaf("sh_install", "Install Shizuku APK", "adb"),
        _leaf("sh_start", "Start via start.sh", "adb"),
        _leaf("sh_status", "Status", "adb"),
        _leaf("sh_stop", "Stop Shizuku app", "adb"),
        _leaf("sh_launch_app", "Open Shizuku app", "adb"),
        _leaf("sh_list_clients", "List Shizuku clients", "adb"),
        _leaf("sh_launch_client", "Launch package", "adb"),
        _leaf("sh_uninstall", "Uninstall Shizuku", "adb"),
    ),
)

HUB_ALEAPP = MenuItem(
    id="hub_aleapp",
    label="Parse Dumps with ALEAPP",
    children=(
        _leaf("al_parse", "Parse dump (official aleapp.py)", "aleapp"),
        _leaf("al_acquire_fs", "Acquire rooted fs paths (adb pull)", "adb"),
        _leaf("al_acquire_tar", "Acquire rooted tar (adb + parse)", "adb"),
        _leaf("al_acquire_backup", "Acquire adb backup", "adb"),
        _leaf("al_open_last", "Open last HTML report", "none"),
    ),
)

HUB_MOBSF = MenuItem(
    id="hub_mobsf",
    label="Static Scan with MobSF",
    children=(
        _leaf("mf_scan", "Upload & scan APK (REST)", "mobsf"),
        _leaf("mf_rescan", "Re-scan existing hash", "mobsf"),
        _leaf("mf_recent_scans", "List recent scans", "mobsf"),
        _leaf("mf_search", "Search scans", "mobsf"),
        _leaf("mf_tasks", "Scan queue / tasks", "mobsf"),
        _leaf("mf_scan_logs", "Live scan logs", "mobsf"),
        _leaf("mf_view_source", "View decompiled source", "mobsf"),
        _leaf("mf_compare", "Compare two scans", "mobsf"),
        _leaf("mf_open_report", "Open static report in browser", "mobsf"),
        _leaf("mf_delete_scan", "Delete scan", "mobsf"),
        _leaf("mf_open_ui", "Open MobSF web UI", "mobsf"),
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
    HUB_VULNERABILITY,
    HUB_PORT_FORWARD,
    _leaf("developer_settings", "Developer Settings"),
    _leaf("set_wallpaper", "Set Wallpaper"),
    HUB_LOCKKNIFE,
    HUB_DROZER,
    HUB_FRIDA,
    HUB_SHIZUKU,
    HUB_ALEAPP,
    HUB_MOBSF,
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


@dataclass(frozen=True)
class MenuSearchHit:
    """A menu entry matched by search, with its breadcrumb path."""

    item: MenuItem
    path: str


def _collect_search_hits(
    item: MenuItem,
    path_parts: list[str],
    query: str,
    hits: list[MenuSearchHit],
) -> None:
    label = item.label.lower()
    if query in label:
        hits.append(MenuSearchHit(item=item, path=" › ".join(path_parts)))
    if item.is_hub and item.children:
        child_path = path_parts + [item.label]
        for child in item.children:
            _collect_search_hits(child, child_path, query, hits)


def search_menu_items(
    query: str,
    *,
    max_results: int = 20,
) -> tuple[list[MenuSearchHit], int]:
    """Case-insensitive substring search over top-level items and hub leaves."""
    q = query.strip().lower()
    if not q:
        return [], 0
    hits: list[MenuSearchHit] = []
    for top in MAIN_ITEMS:
        if top.is_hub:
            hub_path = [top.label]
            if q in top.label.lower():
                hits.append(MenuSearchHit(item=top, path=top.label))
            for child in top.children or ():
                _collect_search_hits(child, hub_path, q, hits)
        else:
            if q in top.label.lower():
                hits.append(MenuSearchHit(item=top, path=top.label))
    total = len(hits)
    return hits[:max_results], total
