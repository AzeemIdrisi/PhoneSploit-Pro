"""Shared UI helpers."""

from __future__ import annotations

import asyncio
import inspect
import tempfile
from collections.abc import Awaitable, Callable
from functools import wraps
from pathlib import Path

from nicegui import run, ui
from nicegui.events import UploadEventArguments

from web.state import state


def notify_success(msg: str) -> None:
    ui.notify(msg, type="positive", close_button=True)


def notify_error(msg: str) -> None:
    ui.notify(msg, type="negative", close_button=True)


def notify_warning(msg: str) -> None:
    ui.notify(msg, type="warning", close_button=True)


def require_device() -> bool:
    if not state.config.adb_path:
        notify_error("ADB is not installed or not on PATH")
        return False
    if not state.active_serial:
        notify_warning("Select an active device from the top bar")
        return False
    return True


def require_adb() -> bool:
    if not state.config.adb_path:
        notify_error("ADB is not installed or not on PATH")
        return False
    return True


async def run_io(fn, *args, **kwargs):
    try:
        return await run.io_bound(fn, *args, **kwargs)
    except asyncio.CancelledError:
        return None


def io_timer(fn: Callable[..., Awaitable[None]]) -> Callable[..., Awaitable[None]]:
    """Wrap async timer/page-load callbacks so shutdown does not log tracebacks."""

    @wraps(fn)
    async def wrapper(*args, **kwargs) -> None:
        try:
            await fn(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except AttributeError:
            pass
        except RuntimeError as exc:
            if "client" in str(exc).lower() or "deleted" in str(exc).lower():
                return
            raise

    return wrapper


async def save_upload(e: UploadEventArguments) -> Path:
    """Persist a NiceGUI upload event to a temp file."""
    name = (e.file.name or "upload.bin").replace("/", "_").replace("\\", "_")
    path = Path(tempfile.gettempdir()) / name
    await e.file.save(path)
    return path


def result_handler(result, *, success_msg: str | None = None) -> None:
    from modules.services.adb import OperationResult

    if isinstance(result, OperationResult):
        if result.success:
            notify_success(success_msg or result.message)
        else:
            notify_error(result.error or result.message)
    elif result:
        notify_success(success_msg or str(result))
    else:
        notify_error("Operation failed")


def confirm_danger(title: str, on_confirm) -> None:
    with ui.dialog() as dialog, ui.card().classes("psp-card"):
        ui.label(title).classes("text-lg font-bold text-red-400")
        ui.label("Type CONFIRM to proceed").classes("text-sm text-gray-400")
        confirm_input = ui.input("CONFIRM").classes("w-full")

        async def proceed() -> None:
            if confirm_input.value != "CONFIRM":
                notify_error("Type CONFIRM to proceed")
                return
            dialog.close()
            result = on_confirm()
            if inspect.isawaitable(result):
                await result

        with ui.row().classes("w-full justify-end gap-2 mt-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Proceed", on_click=proceed).props("color=negative")
    dialog.open()


def render_tool_status_list(container):
    """Populate a container with current tool availability rows."""

    def render() -> None:
        container.clear()
        with container:
            for name, ok in state.tool_status().items():
                with ui.row().classes("items-center gap-2"):
                    ui.icon("check_circle" if ok else "cancel").classes(
                        "text-green-400" if ok else "text-red-400"
                    )
                    ui.label(name)

    return render
