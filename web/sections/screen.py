"""Screen & Audio page sections — CLI 5-7, 21-26, 40-43, 62."""

from __future__ import annotations

from pathlib import Path

from nicegui import ui

from modules.services import media as media_svc
from web.helpers import notify_error, notify_success, require_device, run_io, save_upload
from web.state import state


def render_live() -> None:
    with ui.row().classes("gap-4 flex-wrap"):
        with ui.card().classes("psp-card flex-1 min-w-72"):
            ui.label("Screen mirror (scrcpy)").classes("font-bold mb-2")
            mirror_mode = ui.select(
                {"default": "Default", "fast": "Fast", "custom": "Custom"},
                value="default",
            ).classes("w-full")
            custom_size = ui.input("Size (e.g. 1024)", value="1024").classes("w-full")
            custom_bitrate = ui.input("Bitrate Mbps (e.g. 2)", value="2").classes("w-full")
            custom_fps = ui.input("Max FPS (e.g. 15)", value="15").classes("w-full")

            def toggle_custom_fields() -> None:
                show = mirror_mode.value == "custom"
                custom_size.visible = show
                custom_bitrate.visible = show
                custom_fps.visible = show

            toggle_custom_fields()
            mirror_mode.on("update:model-value", lambda _: toggle_custom_fields())

            async def launch_mirror() -> None:
                if not require_device():
                    return
                if not state.config.scrcpy_path:
                    notify_error("Scrcpy not installed")
                    return
                mode = mirror_mode.value
                kwargs = {}
                if mode == "custom":
                    kwargs = {
                        "size": custom_size.value or "1024",
                        "bitrate": custom_bitrate.value or "2",
                        "fps": custom_fps.value or "15",
                    }
                r = await run_io(media_svc.mirror_mode, state.config, mode, **kwargs)
                notify_success(r.message) if r.success else notify_error(r.message)

            ui.button("Launch Mirror", on_click=launch_mirror).props("color=cyan")

        with ui.card().classes("psp-card flex-1 min-w-72"):
            ui.label("Camera live (Android 12+)").classes("font-bold mb-2")
            facing = ui.select({"front": "Front", "back": "Back"}, value="front")
            rotation = ui.select(
                {"0": "Normal", "90": "90°", "180": "180°", "270": "270°"},
                value="0",
            )

            async def camera() -> None:
                if not require_device():
                    return
                r = await run_io(
                    media_svc.camera_live,
                    state.config,
                    state.context().adb,
                    facing.value,
                    rotation.value,
                )
                notify_success(r.message) if r.success else notify_error(r.message)

            ui.button("Launch Camera", on_click=camera).props("color=cyan")


def render_capture() -> None:
    duration = ui.number("Record duration (seconds)", value=10).classes("w-48 mb-4")

    async def shot(anonymous: bool = False) -> None:
        if not require_device():
            return
        r = await run_io(media_svc.take_screenshot, state.context(), anonymous)
        notify_success(r.message) if r.success else notify_error(r.message)

    async def record(anonymous: bool = False) -> None:
        if not require_device():
            return
        r = await run_io(
            media_svc.screen_record,
            state.context(),
            int(duration.value or 10),
            anonymous,
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    with ui.row().classes("gap-2 flex-wrap"):
        ui.button("Screenshot", on_click=lambda: shot(False)).props("color=cyan")
        ui.button("Anonymous Screenshot", on_click=lambda: shot(True)).props("outline")
        ui.button("Screen Record", on_click=lambda: record(False)).props("color=cyan")
        ui.button("Anonymous Record", on_click=lambda: record(True)).props("outline")


def render_audio() -> None:
    async def audio_stream(mode: str) -> None:
        if not require_device():
            return
        if not state.config.scrcpy_path:
            notify_error("Scrcpy not installed")
            return
        r = await run_io(media_svc.stream_audio, state.config, mode)
        notify_success(r.message) if r.success else notify_error(r.message)

    async def audio_record(mode: str) -> None:
        if not require_device():
            return
        r = await run_io(
            media_svc.record_audio, state.config, state.context(), mode, False
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    with ui.row().classes("gap-2 flex-wrap"):
        ui.button("Stream Mic", on_click=lambda: audio_stream("mic")).props("outline")
        ui.button("Record Mic", on_click=lambda: audio_record("mic")).props("outline")
        ui.button("Stream Device Audio", on_click=lambda: audio_stream("device")).props(
            "outline"
        )
        ui.button("Record Device Audio", on_click=lambda: audio_record("device")).props(
            "outline"
        )


def render_play() -> None:
    media_types = [
        ("photo", "Open Photo", "image/jpeg", "Photo (JPEG, PNG, etc.)"),
        ("audio", "Open Audio", "audio/mp3", "Audio (MP3, etc.)"),
        ("video", "Open Video", "video/mp4", "Video (MP4, etc.)"),
    ]

    with ui.row().classes("gap-4 flex-wrap w-full"):
        for _key, button_label, mime, upload_label in media_types:
            with ui.card().classes("psp-card flex-1 min-w-64"):
                ui.label(upload_label).classes("font-bold mb-2")
                status = ui.label("No file selected").classes("text-xs text-gray-500 mb-2")
                file_holder: dict[str, Path | None] = {"path": None}

                async def on_upload(e, mime_type=mime, status_label=status, holder=file_holder) -> None:
                    if not require_device():
                        return
                    path = await save_upload(e)
                    holder["path"] = path
                    status_label.text = e.file.name

                async def open_on_device(
                    mime_type=mime,
                    holder=file_holder,
                    btn_label=button_label,
                ) -> None:
                    if not require_device():
                        return
                    path = holder.get("path")
                    if not path or not path.is_file():
                        notify_error("Upload a file first")
                        return
                    r = await run_io(
                        media_svc.push_and_open_media,
                        state.context().adb,
                        path,
                        mime_type,
                    )
                    notify_success(r.message) if r.success else notify_error(r.message)

                ui.upload(on_upload=on_upload, auto_upload=True, label="Choose file").classes(
                    "w-full mb-2"
                )
                ui.button(button_label, on_click=open_on_device).props("color=cyan")
