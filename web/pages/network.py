"""Network Tools page."""

from __future__ import annotations

from web.components.page_shell import render_page
from web.navigation import PageMeta, TabMeta
from web.sections import network as net

PAGE = PageMeta(
    id="network",
    label="Network Tools",
    icon="wifi",
    section="INFRASTRUCTURE",
    page_description="Port forwarding, WiFi controls, and connectivity checks.",
    tabs=(
        TabMeta("forward", "Port Forward", "ADB TCP forward and reverse rules."),
        TabMeta("wifi", "WiFi", "Status, toggle, saved networks, and WLAN IP."),
        TabMeta("connectivity", "Connectivity", "Network snapshot and ping from device."),
    ),
)


def render(content, navigate=None) -> None:
    render_page(
        content,
        title="Network Tools",
        description=PAGE.page_description,
        tabs=[
            ("forward", "Port Forward", PAGE.tabs[0].description, net.render_forward),
            ("wifi", "WiFi", PAGE.tabs[1].description, net.render_wifi),
            (
                "connectivity",
                "Connectivity",
                PAGE.tabs[2].description,
                net.render_connectivity,
            ),
        ],
    )
