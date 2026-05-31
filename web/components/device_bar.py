"""Active device selector and live polling."""

from __future__ import annotations

from nicegui import ui

from modules.services.adb import ADBService
from modules.services import connection as conn_svc
from web.components.credits import github_icon_button
from web.helpers import io_timer, notify_success, run_io
from web import meta
from web.state import state


def render_device_bar(container) -> None:
    with container:
        with ui.row().classes("items-center gap-4 w-full p-3 psp-topbar"):
            ui.label("PhoneSploit Pro").classes("text-xl font-bold text-cyan-400")
            ui.label(meta.WEB_UI_LABEL).classes("psp-version-badge text-xs px-2 py-1 rounded")

            device_select = ui.select(
                options=[],
                label="Active device",
                with_input=True,
            ).classes("min-w-64").props("dense outlined dark")

            status_label = ui.label("No devices").classes("text-sm text-gray-400")

            @io_timer
            async def refresh_devices() -> None:
                if not state.config.adb_path:
                    status_label.text = "ADB not available"
                    status_label.classes(remove="text-green-400", add="text-red-400")
                    device_select.options = {}
                    device_select.value = None
                    device_select.update()
                    return

                adb = ADBService(state.config.adb_path)
                result = await run_io(conn_svc.list_devices, adb)
                if result is None:
                    return
                devices = result.data or []
                options = {d.serial: f"{d.serial} ({d.state})" for d in devices}

                if options != device_select.options:
                    device_select.options = options
                    device_select.update()

                ready = [d for d in devices if d.state == "device"]
                if ready and not state.active_serial:
                    state.active_serial = ready[0].serial
                    device_select.value = ready[0].serial
                elif state.active_serial and state.active_serial in options:
                    device_select.value = state.active_serial
                elif state.active_serial and state.active_serial not in options:
                    state.active_serial = None
                    device_select.value = None

                if ready:
                    status_label.text = f"{len(ready)} ready · {len(devices)} total"
                    status_label.classes(remove="text-red-400", add="text-green-400")
                else:
                    status_label.text = "No authorized devices"
                    status_label.classes(remove="text-green-400", add="text-red-400")

            def on_device_change(e) -> None:
                state.active_serial = e.value
                if e.value:
                    notify_success(f"Active device: {e.value}")

            device_select.on("update:model-value", on_device_change)

            ui.button(icon="refresh", on_click=refresh_devices).props(
                "flat round dense"
            ).tooltip("Refresh devices")

            with ui.row().classes("gap-2 ml-auto items-center"):
                github_icon_button()

            ui.timer(10.0, refresh_devices)
            ui.timer(0.1, refresh_devices, once=True)
