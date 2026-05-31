"""Home page — overview and navigation shortcuts."""

from __future__ import annotations

from nicegui import ui

from modules.services import device as device_svc
from modules.tools import resolve_external_tools
from web.components.page_shell import render_page
from web.helpers import io_timer, notify_success, render_tool_status_list, run_io
from web.navigation import PageMeta
from web.state import state

PAGE = PageMeta(
    id="home",
    label="Home",
    icon="dashboard",
    section="OVERVIEW",
    page_description="Status at a glance and quick navigation.",
)


def render(content, navigate=None) -> None:
    def body() -> None:
        with ui.row().classes("w-full gap-4 flex-wrap"):
            with ui.card().classes("psp-card flex-1 min-w-64"):
                ui.label("Active Device").classes("font-bold mb-2")
                model_label = ui.label("—").classes("text-lg")
                android_label = ui.label("").classes("text-gray-400")
                serial_label = ui.label("").classes("psp-mono text-xs text-cyan-400 mt-2")
                battery_label = ui.label("").classes("text-sm")

                @io_timer
                async def load_summary() -> None:
                    if not state.active_serial:
                        model_label.text = "No device selected"
                        android_label.text = "Choose one in the top bar"
                        serial_label.text = ""
                        battery_label.text = ""
                        return
                    if not state.config.adb_path:
                        model_label.text = "ADB not available"
                        android_label.text = ""
                        serial_label.text = ""
                        battery_label.text = ""
                        return
                    info = await run_io(device_svc.get_device_info, state.context().adb)
                    bat = await run_io(device_svc.get_battery_info, state.context().adb)
                    if info is None or bat is None:
                        return
                    if info.success and info.data:
                        model_label.text = info.data.get("Model", "Unknown")
                        android_label.text = f"Android {info.data.get('Android Version', '?')}"
                    else:
                        model_label.text = "Unknown device"
                        android_label.text = ""
                    serial_label.text = state.active_serial
                    battery_parts = []
                    if bat.success and bat.data:
                        for k, v in bat.data.items():
                            if k.lower() in ("level", "status") and v:
                                battery_parts.append(f"{k}: {v}")
                    battery_label.text = " · ".join(battery_parts)

                ui.button("Refresh", on_click=load_summary).props("flat dense size=sm")
                ui.timer(0.1, load_summary, once=True)

            with ui.card().classes("psp-card flex-1 min-w-64"):
                ui.label("Tool Status").classes("font-bold mb-2")
                tools_list = ui.column().classes("w-full gap-1")
                render_tools = render_tool_status_list(tools_list)

                async def refresh_tools() -> None:
                    resolve_external_tools(state.config)
                    from modules.services.adb import set_global_adb

                    set_global_adb(state.config.adb_path)
                    render_tools()
                    notify_success("Tool paths refreshed")

                with ui.row().classes("items-center gap-2"):
                    ui.button("Refresh Tools", on_click=refresh_tools).props("flat dense size=sm")
                render_tools()

            with ui.card().classes("psp-card flex-1 min-w-64"):
                ui.label("Output").classes("font-bold mb-2")
                ui.label(str(state.output_dir)).classes("psp-mono text-sm text-gray-400")

        if navigate:
            ui.label("Quick navigation").classes("font-bold mt-6 mb-2")
            shortcuts = [
                ("devices", "Devices", "link"),
                ("screen", "Mirror / Capture", "videocam"),
                ("console", "Console", "terminal"),
                ("apps", "Applications", "apps"),
                ("exploit", "Exploit", "security"),
            ]
            with ui.row().classes("gap-2 flex-wrap"):
                for page_id, label, icon in shortcuts:
                    ui.button(
                        label,
                        icon=icon,
                        on_click=lambda p=page_id: navigate(p),
                    ).props("outline color=cyan")

    render_page(
        content,
        title="Home",
        description=PAGE.page_description,
        content_fn=body,
    )
