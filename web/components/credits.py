"""Credits and footer for the web UI."""

from __future__ import annotations

from nicegui import ui

from web import meta


def github_icon_button(*, flat: bool = True, dense: bool = True) -> None:
    props = "flat round" if flat else "outline"
    if dense:
        props += " dense"
    with ui.link(target=meta.GITHUB_REPO, new_tab=True).tooltip("View on GitHub").classes(
        "psp-icon-link inline-flex items-center"
    ):
        ui.icon("img:https://cdn.simpleicons.org/github/e6edf3").classes("w-5 h-5")


def render_app_footer() -> None:
    with ui.row().classes(
        "w-full items-center justify-center gap-1 px-4 py-3 "
        "border-t border-gray-800 text-xs text-gray-500"
    ):
        ui.label(f"{meta.APP_NAME} by")
        ui.link(meta.AUTHOR, meta.AUTHOR_GITHUB, new_tab=True).classes("psp-text-link")
        ui.label(meta.COPYRIGHT_YEAR)


def render_link_row() -> None:
    with ui.row().classes("gap-3 flex-wrap items-center"):
        github_icon_button()
        ui.link("Repository", meta.GITHUB_REPO, new_tab=True).classes("psp-text-link text-sm")
        ui.link("Report issue", meta.GITHUB_ISSUES, new_tab=True).classes("psp-text-link text-sm")
        ui.link("Documentation", meta.GITHUB_DOCS, new_tab=True).classes("psp-text-link text-sm")
        ui.link(meta.LICENSE, meta.LICENSE_URL, new_tab=True).classes("psp-text-link text-sm")


def render_about_section() -> None:
    with ui.card().classes("psp-card w-full mt-4"):
        ui.label("About").classes("font-bold mb-2")
        ui.label(meta.TAGLINE).classes("text-sm text-gray-400 mb-3")
        with ui.row().classes("gap-4 flex-wrap mb-4"):
            with ui.column().classes("gap-1"):
                ui.label("Version").classes("text-xs text-gray-500 uppercase")
                ui.label(meta.VERSION).classes("psp-mono text-cyan-400")
            with ui.column().classes("gap-1"):
                ui.label("License").classes("text-xs text-gray-500 uppercase")
                ui.link(meta.LICENSE, meta.LICENSE_URL, new_tab=True).classes("psp-text-link")
            with ui.column().classes("gap-1"):
                ui.label("Developer").classes("text-xs text-gray-500 uppercase")
                ui.link(meta.AUTHOR, meta.AUTHOR_GITHUB, new_tab=True).classes("psp-text-link")

        render_link_row()

        ui.label("Support the project").classes("text-sm font-bold mt-4 mb-2")
        with ui.row().classes("gap-3 flex-wrap"):
            for label, url in meta.SUPPORT_LINKS:
                ui.link(label, url, new_tab=True).classes("psp-text-link text-sm")

        ui.label("Disclaimer").classes("text-sm font-bold mt-4 mb-2")
        ui.label(meta.DISCLAIMER).classes("text-sm text-yellow-600")
        ui.label(
            "This project does not promote illegal activity. The developer is not "
            "responsible for misuse. Use only on devices you own or have permission to test."
        ).classes("text-xs text-gray-500 mt-2")
