"""Network Tools page sections — CLI 44, 51, 56-60."""

from __future__ import annotations

from nicegui import ui

from modules.services import extras as extras_svc
from modules.services import port_forward as pf_svc
from modules.services import wifi_utils as wifi_svc
from web.helpers import notify_error, notify_success, require_device, run_io
from web.state import state


def render_forward() -> None:
    net_output = ui.column().classes("w-full psp-terminal max-h-48 overflow-auto mb-4")
    local_port = ui.number("Local (PC) port", value=8080).classes("w-40")
    remote_port = ui.number("Remote (device) port", value=8080).classes("w-40")
    device_port = ui.number("Device port (reverse)", value=8080).classes("w-40")
    host_port = ui.number("Host port (reverse)", value=8080).classes("w-40")

    async def forward() -> None:
        if not require_device():
            return
        r = await run_io(
            pf_svc.forward_port,
            state.context().adb,
            int(local_port.value),
            int(remote_port.value),
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    async def reverse() -> None:
        if not require_device():
            return
        r = await run_io(
            pf_svc.reverse_port,
            state.context().adb,
            int(device_port.value),
            int(host_port.value),
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    async def list_rules() -> None:
        if not require_device():
            return
        r = await run_io(pf_svc.list_forwards, state.context().adb)
        net_output.clear()
        with net_output:
            ui.label(r.data or r.message).classes("psp-mono text-sm whitespace-pre-wrap")

    async def remove_all() -> None:
        if not require_device():
            return
        r = await run_io(pf_svc.remove_all_forwards, state.context().adb)
        notify_success(r.message) if r.success else notify_error(r.message)

    with ui.row().classes("gap-2 flex-wrap"):
        ui.button("Forward", on_click=forward).props("outline")
        ui.button("Reverse", on_click=reverse).props("outline")
        ui.button("List Rules", on_click=list_rules).props("outline")
        ui.button("Remove All", on_click=remove_all).props("outline color=negative")


def render_wifi() -> None:
    net_output = ui.column().classes("w-full psp-terminal max-h-64 overflow-auto mb-4")
    wifi_mode = ui.select({"enable": "Enable", "disable": "Disable"}, value="enable")

    async def wifi_summary() -> None:
        if not require_device():
            return
        r = await run_io(wifi_svc.wifi_status_summary, state.context().adb)
        net_output.clear()
        with net_output:
            for line in r.data or []:
                ui.label(line).classes("psp-mono text-xs")

    async def wifi_save() -> None:
        if not require_device():
            return
        r = await run_io(wifi_svc.wifi_status_save, state.context())
        notify_success(r.message) if r.success else notify_error(r.message)

    async def wlan() -> None:
        if not require_device():
            return
        r = await run_io(wifi_svc.wlan_ip, state.context().adb)
        net_output.clear()
        with net_output:
            ui.label(r.data or "").classes("psp-mono text-xs whitespace-pre-wrap")

    async def toggle_wifi() -> None:
        if not require_device():
            return
        r = await run_io(wifi_svc.wifi_toggle, state.context().adb, wifi_mode.value)
        notify_success(r.message) if r.success else notify_error(r.message)

    async def saved() -> None:
        if not require_device():
            return
        r = await run_io(wifi_svc.saved_wifi_networks, state.context().adb)
        net_output.clear()
        with net_output:
            if r.success:
                for ssid in (r.data or {}).get("ssids", []):
                    ui.label(ssid).classes("psp-mono text-sm")
            else:
                ui.label(r.message).classes("text-red-400")

    with ui.row().classes("gap-2 flex-wrap"):
        ui.button("WiFi Summary", on_click=wifi_summary).props("outline")
        ui.button("Save dumpsys wifi", on_click=wifi_save).props("outline")
        ui.button("WLAN IP", on_click=wlan).props("outline")
        ui.button("Toggle WiFi", on_click=toggle_wifi).props("outline")
        ui.button("Saved Networks", on_click=saved).props("outline")


def render_connectivity() -> None:
    net_output = ui.column().classes("w-full psp-terminal max-h-64 overflow-auto mb-4")
    ping_host = ui.input("Host to ping", value="8.8.8.8").classes("w-full mb-4")

    async def snapshot() -> None:
        if not require_device():
            return
        r = await run_io(extras_svc.network_snapshot, state.context().adb)
        net_output.clear()
        with net_output:
            d = r.data or {}
            ui.label("=== Interfaces ===").classes("text-cyan-400")
            ui.label(d.get("interfaces", "")).classes("psp-mono text-xs whitespace-pre-wrap")
            ui.label("=== Routes ===").classes("text-cyan-400 mt-2")
            ui.label(d.get("routes", "")).classes("psp-mono text-xs whitespace-pre-wrap")
            ui.label(f"DNS: {d.get('dns', 'N/A')}").classes("mt-2")

    async def ping() -> None:
        if not require_device():
            return
        r = await run_io(
            wifi_svc.ping_connectivity, state.context().adb, ping_host.value or "8.8.8.8"
        )
        net_output.clear()
        with net_output:
            ui.label(r.data or r.message).classes("psp-mono text-xs whitespace-pre-wrap")

    with ui.row().classes("gap-2"):
        ui.button("Network Snapshot", on_click=snapshot).props("color=cyan")
        ui.button("Ping from Device", on_click=ping).props("outline")
