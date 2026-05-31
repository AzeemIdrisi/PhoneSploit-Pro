"""Remote Control page."""

from __future__ import annotations

from web.components.page_shell import render_page
from web.navigation import PageMeta, TabMeta
from web.sections import remote as rem

PAGE = PageMeta(
    id="remote",
    label="Remote Control",
    icon="gamepad",
    section="OPERATE",
    page_description="Send input, control power state, and message the device.",
    tabs=(
        TabMeta("input", "Input", "Keycodes and text input."),
        TabMeta("power", "Lock & Power", "Lock, unlock, reboot, and power off."),
        TabMeta("messaging", "Messaging", "Send SMS and open URLs."),
    ),
)


def render(content, navigate=None) -> None:
    render_page(
        content,
        title="Remote Control",
        description=PAGE.page_description,
        tabs=[
            ("input", "Input", PAGE.tabs[0].description, rem.render_input),
            ("power", "Lock & Power", PAGE.tabs[1].description, rem.render_lock_power),
            ("messaging", "Messaging", PAGE.tabs[2].description, rem.render_messaging),
        ],
    )
