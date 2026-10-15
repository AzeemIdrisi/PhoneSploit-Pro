"""Map catalog feature ids to operations."""

from __future__ import annotations

from typing import Any, Callable

from modules.input_control import KEYCODE_MAP
from modules.services import operations as ops
from modules.services.catalog import HOST_IDS, feature_ids
from modules.services.runner import AdbError
from modules.vulnerability import HARDENING_CATEGORIES

Handler = Callable[..., dict[str, Any]]


def _device(fn: Callable[..., dict[str, Any]]) -> Handler:
    def wrapped(serial: str, params: dict[str, Any], config: Any) -> dict[str, Any]:
        return fn(serial)

    return wrapped


def _params(fn: Callable[..., dict[str, Any]]) -> Handler:
    def wrapped(serial: str, params: dict[str, Any], config: Any) -> dict[str, Any]:
        return fn(serial, params)

    return wrapped


def _host(fn: Callable[..., dict[str, Any]], *, takes_params: bool = False, takes_config: bool = False) -> Handler:
    def wrapped(serial: str, params: dict[str, Any], config: Any) -> dict[str, Any]:
        if takes_config and takes_params:
            return fn(config, params)
        if takes_config:
            return fn(config)
        if takes_params:
            return fn(params)
        return fn()

    return wrapped


def _handlers() -> dict[str, Handler]:
    mapping: dict[str, Handler] = {
        "connect": _host(ops.connect_device, takes_params=True),
        "list_devices": _host(ops.list_devices),
        "disconnect": _host(ops.disconnect_all),
        "scan_network": _host(ops.scan_network, takes_config=True),
        "stop_adb": _host(ops.stop_adb),
        "restart_adb": _host(ops.restart_adb),
        "wireless_pair": _host(ops.wireless_pair, takes_params=True),
        "wireless_connect": _host(ops.wireless_connect, takes_params=True),
        "wireless_tcpip": _host(ops.wireless_tcpip, takes_params=True),
        "wireless_usb": _host(ops.wireless_usb),
        "device_info": _device(ops.device_info),
        "battery_info": _device(ops.battery_info),
        "device_accounts": _device(ops.accounts),
        "device_sim": _device(ops.sim_info),
        "device_bluetooth": _device(ops.bluetooth),
        "locale_read": _device(ops.locale_read),
        "location": _device(ops.location),
        "root_heuristics": _device(ops.root_heuristics),
        "unlock": _params(ops.unlock),
        "lock": _device(ops.lock),
        "reboot": _device(lambda serial: ops.reboot(serial)),
        "reboot_advanced": _params(lambda serial, params: ops.reboot(serial, str(params.get("target") or ""))),
        "power_off": _device(ops.power_off),
        "keycode_text": _params(ops.key_text),
        "screen_stay_on": _params(ops.stay_on),
        "display_view": _device(ops.display_view),
        "display_resolution": _params(ops.display_resolution),
        "display_density": _params(ops.display_density),
        "display_scaling": _params(ops.display_scaling),
        "display_reset": _device(ops.display_reset),
        "sound_volume_show": _device(ops.volume_show),
        "sound_volume_set": _params(ops.volume_set),
        "sound_brightness": _params(ops.brightness),
        "sound_timeout": _params(ops.screen_timeout),
        "sound_dnd": _params(ops.dnd),
        "notif_post": _params(ops.notif_post),
        "notif_expand": _device(lambda serial: ops.statusbar(serial, "expand-notifications")),
        "notif_expand_qs": _device(lambda serial: ops.statusbar(serial, "expand-settings")),
        "notif_collapse": _device(lambda serial: ops.statusbar(serial, "collapse")),
        "mock_battery_set": _params(ops.mock_level),
        "mock_battery_unplug": _device(ops.mock_unplug),
        "mock_battery_plug": _device(ops.mock_plug),
        "mock_battery_reset": _device(ops.mock_reset),
        "mock_battery_status": _device(ops.battery_info),
        "open_link": _params(ops.open_url),
        "send_sms": _params(ops.send_sms),
        "developer_settings": _params(ops.developer),
        "list_apps": _params(
            lambda serial, params: ops.list_apps(serial, str(params.get("thirdParty") or "").lower() in ("1", "true"))
        ),
        "uninstall_app": _params(ops.uninstall_app),
        "launch_app": _params(ops.launch_app),
        "extract_apk": _params(ops.extract_apk),
        "force_stop_app": _params(ops.force_stop),
        "restart_app": _params(ops.restart_app),
        "clear_app_data": _params(ops.clear_app),
        "disable_app": _params(lambda serial, params: ops.pm_state(serial, ops._pkg(params), "disable-user", "--user", "0")),
        "enable_app": _params(lambda serial, params: ops.pm_state(serial, ops._pkg(params), "enable")),
        "suspend_app": _params(lambda serial, params: ops.pm_state(serial, ops._pkg(params), "suspend", "--user", "0")),
        "unsuspend_app": _params(lambda serial, params: ops.pm_state(serial, ops._pkg(params), "unsuspend", "--user", "0")),
        "grant_revoke": _params(ops.grant_revoke),
        "battery_whitelist_show": _device(ops.battery_whitelist_show),
        "battery_whitelist": _params(lambda serial, params: ops.battery_whitelist(serial, params, True)),
        "battery_unwhitelist": _params(lambda serial, params: ops.battery_whitelist(serial, params, False)),
        "show_home_app": _device(ops.show_home),
        "set_home_app": _params(ops.set_home),
        "list_files": _params(lambda serial, params: ops.list_files(serial, str(params.get("path") or "/sdcard"))),
        "pull_file": _params(lambda serial, params: ops.pull_path(serial, "/sdcard/" + str(params.get("path") or "").lstrip("/"))),
        "dump_sms": _device(ops.dump_sms),
        "dump_contacts": _device(ops.dump_contacts),
        "dump_call_logs": _device(ops.dump_calls),
        "usage_stats": _params(ops.usage),
        "clipboard_read": _device(ops.clipboard_read),
        "clipboard_set": _params(lambda serial, params: ops.clipboard_set(serial, str(params.get("text") or ""))),
        "clipboard_clear": _device(lambda serial: ops.clipboard_set(serial, "")),
        "wifi_status": _device(ops.wifi_status),
        "wlan_ip": _device(ops.wlan_ip),
        "saved_wifi": _device(ops.saved_wifi),
        "nearby_wifi": _device(ops.nearby_wifi),
        "wifi_toggle": _params(lambda serial, params: ops._radio(serial, "wifi", ops._bool_param(params.get("on")))),
        "radio_data": _params(lambda serial, params: ops._radio(serial, "data", ops._bool_param(params.get("on")))),
        "radio_bluetooth": _params(lambda serial, params: ops._radio(serial, "bluetooth", ops._bool_param(params.get("on")))),
        "radio_nfc": _params(lambda serial, params: ops._radio(serial, "nfc", ops._bool_param(params.get("on")))),
        "radio_airplane": _params(lambda serial, params: ops._radio(serial, "airplane", ops._bool_param(params.get("on")))),
        "hotspot_start": _device(lambda serial: ops.hotspot(serial, True)),
        "hotspot_stop": _device(lambda serial: ops.hotspot(serial, False)),
        "ping": _params(ops.ping),
        "network_snapshot": _device(ops.network_snapshot),
        "port_forward_add": _params(ops.port_add),
        "port_forward_reverse": _params(ops.port_reverse),
        "port_forward_list": _device(ops.port_list),
        "port_forward_remove": _params(ops.port_remove),
        "port_forward_remove_all": _device(ops.port_remove_all),
        "logcat_snippet": _params(ops.logcat_snippet),
        "screenshot": _device(lambda serial: ops.screenshot(serial, False)),
        "anon_screenshot": _device(lambda serial: ops.screenshot(serial, True)),
        "screenrecord": _params(lambda serial, params: ops.screenrecord(serial, int(params.get("seconds") or 0), False)),
        "anon_screenrecord": _params(lambda serial, params: ops.screenrecord(serial, int(params.get("seconds") or 0), True)),
        "copy_whatsapp": _device(
            lambda serial: ops.copy_remote_dir(
                serial,
                ["/sdcard/Android/media/com.whatsapp/WhatsApp", "/sdcard/WhatsApp"],
                "WhatsApp",
            )
        ),
        "copy_screenshots": _device(
            lambda serial: ops.copy_remote_dir(
                serial,
                ["/sdcard/Pictures/Screenshots", "/sdcard/DCIM/Screenshots", "/sdcard/Screenshots"],
                "Screenshots",
            )
        ),
        "copy_camera": _device(lambda serial: ops.copy_remote_dir(serial, ["/sdcard/DCIM/Camera"], "Camera")),
        "vuln_full_audit": lambda serial, params, config: ops.hardax_run(config, serial, []),
        "vuln_patch_cve": lambda serial, params, config: ops.hardax_run(config, serial, ["--category", "CVE_INDICATORS"]),
        "vuln_hardening": lambda serial, params, config: ops.hardax_run(
            config, serial, ["--category", HARDENING_CATEGORIES]
        ),
        "vuln_app_surface": lambda serial, params, config: ops.hardax_run(config, serial, ["--category", "APPS"]),
        "vuln_export_report": lambda serial, params, config: ops.hardax_last(),
        "metasploit": lambda serial, params, config: ops.metasploit_job(config, serial, params),
    }
    for feature_id, (code, label) in KEYCODE_MAP.items():
        mapping[feature_id] = _device(lambda serial, code=code, label=label: ops.keyevent(serial, code, label))
    return mapping


_HANDLERS: dict[str, Handler] | None = None


def handlers() -> dict[str, Handler]:
    global _HANDLERS
    if _HANDLERS is None:
        _HANDLERS = _handlers()
    return _HANDLERS


# These are reached through uploads, websockets, or process control instead of the generic action body.
SPECIAL_IDS = frozenset(
    {
        "install_app",
        "install_split_apks",
        "push_file",
        "open_photo",
        "open_audio",
        "open_video",
        "set_wallpaper",
        "shell",
        "mirror",
        "camera_live",
        "stream_mic",
        "record_mic",
        "stream_device_audio",
        "record_device_audio",
        "live_logcat",
    }
)


def missing_handlers() -> list[str]:
    covered = set(handlers()) | SPECIAL_IDS
    return sorted(feature_ids() - covered)


def run_feature(feature_id: str, serial: str, params: dict[str, Any], config: Any) -> dict[str, Any]:
    handler = handlers().get(feature_id)
    if handler is None:
        if feature_id in SPECIAL_IDS:
            raise AdbError(f"{feature_id} uses a dedicated endpoint.")
        raise AdbError(f"Unknown feature '{feature_id}'.")
    if feature_id not in HOST_IDS and not serial:
        raise AdbError("A device serial is required.")
    return handler(serial, params or {}, config)
