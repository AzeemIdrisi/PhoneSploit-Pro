"""Screen & Audio page."""

from __future__ import annotations

from web.components.page_shell import render_page
from web.navigation import PageMeta, TabMeta
from web.sections import screen as scr

PAGE = PageMeta(
    id="screen",
    label="Screen & Audio",
    icon="videocam",
    section="OPERATE",
    page_description="Mirror, capture, stream, and play media on the device.",
    tabs=(
        TabMeta("live", "Live View", "Real-time mirror and camera via scrcpy."),
        TabMeta("capture", "Capture", "Screenshots and screen recordings saved to PC."),
        TabMeta("audio", "Audio", "Stream or record microphone and device audio."),
        TabMeta("play", "Play on Device", "Push a file and open it on the device."),
    ),
)


def render(content, navigate=None) -> None:
    render_page(
        content,
        title="Screen & Audio",
        description=PAGE.page_description,
        tabs=[
            ("live", "Live View", PAGE.tabs[0].description, scr.render_live),
            ("capture", "Capture", PAGE.tabs[1].description, scr.render_capture),
            ("audio", "Audio", PAGE.tabs[2].description, scr.render_audio),
            ("play", "Play on Device", PAGE.tabs[3].description, scr.render_play),
        ],
    )
