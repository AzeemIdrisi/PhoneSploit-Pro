"""PhoneSploit Pro NiceGUI application."""

from __future__ import annotations

from nicegui import ui

from web.components.credits import render_app_footer
from web.components.device_bar import render_device_bar
from web.components.terminal import register_terminal_routes
from web.navigation import NAV_SECTIONS
from web.pages import (
    apps,
    console,
    dashboard,
    devices,
    exploit,
    files,
    network,
    remote,
    screen,
    settings,
    system,
)
from modules.constants import WEB_UI_HOST, WEB_UI_PORT
from web.state import state
from web import meta
from web.theme import bootstrap_script, build_css

PAGE_MODULES = {
    "home": dashboard,
    "devices": devices,
    "screen": screen,
    "remote": remote,
    "apps": apps,
    "files": files,
    "network": network,
    "console": console,
    "exploit": exploit,
    "system": system,
    "settings": settings,
}


def create_app() -> None:
    register_terminal_routes()
    ui.add_head_html(f"<style id=\"psp-theme-style\">{build_css()}</style>", shared=True)
    ui.add_head_html(bootstrap_script(), shared=True)
    ui.add_head_html(
        f"""
        <link rel="icon" href="https://cdn.simpleicons.org/android/58a6ff">
        <meta name="description" content="{meta.APP_NAME} — {meta.TAGLINE}">
        <meta name="author" content="{meta.AUTHOR}">
        """,
        shared=True,
    )

    @ui.page("/")
    def main_page() -> None:
        page_buttons: dict[str, ui.button] = {}
        content_area = None

        def navigate(page_id: str) -> None:
            if page_id not in PAGE_MODULES:
                return
            state.current_page = page_id
            content_area.clear()
            module = PAGE_MODULES[page_id]
            module.render(content_area, navigate=navigate)
            for pid, btn in page_buttons.items():
                if pid == page_id:
                    btn.props("color=cyan flat")
                else:
                    btn.props("flat color=grey")

        with ui.left_drawer(fixed=True).classes("psp-sidebar"):
            with ui.column().classes("psp-sidebar-inner w-full"):
                ui.label("PhoneSploit Pro").classes(
                    "text-lg font-bold text-cyan-400 px-2 py-3 shrink-0"
                )
                with ui.scroll_area().classes("psp-sidebar-nav"):
                    with ui.column().classes("w-full pb-4"):
                        for section_label, pages in NAV_SECTIONS:
                            ui.label(section_label).classes(
                                "text-xs text-gray-500 uppercase tracking-wide px-2 pt-3 pb-1"
                            )
                            for page in pages:
                                btn = ui.button(
                                    page.label,
                                    icon=page.icon,
                                    on_click=lambda p=page.id: navigate(p),
                                )
                                btn.props("flat align=left").classes("w-full justify-start")
                                page_buttons[page.id] = btn

        with ui.header().classes("psp-topbar"):
            topbar = ui.column().classes("w-full")
            render_device_bar(topbar)

        with ui.column().classes("w-full px-4 pt-2 flex-1"):
            content_area = ui.column().classes("w-full min-h-[70vh]")

        render_app_footer()

        navigate("home")


def run(host: str = WEB_UI_HOST, port: int = WEB_UI_PORT) -> None:
    state.web_host = host
    state.web_port = port
    create_app()
    try:
        ui.run(
            host=host,
            port=port,
            title="PhoneSploit Pro",
            dark=True,
            reload=False,
            show=True,
            favicon="https://cdn.simpleicons.org/android/58a6ff",
        )
    except KeyboardInterrupt:
        pass
