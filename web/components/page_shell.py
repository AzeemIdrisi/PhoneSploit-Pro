"""Reusable page layout with optional tabs."""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui


def render_page(
    container,
    *,
    title: str,
    description: str,
    tabs: list[tuple[str, str, str, Callable[[], None]]] | None = None,
    content_fn: Callable[[], None] | None = None,
    title_class: str = "text-2xl font-bold text-cyan-400",
) -> None:
    """Render a page shell. Use tabs OR content_fn for single-panel pages."""
    with container:
        ui.label(title).classes(title_class)
        ui.label(description).classes("text-gray-400 mb-4")

        if content_fn is not None:
            content_fn()
            return

        if not tabs:
            return

        if len(tabs) == 1:
            _tab_id, _label, tab_desc, render_fn = tabs[0]
            ui.label(tab_desc).classes("text-sm text-gray-500 mb-3")
            render_fn()
            return

        with ui.tabs().classes("w-full") as tab_bar:
            for tab_id, label, _, _ in tabs:
                ui.tab(tab_id, label=label)

        with ui.tab_panels(tab_bar, value=tabs[0][0]).classes("w-full"):
            for tab_id, _, tab_desc, render_fn in tabs:
                with ui.tab_panel(tab_id):
                    ui.label(tab_desc).classes("text-sm text-gray-500 mb-3")
                    render_fn()
