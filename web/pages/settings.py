"""Settings page."""

from __future__ import annotations

from pathlib import Path

from nicegui import ui

from modules.cli import _collect_missing_tools
from modules.tools import resolve_external_tools
from web.components.credits import render_about_section
from web.components.page_shell import render_page
from web.helpers import io_timer, notify_success
from web.navigation import PageMeta
from web.preferences import apply_preferences, load_preferences
from web.state import state
from web.theme import DEFAULT_FONT, DEFAULT_THEME, font_options, theme_options

PAGE = PageMeta(
    id="settings",
    label="Settings",
    icon="settings",
    section="CONFIG",
    page_description="Output folder, appearance, and dependencies.",
)


def render(content, navigate=None) -> None:
    def body() -> None:
        out_input = ui.input("Output folder", value=str(state.output_dir)).classes("w-full")

        def save_output() -> None:
            p = Path(out_input.value.strip() or "Downloaded-Files")
            p.mkdir(parents=True, exist_ok=True)
            state.output_dir = p
            notify_success(f"Output folder: {p}")

        ui.button("Save Output Folder", on_click=save_output).props("outline")

        with ui.card().classes("psp-card w-full mt-4"):
            ui.label("Appearance").classes("font-bold mb-2")
            ui.label("Theme and font preferences are saved in your browser.").classes(
                "text-xs text-gray-500 mb-3"
            )
            theme_select = ui.select(theme_options(), value=DEFAULT_THEME, label="Theme").classes(
                "w-full mb-3"
            )
            font_select = ui.select(font_options(), value=DEFAULT_FONT, label="Font").classes(
                "w-full mb-3"
            )
            ui.label("Preview").classes("text-xs text-gray-500 uppercase tracking-wide mb-1")
            ui.label("The quick brown fox jumps over the lazy dog.").classes("text-lg mb-1")
            ui.label("adb shell getprop ro.product.model").classes("psp-mono text-sm")

            @io_timer
            async def sync_appearance_controls() -> None:
                theme, font = await load_preferences()
                theme_select.value = theme
                font_select.value = font

            def preview_appearance() -> None:
                apply_preferences(theme_select.value, font_select.value)

            def save_appearance() -> None:
                apply_preferences(theme_select.value, font_select.value)
                notify_success("Appearance saved")

            def reset_appearance() -> None:
                theme_select.value = DEFAULT_THEME
                font_select.value = DEFAULT_FONT
                apply_preferences(DEFAULT_THEME, DEFAULT_FONT)
                notify_success("Appearance reset")

            with ui.row().classes("gap-2 mt-3 flex-wrap"):
                ui.button("Apply", on_click=save_appearance).props("color=cyan")
                ui.button("Reset defaults", on_click=reset_appearance).props("flat")
            theme_select.on("update:model-value", lambda _: preview_appearance())
            font_select.on("update:model-value", lambda _: preview_appearance())
            ui.timer(0.1, sync_appearance_controls, once=True)

        with ui.card().classes("psp-card w-full mt-4"):
            ui.label("Dependencies").classes("font-bold mb-2")
            deps_list = ui.column().classes("w-full gap-1 mb-2")

            def render_deps() -> None:
                deps_list.clear()
                missing = _collect_missing_tools(state.config)
                with deps_list:
                    if missing:
                        for name, _ in missing:
                            ui.label(f"Missing: {name}").classes("text-red-400")
                    else:
                        ui.label("All tools detected").classes("text-green-400")

            render_deps()
            ui.label("Run install.sh or install.ps1 for missing tools.").classes(
                "text-xs text-gray-500 mt-2"
            )

            async def refresh_tools() -> None:
                resolve_external_tools(state.config)
                from modules.services.adb import set_global_adb

                set_global_adb(state.config.adb_path)
                render_deps()
                notify_success("Tool paths refreshed")

            ui.button("Refresh Tool Detection", on_click=refresh_tools).props("flat")

        render_about_section()

        ui.label(
            "Web UI binds to 127.0.0.1 only — do not expose to your network without authentication."
        ).classes("text-xs text-yellow-600 mt-6")

    render_page(
        content,
        title="Settings",
        description=PAGE.page_description,
        content_fn=body,
    )
