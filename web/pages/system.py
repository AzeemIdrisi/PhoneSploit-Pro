"""System page."""

from __future__ import annotations

from web.components.page_shell import render_page
from web.navigation import PageMeta, TabMeta
from web.sections import system as sys_sec

PAGE = PageMeta(
    id="system",
    label="System",
    icon="bug_report",
    section="ADVANCED",
    page_description="Logs, developer settings, and security heuristics.",
    tabs=(
        TabMeta("logs", "Logs", "Save logcat snippets; live stream on Console page."),
        TabMeta("config", "Configuration", "Developer settings, locale, screen stay-on."),
        TabMeta("security", "Security Check", "Root and build heuristics."),
    ),
)


def render(content, navigate=None) -> None:
    render_page(
        content,
        title="System",
        description=PAGE.page_description,
        tabs=[
            ("logs", "Logs", PAGE.tabs[0].description, sys_sec.render_logs),
            ("config", "Configuration", PAGE.tabs[1].description, sys_sec.render_config),
            ("security", "Security Check", PAGE.tabs[2].description, sys_sec.render_security_check),
        ],
    )
