"""Serialize this branch's menu into a UI catalog.

`webui` is a CLI launcher and is omitted here — the browser is already the UI.
"""

from __future__ import annotations

from typing import Any

from modules.menu import MAIN_ITEMS, MenuItem

TERMINAL_IDS = frozenset({"metasploit", "shell"})
HOST_PROCESS_IDS = frozenset(
    {
        "camera_live",
        "stream_mic",
        "record_mic",
        "stream_device_audio",
        "record_device_audio",
    }
)
SCREEN_IDS = frozenset({"mirror"})
EXCLUDED_IDS = frozenset({"webui"})

_PKG = {"name": "package", "label": "Package name", "type": "text", "required": True}
_TEXT = {"name": "text", "label": "Text", "type": "text", "required": True}
_ON = {
    "name": "on",
    "label": "State",
    "type": "select",
    "required": True,
    "options": [{"value": "true", "label": "On"}, {"value": "false", "label": "Off"}],
}

FIELDS: dict[str, list[dict[str, Any]]] = {
    "connect": [{"name": "ip", "label": "Device IP", "type": "text", "required": True, "placeholder": "192.168.1.23"}],
    "wireless_pair": [
        {"name": "address", "label": "Pairing address (IP:port)", "type": "text", "required": True},
        {"name": "code", "label": "6-digit pairing code", "type": "text", "required": True},
    ],
    "wireless_connect": [{"name": "address", "label": "Address (IP or IP:port)", "type": "text", "required": True}],
    "wireless_tcpip": [{"name": "port", "label": "Port", "type": "text", "placeholder": "5555"}],
    "keycode_text": [_TEXT],
    "unlock": [{"name": "password", "label": "Password (blank to swipe only)", "type": "text"}],
    "reboot_advanced": [
        {
            "name": "target",
            "label": "Target",
            "type": "select",
            "required": True,
            "options": [
                {"value": "recovery", "label": "Recovery"},
                {"value": "bootloader", "label": "Bootloader"},
                {"value": "fastboot", "label": "Fastboot"},
            ],
        }
    ],
    "send_sms": [
        {"name": "number", "label": "Phone number", "type": "text", "required": True},
        {"name": "message", "label": "Message", "type": "text", "required": True},
    ],
    "open_link": [{"name": "url", "label": "URL", "type": "text", "required": True}],
    "open_photo": [],
    "open_audio": [],
    "open_video": [],
    "set_wallpaper": [],
    "screenshot": [],
    "anon_screenshot": [],
    "screenrecord": [{"name": "seconds", "label": "Duration (seconds)", "type": "number", "required": True}],
    "anon_screenrecord": [{"name": "seconds", "label": "Duration (seconds)", "type": "number", "required": True}],
    "pull_file": [{"name": "path", "label": "Path under /sdcard/", "type": "text", "required": True}],
    "push_file": [{"name": "destination", "label": "Destination under /sdcard/", "type": "text", "placeholder": "Download"}],
    "install_app": [],
    "install_split_apks": [],
    "uninstall_app": [_PKG],
    "launch_app": [_PKG],
    "extract_apk": [_PKG],
    "force_stop_app": [_PKG],
    "restart_app": [_PKG],
    "clear_app_data": [_PKG],
    "disable_app": [_PKG],
    "enable_app": [_PKG],
    "suspend_app": [_PKG],
    "unsuspend_app": [_PKG],
    "grant_revoke": [
        _PKG,
        {"name": "permission", "label": "Permission", "type": "text", "required": True, "placeholder": "android.permission.CAMERA"},
        {
            "name": "grant",
            "label": "Action",
            "type": "select",
            "required": True,
            "options": [{"value": "grant", "label": "Grant"}, {"value": "revoke", "label": "Revoke"}],
        },
    ],
    "battery_whitelist": [_PKG],
    "battery_unwhitelist": [_PKG],
    "set_home_app": [{"name": "component", "label": "Home activity (pkg/activity)", "type": "text", "required": True}],
    "clipboard_set": [_TEXT],
    "mock_battery_set": [{"name": "level", "label": "Level (0-100)", "type": "number", "required": True}],
    "display_resolution": [{"name": "size", "label": "Resolution WxH, or 'reset'", "type": "text", "required": True, "placeholder": "1080x1920"}],
    "display_density": [{"name": "dpi", "label": "DPI, or 'reset'", "type": "text", "required": True, "placeholder": "420"}],
    "display_scaling": [
        {
            "name": "enabled",
            "label": "Scaling",
            "type": "select",
            "required": True,
            "options": [{"value": "1", "label": "Enable"}, {"value": "0", "label": "Disable"}],
        }
    ],
    "sound_volume_set": [{"name": "level", "label": "Media volume (0-15)", "type": "number", "required": True}],
    "sound_brightness": [{"name": "value", "label": "Brightness 0-255 (empty = auto)", "type": "text"}],
    "sound_timeout": [{"name": "seconds", "label": "Timeout (seconds)", "type": "number", "required": True}],
    "sound_dnd": [
        {
            "name": "mode",
            "label": "Mode",
            "type": "select",
            "required": True,
            "options": [
                {"value": "0", "label": "Off"},
                {"value": "1", "label": "Alarms only"},
                {"value": "2", "label": "Priority only"},
                {"value": "3", "label": "Total silence"},
            ],
        }
    ],
    "screen_stay_on": [
        {
            "name": "target",
            "label": "Stay on",
            "type": "select",
            "required": True,
            "options": [
                {"value": "usb", "label": "While USB connected"},
                {"value": "true", "label": "Always"},
                {"value": "false", "label": "Off"},
            ],
        }
    ],
    "notif_post": [
        {"name": "title", "label": "Title", "type": "text", "required": True},
        {"name": "message", "label": "Message", "type": "text", "required": True},
    ],
    "wifi_toggle": [_ON],
    "radio_data": [_ON],
    "radio_bluetooth": [_ON],
    "radio_nfc": [_ON],
    "radio_airplane": [_ON],
    "ping": [{"name": "host", "label": "Host", "type": "text", "placeholder": "8.8.8.8"}],
    "port_forward_add": [
        {"name": "local", "label": "Local TCP port", "type": "number", "required": True},
        {"name": "remote", "label": "Device TCP port", "type": "number", "required": True},
    ],
    "port_forward_reverse": [
        {"name": "device", "label": "Device TCP port", "type": "number", "required": True},
        {"name": "host", "label": "Host TCP port", "type": "number", "required": True},
    ],
    "port_forward_remove": [{"name": "spec", "label": "Rule (e.g. tcp:8080)", "type": "text", "required": True}],
    "usage_stats": [
        {
            "name": "window",
            "label": "Window",
            "type": "select",
            "required": True,
            "options": [
                {"value": "1", "label": "Last 1 day"},
                {"value": "7", "label": "Last 7 days"},
                {"value": "all", "label": "All time"},
            ],
        }
    ],
    "logcat_snippet": [{"name": "lines", "label": "Last N lines", "type": "number", "placeholder": "500"}],
    "developer_settings": [
        {
            "name": "action",
            "label": "Action",
            "type": "select",
            "required": True,
            "options": [
                {"value": "open", "label": "Open Developer Options"},
                {"value": "read", "label": "Read global settings"},
                {"value": "write", "label": "Write a global setting"},
            ],
        },
        {"name": "key", "label": "Key (write only)", "type": "text"},
        {"name": "value", "label": "Value (write only)", "type": "text"},
    ],
    "camera_live": [
        {
            "name": "facing",
            "label": "Camera",
            "type": "select",
            "required": True,
            "options": [{"value": "front", "label": "Front"}, {"value": "back", "label": "Back"}],
        },
        {
            "name": "orientation",
            "label": "Orientation",
            "type": "select",
            "options": [
                {"value": "0", "label": "Normal"},
                {"value": "90", "label": "Rotate 90"},
                {"value": "180", "label": "Rotate 180"},
                {"value": "270", "label": "Rotate 270"},
            ],
        },
    ],
    "metasploit": [
        {"name": "lhost", "label": "LHOST", "type": "text", "required": True},
        {"name": "lport", "label": "LPORT", "type": "number", "required": True, "placeholder": "4444"},
        {
            "name": "reuse",
            "label": "Reuse installed payload",
            "type": "select",
            "options": [{"value": "false", "label": "Build new APK"}, {"value": "true", "label": "Reuse installed"}],
        },
    ],
}

DESTRUCTIVE = frozenset(
    {
        "disconnect",
        "stop_adb",
        "restart_adb",
        "power_off",
        "reboot",
        "reboot_advanced",
        "uninstall_app",
        "clear_app_data",
        "disable_app",
        "wireless_tcpip",
        "wireless_usb",
        "metasploit",
    }
)

HOST_IDS = frozenset(
    {
        "connect",
        "list_devices",
        "disconnect",
        "scan_network",
        "stop_adb",
        "restart_adb",
        "wireless_pair",
        "wireless_connect",
        "wireless_tcpip",
        "wireless_usb",
    }
)


def feature_tier(feature_id: str) -> str:
    if feature_id in TERMINAL_IDS:
        return "terminal"
    if feature_id in HOST_PROCESS_IDS:
        return "host_process"
    if feature_id in SCREEN_IDS:
        return "screen"
    return "native"


def _leaf_dict(item: MenuItem, hub: str | None) -> dict[str, Any]:
    return {
        "id": item.id,
        "label": item.label,
        "hub": hub,
        "requires": item.requires or "adb",
        "tier": feature_tier(item.id),
        "scope": "host" if item.id in HOST_IDS else "device",
        "destructive": item.id in DESTRUCTIVE,
        "fields": FIELDS.get(item.id, []),
    }


def build_catalog() -> dict[str, Any]:
    groups: list[dict[str, Any]] = []
    features: list[dict[str, Any]] = []
    for item in MAIN_ITEMS:
        if item.id in EXCLUDED_IDS:
            continue
        if item.is_hub:
            children = [
                _leaf_dict(child, item.label)
                for child in (item.children or ())
                if child.id not in EXCLUDED_IDS
            ]
            groups.append({"id": item.id, "label": item.label, "features": children})
            features.extend(children)
        else:
            leaf = _leaf_dict(item, None)
            groups.append({"id": item.id, "label": item.label, "features": [leaf]})
            features.append(leaf)
    return {"groups": groups, "features": features}


def feature_ids() -> set[str]:
    return {feature["id"] for feature in build_catalog()["features"]}
