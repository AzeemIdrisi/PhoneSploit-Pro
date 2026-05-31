"""Remote control page sections — CLI 17, 23, 29-32, 38-39."""

from __future__ import annotations

from nicegui import ui

from modules.services import communication as comm_svc
from modules.services import device as device_svc
from modules.services import input_control as input_svc
from web.helpers import confirm_danger, notify_error, notify_success, require_device, run_io
from web.state import state


def render_input() -> None:
    text_input = ui.input("Text to send").classes("w-full mb-4")

    keys = [
        ("home", "Home"),
        ("back", "Back"),
        ("recents", "Recents"),
        ("power", "Power"),
        ("volume_up", "Vol+"),
        ("volume_down", "Vol-"),
        ("enter", "Enter"),
        ("delete", "Delete"),
        ("dpad_up", "↑"),
        ("dpad_down", "↓"),
        ("dpad_left", "←"),
        ("dpad_right", "→"),
    ]

    with ui.row().classes("gap-2 flex-wrap mb-4"):
        for key, label in keys:

            async def send(k=key) -> None:
                if not require_device():
                    return
                r = await run_io(input_svc.send_keycode, state.context().adb, k)
                notify_success(r.message) if r.success else notify_error(r.message)

            ui.button(label, on_click=send).props("dense outline")

    async def send_text() -> None:
        if not require_device() or not text_input.value:
            return
        r = await run_io(input_svc.send_text, state.context().adb, text_input.value)
        notify_success(r.message) if r.success else notify_error(r.message)

    ui.button("Send Text", on_click=send_text).props("color=cyan")

    ui.label(
        "Interactive ADB shell → open Console in the sidebar (Terminal tab)."
    ).classes("text-gray-500 text-sm mt-4")


def render_lock_power() -> None:
    unlock_pwd = ui.input("Unlock password (optional)").classes("w-full mb-4")

    async def unlock() -> None:
        if not require_device():
            return
        r = await run_io(
            device_svc.unlock_device, state.context().adb, unlock_pwd.value or ""
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    async def lock() -> None:
        if not require_device():
            return
        r = await run_io(device_svc.lock_device, state.context().adb)
        notify_success(r.message) if r.success else notify_error(r.message)

    with ui.row().classes("gap-2 mb-4"):
        ui.button("Unlock", on_click=unlock).props("outline")
        ui.button("Lock", on_click=lock).props("outline")

    reboot_mode = ui.select(
        {
            "system": "System",
            "recovery": "Recovery",
            "bootloader": "Bootloader",
            "fastboot": "Fastboot",
        },
        value="system",
    ).classes("w-64 mb-4")

    async def do_reboot() -> None:
        if not require_device():
            return
        r = await run_io(device_svc.reboot, state.context().adb, reboot_mode.value)
        notify_success(r.message) if r.success else notify_error(r.message)

    async def do_power_off() -> None:
        if not require_device():
            return
        r = await run_io(device_svc.power_off, state.context().adb)
        notify_success(r.message) if r.success else notify_error(r.message)

    with ui.row().classes("gap-2"):
        ui.button(
            "Reboot",
            on_click=lambda: confirm_danger("Reboot device?", do_reboot),
        ).props("outline color=orange")
        ui.button(
            "Power Off",
            on_click=lambda: confirm_danger("Power off device?", do_power_off),
        ).props("outline color=negative")


def render_messaging() -> None:
    with ui.card().classes("psp-card w-full mb-4"):
        ui.label("Send SMS (BETA — Android 12 tested)").classes("font-bold mb-2")
        number = ui.input("Phone + country code", placeholder="+1234567890").classes("w-full")
        message = ui.textarea("Message").classes("w-full")

        async def send() -> None:
            if not require_device():
                return
            r = await run_io(
                comm_svc.send_sms,
                state.context().adb,
                number.value.strip(),
                message.value.strip(),
            )
            notify_success(r.message) if r.success else notify_error(r.message)

        ui.button("Send SMS", on_click=send).props("color=cyan")

    with ui.card().classes("psp-card w-full"):
        ui.label("Open URL").classes("font-bold mb-2")
        url = ui.input("URL", placeholder="https://github.com").classes("w-full")

        async def open_url() -> None:
            if not require_device():
                return
            r = await run_io(comm_svc.open_link, state.context().adb, url.value.strip())
            notify_success(r.message) if r.success else notify_error(r.message)

        ui.button("Open on Device", on_click=open_url).props("color=cyan")
