"""Console page — ADB shell, live logcat, and background jobs."""

from __future__ import annotations

from nicegui import ui

from web.components.job_monitor import render_job_monitor
from web.components.page_shell import render_page
from web.components.terminal import render_terminal_panel
from web.navigation import PageMeta, TabMeta

PAGE = PageMeta(
    id="console",
    label="Console",
    icon="terminal",
    section="INFRASTRUCTURE",
    page_description="ADB shell, live logcat, and background job output.",
    tabs=(
        TabMeta("terminal", "Terminal", "Interactive shell and live logcat stream."),
        TabMeta("jobs", "Job Monitor", "Track Metasploit handlers, scans, and long-running tasks."),
    ),
)


def render(content, navigate=None) -> None:
    def terminal_tab() -> None:
        render_terminal_panel(ui.column().classes("w-full"), embedded=True)

    def jobs_tab() -> None:
        render_job_monitor(ui.column().classes("w-full"), embedded=True)

    render_page(
        content,
        title="Console",
        description=PAGE.page_description,
        tabs=[
            ("terminal", "Terminal", PAGE.tabs[0].description, terminal_tab),
            ("jobs", "Job Monitor", PAGE.tabs[1].description, jobs_tab),
        ],
    )
