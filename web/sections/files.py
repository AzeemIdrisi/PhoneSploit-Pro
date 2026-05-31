"""Files & Data page sections — CLI 8-9, 16-20, 33-35."""

from __future__ import annotations

from pathlib import Path

from nicegui import ui

from modules.services import data_extraction as data_svc
from modules.services import file_manager as file_svc
from web.helpers import notify_error, notify_success, require_device, run_io, save_upload
from web.state import state


def render_manager() -> None:
    sdcard_list = ui.column().classes("w-full psp-terminal max-h-64 overflow-auto mb-4")
    remote_path = ui.input(
        "Remote path under /sdcard/", placeholder="Download/file.zip"
    ).classes("w-full")
    push_dest = ui.input("Push destination folder", placeholder="Documents").classes("w-full mb-4")

    async def list_sdcard() -> None:
        if not require_device():
            return
        r = await run_io(file_svc.list_sdcard, state.context().adb)
        sdcard_list.clear()
        with sdcard_list:
            for entry in r.data or []:
                ui.label(entry).classes("psp-mono text-sm")

    async def pull() -> None:
        if not require_device() or not remote_path.value:
            notify_error("Enter remote path")
            return
        r = await run_io(file_svc.pull_file, state.context(), remote_path.value.strip())
        notify_success(r.message) if r.success else notify_error(r.message)

    async def push_upload(e) -> None:
        if not require_device():
            return
        path = await save_upload(e)
        r = await run_io(
            file_svc.push_file,
            state.context().adb,
            path,
            push_dest.value or "",
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    with ui.row().classes("gap-2 mb-4"):
        ui.button("List /sdcard/", on_click=list_sdcard).props("color=cyan")
        ui.button("Pull File", on_click=pull).props("outline")

    ui.upload(on_upload=push_upload, auto_upload=True, label="Push file to device").classes(
        "w-full"
    )


def render_bulk() -> None:
    async def copy_wa() -> None:
        if not require_device():
            return
        r = await run_io(file_svc.copy_whatsapp, state.context())
        notify_success(r.message) if r.success else notify_error(r.message)

    async def copy_ss() -> None:
        if not require_device():
            return
        r = await run_io(file_svc.copy_screenshots, state.context())
        notify_success(r.message) if r.success else notify_error(r.message)

    async def copy_cam() -> None:
        if not require_device():
            return
        r = await run_io(file_svc.copy_camera, state.context())
        notify_success(r.message) if r.success else notify_error(r.message)

    with ui.row().classes("gap-2 flex-wrap"):
        ui.button("Copy WhatsApp Data", on_click=copy_wa).props("outline")
        ui.button("Copy All Screenshots", on_click=copy_ss).props("outline")
        ui.button("Copy Camera Photos", on_click=copy_cam).props("outline")


def render_personal() -> None:
    ui.label("Exports are saved to your output folder.").classes("text-gray-500 text-sm mb-4")

    async def dump(fn) -> None:
        if not require_device():
            return
        r = await run_io(fn, state.context())
        notify_success(r.message) if r.success else notify_error(r.message)

    with ui.row().classes("gap-2 flex-wrap"):
        ui.button("Dump SMS", on_click=lambda: dump(data_svc.dump_sms)).props("color=cyan")
        ui.button("Dump Contacts", on_click=lambda: dump(data_svc.dump_contacts)).props(
            "color=cyan"
        )
        ui.button("Dump Call Logs", on_click=lambda: dump(data_svc.dump_call_logs)).props(
            "color=cyan"
        )
