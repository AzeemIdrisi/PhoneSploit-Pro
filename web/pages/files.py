"""Files & Data page."""

from __future__ import annotations

from web.components.page_shell import render_page
from web.navigation import PageMeta, TabMeta
from web.sections import files as file_sec

PAGE = PageMeta(
    id="files",
    label="Files & Data",
    icon="folder",
    section="MANAGE",
    page_description="Transfer files and export personal data from the device.",
    tabs=(
        TabMeta("manager", "File Manager", "Browse /sdcard/, pull, and push files."),
        TabMeta("bulk", "Bulk Export", "Copy WhatsApp, screenshots, and camera rolls."),
        TabMeta("personal", "Personal Data", "Export SMS, contacts, and call logs."),
    ),
)


def render(content, navigate=None) -> None:
    render_page(
        content,
        title="Files & Data",
        description=PAGE.page_description,
        tabs=[
            ("manager", "File Manager", PAGE.tabs[0].description, file_sec.render_manager),
            ("bulk", "Bulk Export", PAGE.tabs[1].description, file_sec.render_bulk),
            ("personal", "Personal Data", PAGE.tabs[2].description, file_sec.render_personal),
        ],
    )
