"""Devices page."""

from __future__ import annotations

from web.components.page_shell import render_page
from web.navigation import PageMeta, TabMeta
from web.sections import devices as dev

PAGE = PageMeta(
    id="devices",
    label="Devices",
    icon="devices",
    section="CONNECT",
    page_description="Connect, discover, and inspect Android devices.",
    tabs=(
        TabMeta("connect", "Connect", "Pair over Wi‑Fi and manage the device list."),
        TabMeta("discover", "Discover", "Scan the LAN for ADB hosts and connect."),
        TabMeta("adb", "ADB Server", "Disconnect sessions or stop the ADB server."),
        TabMeta("info", "Device Info", "Hardware, OS, and battery details."),
    ),
)


def render(content, navigate=None) -> None:
    render_page(
        content,
        title="Devices",
        description=PAGE.page_description,
        tabs=[
            ("connect", "Connect", PAGE.tabs[0].description, dev.render_connect),
            ("discover", "Discover", PAGE.tabs[1].description, dev.render_discover),
            ("adb", "ADB Server", PAGE.tabs[2].description, dev.render_adb_server),
            ("info", "Device Info", PAGE.tabs[3].description, dev.render_info),
        ],
    )
