"""System page sections — CLI 47, 50, 53-55, 61."""

from __future__ import annotations

from nicegui import ui

from modules.services import extras as extras_svc
from modules.services import root_check as root_svc
from web.helpers import notify_error, notify_success, require_device, run_io
from web.state import state


def render_logs() -> None:
    log_lines = ui.number("Last N lines to save", value=500).classes("w-40 mb-4")

    async def logcat_snippet() -> None:
        if not require_device():
            return
        r = await run_io(
            extras_svc.save_logcat_snippet, state.context(), int(log_lines.value or 500)
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    ui.button("Save Logcat Snippet", on_click=logcat_snippet).props("color=cyan")

    ui.label(
        "Live logcat stream → open Console in the sidebar (Terminal tab)."
    ).classes("text-gray-500 text-sm mt-4")


def render_config() -> None:
    diag_output = ui.column().classes("w-full psp-terminal max-h-64 overflow-auto mb-4")
    dev_key = ui.input("Settings key (global namespace)").classes("w-full")
    dev_val = ui.input("Settings value").classes("w-full mb-4")
    stay_mode = ui.select(
        {"usb": "Stay on USB", "true": "Stay on (all)", "false": "Turn off"},
        value="usb",
    ).classes("w-64 mb-4")

    async def dev_read() -> None:
        if not require_device():
            return
        r = await run_io(extras_svc.read_developer_settings, state.context().adb)
        diag_output.clear()
        with diag_output:
            for k, v in (r.data or {}).items():
                ui.label(f"{k}: {v}").classes("psp-mono text-sm")

    async def dev_write() -> None:
        if not require_device() or not dev_key.value:
            notify_error("Enter settings key")
            return
        r = await run_io(
            extras_svc.write_developer_setting,
            state.context().adb,
            dev_key.value,
            dev_val.value,
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    async def locale() -> None:
        if not require_device():
            return
        r = await run_io(extras_svc.read_locale, state.context().adb)
        diag_output.clear()
        with diag_output:
            for k, v in (r.data or {}).items():
                ui.label(f"{k}: {v}").classes("psp-mono text-sm")

    async def stay_on() -> None:
        if not require_device():
            return
        r = await run_io(extras_svc.screen_stay_on, state.context().adb, stay_mode.value)
        notify_success(r.message) if r.success else notify_error(r.message)

    with ui.row().classes("gap-2 flex-wrap mb-4"):
        ui.button("Read Dev Settings", on_click=dev_read).props("outline")
        ui.button("Write Dev Setting", on_click=dev_write).props("outline")
        ui.button("Read Locale", on_click=locale).props("outline")

    ui.button("Set Screen Stay-On", on_click=stay_on).props("outline")


def render_security_check() -> None:
    diag_output = ui.column().classes("w-full psp-terminal max-h-96 overflow-auto")

    async def root() -> None:
        if not require_device():
            return
        r = await run_io(root_svc.root_heuristics, state.context().adb)
        diag_output.clear()
        with diag_output:
            d = r.data or {}
            ui.label(f"Verdict: {d.get('verdict', r.message)}").classes(
                "text-yellow-400 font-bold"
            )
            ui.label(d.get("detail", "")).classes("text-sm text-gray-400 mb-2")
            for k, v in (d.get("props") or {}).items():
                ui.label(f"{k}: {v}").classes("psp-mono text-xs")

    ui.button("Run Root Heuristics", on_click=root).props("color=cyan")
