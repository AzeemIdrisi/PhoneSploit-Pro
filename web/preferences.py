"""Load and apply UI appearance preferences."""

from __future__ import annotations

import json

from nicegui import ui

from web.theme import (
    DEFAULT_FONT,
    DEFAULT_THEME,
    FONTS,
    STORAGE_FONT,
    STORAGE_THEME,
    THEMES,
    apply_preferences_js,
)


def normalize_theme(theme_id: str | None) -> str:
    if theme_id in THEMES:
        return theme_id
    return DEFAULT_THEME


def normalize_font(font_id: str | None) -> str:
    if font_id in FONTS:
        return font_id
    return DEFAULT_FONT


async def load_preferences() -> tuple[str, str]:
    result = await ui.run_javascript(
        f"""
        return {{
            theme: localStorage.getItem({json.dumps(STORAGE_THEME)}) || {json.dumps(DEFAULT_THEME)},
            font: localStorage.getItem({json.dumps(STORAGE_FONT)}) || {json.dumps(DEFAULT_FONT)},
        }};
        """
    )
    if not result:
        return DEFAULT_THEME, DEFAULT_FONT
    return normalize_theme(result.get("theme")), normalize_font(result.get("font"))


def apply_preferences(theme_id: str, font_id: str) -> None:
    theme_id = normalize_theme(theme_id)
    font_id = normalize_font(font_id)
    ui.run_javascript(apply_preferences_js(theme_id, font_id))
