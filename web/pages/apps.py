"""Applications page."""

from __future__ import annotations

from web.components.page_shell import render_page
from web.navigation import PageMeta, TabMeta
from web.sections import apps as app_sec

PAGE = PageMeta(
    id="apps",
    label="Applications",
    icon="apps",
    section="MANAGE",
    page_description="Browse, install, and manage installed apps.",
    tabs=(
        TabMeta("installed", "Installed", "List, launch, and uninstall apps."),
        TabMeta("install", "Install", "Deploy APK or split APK bundles."),
        TabMeta("manage", "Manage", "Force-stop, clear data, permissions, extract APK."),
    ),
)


def render(content, navigate=None) -> None:
    render_page(
        content,
        title="Applications",
        description=PAGE.page_description,
        tabs=[
            ("installed", "Installed", PAGE.tabs[0].description, app_sec.render_installed),
            ("install", "Install", PAGE.tabs[1].description, app_sec.render_install),
            ("manage", "Manage", PAGE.tabs[2].description, app_sec.render_manage),
        ],
    )
