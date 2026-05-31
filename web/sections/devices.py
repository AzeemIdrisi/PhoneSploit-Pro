"""Devices page sections — CLI 1-4, 27-28, 37."""

from __future__ import annotations

from nicegui import ui

from modules.services.adb import ADBService
from modules.services import connection as conn_svc
from modules.services import device as device_svc
from web.helpers import io_timer, notify_error, notify_success, require_device, run_io
from web.state import state


def render_connect() -> None:
    with ui.card().classes("psp-card w-full mb-4"):
        ui.label("Connect over Wi‑Fi").classes("font-bold mb-2")
        ip_input = ui.input("Device IP", placeholder="192.168.1.23").classes("w-full")
        port_input = ui.number("Port", value=5555).classes("w-32")

        async def do_connect() -> None:
            ip = (ip_input.value or "").strip()
            if not ip:
                notify_error("Enter device IP")
                return
            if not state.config.adb_path:
                notify_error("ADB is not installed or not on PATH")
                return
            port = int(port_input.value or 5555)
            adb = ADBService(state.config.adb_path)
            r = await run_io(conn_svc.connect_device, adb, ip, port)
            if r.success:
                notify_success(r.message)
                serials = (r.data or {}).get("serials", [])
                if serials:
                    state.active_serial = serials[-1]
            else:
                notify_error(r.message)

        ui.button("Connect", on_click=do_connect).props("color=cyan")

    with ui.card().classes("psp-card w-full"):
        ui.label("Connected devices").classes("font-bold mb-2")
        table_area = ui.column().classes("w-full")

        @io_timer
        async def refresh() -> None:
            table_area.clear()
            if not state.config.adb_path:
                with table_area:
                    ui.label("ADB not available").classes("text-red-400")
                    ui.button("Refresh", on_click=refresh).props("flat dense size=sm")
                return
            adb = ADBService(state.config.adb_path)
            r = await run_io(conn_svc.list_devices, adb)
            if r is None:
                return
            with table_area:
                if not r.data:
                    ui.label("No devices connected").classes("text-gray-500")
                for d in r.data or []:
                    with ui.row().classes("gap-2 items-center py-1"):
                        ui.label(d.serial).classes("psp-mono text-sm flex-1")
                        ui.badge(d.state).props(
                            "color=green" if d.state == "device" else "color=orange"
                        )

                        def select(serial=d.serial) -> None:
                            state.active_serial = serial
                            notify_success(f"Active device: {serial}")

                        if d.state == "device":
                            ui.button("Use", on_click=select).props("flat dense size=sm")

                ui.button("Refresh", on_click=refresh).props("flat dense size=sm")
                ui.timer(0.1, refresh, once=True)


def render_discover() -> None:
    scan_table = ui.column().classes("w-full")

    async def scan_and_show() -> None:
        if not state.config.nmap_path:
            notify_error("Nmap not installed")
            return
        r = await run_io(conn_svc.scan_network, state.config)
        scan_table.clear()
        with scan_table:
            if not r.success and not r.data:
                notify_error(r.message)
                return
            if not r.data:
                ui.label("No hosts found").classes("text-gray-500")
                return
            for h in r.data:
                with ui.row().classes(
                    "gap-4 psp-mono text-sm border-b border-gray-700 py-2 items-center w-full"
                ):
                    ui.label(h.ip).classes("text-green-400 w-32")
                    ui.label(h.adb_summary).classes("flex-1")
                    ui.label(h.android_hint).classes("text-yellow-400 w-48")

                    async def connect_to(ip=h.ip) -> None:
                        if not state.config.adb_path:
                            notify_error("ADB is not installed or not on PATH")
                            return
                        adb = ADBService(state.config.adb_path)
                        cr = await run_io(conn_svc.connect_device, adb, ip, 5555)
                        if cr.success:
                            notify_success(cr.message)
                            serials = (cr.data or {}).get("serials", [])
                            if serials:
                                state.active_serial = serials[-1]
                        else:
                            notify_error(cr.message)

                    ui.button("Connect", on_click=connect_to).props("flat dense size=sm")

    ui.button("Scan LAN for ADB hosts", on_click=scan_and_show).props("color=cyan")


def render_adb_server() -> None:
    with ui.card().classes("psp-card w-full"):
        ui.label("ADB server control").classes("font-bold mb-2")

        async def disconnect() -> None:
            if not state.config.adb_path:
                notify_error("ADB is not installed or not on PATH")
                return
            r = await run_io(conn_svc.disconnect_all, ADBService(state.config.adb_path))
            state.active_serial = None
            notify_success(r.message) if r.success else notify_error(r.message)

        async def stop_adb() -> None:
            if not state.config.adb_path:
                notify_error("ADB is not installed or not on PATH")
                return
            r = await run_io(conn_svc.stop_adb_server, ADBService(state.config.adb_path))
            state.active_serial = None
            notify_success(r.message) if r.success else notify_error(r.message)

        with ui.row().classes("gap-2"):
            ui.button("Disconnect All Devices", on_click=disconnect).props("outline color=orange")
            ui.button("Stop ADB Server", on_click=stop_adb).props("outline color=negative")


def render_info() -> None:
    info_area = ui.column().classes("w-full psp-terminal max-h-96 overflow-auto")

    async def show_info() -> None:
        if not require_device():
            return
        r = await run_io(device_svc.get_device_info, state.context().adb)
        info_area.clear()
        with info_area:
            ui.label("Device properties").classes("text-cyan-400 font-bold mb-2")
            for k, v in (r.data or {}).items():
                ui.label(f"{k}: {v}").classes("psp-mono text-sm")

    async def battery() -> None:
        if not require_device():
            return
        r = await run_io(device_svc.get_battery_info, state.context().adb)
        info_area.clear()
        with info_area:
            ui.label("Battery").classes("text-cyan-400 font-bold mb-2")
            for k, v in (r.data or {}).items():
                ui.label(f"{k}: {v}").classes("psp-mono text-sm")

    with ui.row().classes("gap-2 mb-4"):
        ui.button("Load Device Info", on_click=show_info).props("color=cyan")
        ui.button("Load Battery Info", on_click=battery).props("outline")
