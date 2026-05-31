"""Applications page sections — CLI 10-13, 36, 45-46, 48-49, 52."""

from __future__ import annotations

from pathlib import Path

from nicegui import ui

from modules.services import app_manager as app_svc
from modules.services import extras as extras_svc
from web.helpers import notify_error, notify_success, require_device, run_io, save_upload
from web.state import state


def render_installed() -> None:
    third_party = ui.switch("Third-party apps only", value=True).classes("mb-4")
    apps_table = ui.column().classes("w-full")

    async def load_apps() -> None:
        if not require_device():
            return
        r = await run_io(app_svc.list_apps, state.context().adb, third_party.value)
        apps_table.clear()
        with apps_table:
            for pkg in (r.data or [])[:200]:
                with ui.row().classes("w-full items-center gap-2 py-1 border-b border-gray-800"):
                    ui.label(pkg).classes("psp-mono text-sm flex-1")

                    async def launch(p=pkg) -> None:
                        lr = await run_io(app_svc.launch_app, state.context().adb, p)
                        notify_success(lr.message) if lr.success else notify_error(lr.message)

                    async def uninstall(p=pkg) -> None:
                        ur = await run_io(app_svc.uninstall_app, state.context().adb, p)
                        notify_success(ur.message) if ur.success else notify_error(ur.message)

                    ui.button(icon="play_arrow", on_click=launch).props("flat dense round")
                    ui.button(icon="delete", on_click=uninstall).props(
                        "flat dense round color=negative"
                    )

    ui.button("Load Apps", on_click=load_apps).props("color=cyan")


def render_install() -> None:
    with ui.card().classes("psp-card w-full mb-4"):
        ui.label("Install APK").classes("font-bold mb-2")

        async def install_upload(e) -> None:
            if not require_device():
                return
            path = await save_upload(e)
            r = await run_io(app_svc.install_app, state.context().adb, path)
            notify_success(r.message) if r.success else notify_error(r.message)

        ui.upload(on_upload=install_upload, auto_upload=True, label="Select APK file").classes(
            "w-full"
        )

    with ui.card().classes("psp-card w-full"):
        ui.label("Install split APKs").classes("font-bold mb-2")
        split_paths: list[Path] = []

        async def split_upload(e) -> None:
            path = await save_upload(e)
            split_paths.append(path)
            notify_success(f"Added {e.file.name} ({len(split_paths)} total)")

        async def install_splits() -> None:
            if not require_device() or not split_paths:
                notify_error("Upload split APK files first")
                return
            r = await run_io(app_svc.install_split_apks, state.context().adb, split_paths)
            notify_success(r.message) if r.success else notify_error(r.message)

        ui.upload(on_upload=split_upload, auto_upload=True, multiple=True).classes("w-full")
        ui.button("Install All Splits", on_click=install_splits).props("color=cyan mt-2")


def render_manage() -> None:
    pkg_input = ui.input("Package name", placeholder="com.example.app").classes("w-full mb-2")
    perm = ui.input("Permission", placeholder="android.permission.CAMERA").classes("w-full mb-4")

    async def extract() -> None:
        if not require_device() or not pkg_input.value:
            notify_error("Enter package name")
            return
        r = await run_io(app_svc.extract_apk, state.context(), pkg_input.value.strip())
        notify_success(r.message) if r.success else notify_error(r.message)

    async def force_stop() -> None:
        if not require_device() or not pkg_input.value:
            return
        r = await run_io(
            app_svc.force_stop_app, state.context().adb, pkg_input.value.strip()
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    async def clear_data() -> None:
        if not require_device() or not pkg_input.value:
            return
        r = await run_io(
            app_svc.clear_app_data, state.context().adb, pkg_input.value.strip()
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    async def restart() -> None:
        if not require_device() or not pkg_input.value:
            return
        r = await run_io(
            app_svc.restart_app, state.context().adb, pkg_input.value.strip()
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    async def grant() -> None:
        if not require_device() or not pkg_input.value or not perm.value:
            notify_error("Enter package and permission")
            return
        r = await run_io(
            extras_svc.grant_revoke_permission,
            state.context().adb,
            pkg_input.value.strip(),
            perm.value.strip(),
            True,
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    async def revoke() -> None:
        if not require_device() or not pkg_input.value or not perm.value:
            notify_error("Enter package and permission")
            return
        r = await run_io(
            extras_svc.grant_revoke_permission,
            state.context().adb,
            pkg_input.value.strip(),
            perm.value.strip(),
            False,
        )
        notify_success(r.message) if r.success else notify_error(r.message)

    with ui.row().classes("gap-2 flex-wrap"):
        ui.button("Extract APK", on_click=extract).props("outline")
        ui.button("Force Stop", on_click=force_stop).props("outline color=orange")
        ui.button("Clear Data", on_click=clear_data).props("outline color=negative")
        ui.button("Restart App", on_click=restart).props("outline")
        ui.button("Grant Permission", on_click=grant).props("outline")
        ui.button("Revoke Permission", on_click=revoke).props("outline")
