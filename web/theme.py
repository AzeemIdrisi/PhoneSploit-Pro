"""Theme and typography tokens for the web UI."""

from __future__ import annotations

import json

DEFAULT_THEME = "dark"
DEFAULT_FONT = "system"

THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "label": "Dark",
        "bg": "#0d1117",
        "surface": "#161b22",
        "border": "#30363d",
        "accent": "#58a6ff",
        "success": "#3fb950",
        "warning": "#d29922",
        "error": "#f85149",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "terminal_bg": "#010409",
        "terminal_text": "#3fb950",
    },
    "light": {
        "label": "Light",
        "bg": "#f6f8fa",
        "surface": "#ffffff",
        "border": "#d0d7de",
        "accent": "#0969da",
        "success": "#1a7f37",
        "warning": "#9a6700",
        "error": "#cf222e",
        "text": "#1f2328",
        "muted": "#656d76",
        "terminal_bg": "#24292f",
        "terminal_text": "#7ee787",
    },
    "midnight": {
        "label": "Midnight",
        "bg": "#050810",
        "surface": "#0c1220",
        "border": "#1e293b",
        "accent": "#22d3ee",
        "success": "#34d399",
        "warning": "#fbbf24",
        "error": "#f87171",
        "text": "#e2e8f0",
        "muted": "#94a3b8",
        "terminal_bg": "#020617",
        "terminal_text": "#34d399",
    },
}

# Professional sans-serif stacks only — no decorative or cursive fonts.
FONTS: dict[str, dict[str, str | None]] = {
    "system": {
        "label": "System",
        "sans": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
        "mono": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace",
        "href": None,
    },
    "inter": {
        "label": "Inter",
        "sans": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "mono": "'JetBrains Mono', ui-monospace, Menlo, Monaco, Consolas, monospace",
        "href": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
    },
    "roboto": {
        "label": "Roboto",
        "sans": "'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "mono": "'Roboto Mono', ui-monospace, Menlo, Monaco, Consolas, monospace",
        "href": "https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap",
    },
    "ibm-plex": {
        "label": "IBM Plex Sans",
        "sans": "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "mono": "'IBM Plex Mono', ui-monospace, Menlo, Monaco, Consolas, monospace",
        "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap",
    },
    "source-sans": {
        "label": "Source Sans 3",
        "sans": "'Source Sans 3', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "mono": "'Source Code Pro', ui-monospace, Menlo, Monaco, Consolas, monospace",
        "href": "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&family=Source+Code+Pro:wght@400;500&display=swap",
    },
    "noto-sans": {
        "label": "Noto Sans",
        "sans": "'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "mono": "'Noto Sans Mono', ui-monospace, Menlo, Monaco, Consolas, monospace",
        "href": "https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&family=Noto+Sans+Mono:wght@400;500&display=swap",
    },
}

STORAGE_THEME = "psp_theme"
STORAGE_FONT = "psp_font"


def theme_options() -> dict[str, str]:
    return {key: spec["label"] for key, spec in THEMES.items()}


def font_options() -> dict[str, str]:
    return {key: spec["label"] for key, spec in FONTS.items()}


def _theme_block(theme_id: str, spec: dict[str, str]) -> str:
    selector = f'html[data-psp-theme="{theme_id}"]'
    return f"""
{selector} {{
    --psp-bg: {spec["bg"]};
    --psp-surface: {spec["surface"]};
    --psp-border: {spec["border"]};
    --psp-accent: {spec["accent"]};
    --psp-success: {spec["success"]};
    --psp-warning: {spec["warning"]};
    --psp-error: {spec["error"]};
    --psp-text: {spec["text"]};
    --psp-muted: {spec["muted"]};
    --psp-terminal-bg: {spec["terminal_bg"]};
    --psp-terminal-text: {spec["terminal_text"]};
}}
"""


def _font_block(font_id: str, spec: dict[str, str | None]) -> str:
    selector = f'html[data-psp-font="{font_id}"]'
    return f"""
{selector} {{
    --psp-font-sans: {spec["sans"]};
    --psp-font-mono: {spec["mono"]};
}}
"""


def build_css() -> str:
    theme_css = "".join(_theme_block(key, spec) for key, spec in THEMES.items())
    font_css = "".join(_font_block(key, spec) for key, spec in FONTS.items())
    return f"""
html {{
    color-scheme: dark;
}}
html[data-psp-theme="dark"],
html:not([data-psp-theme]) {{
    color-scheme: dark;
}}
html[data-psp-theme="light"] {{
    color-scheme: light;
}}
{theme_css}
{font_css}

body, .nicegui-content, .q-body--force-scrollbar-y, .q-page {{
    background-color: var(--psp-bg) !important;
    color: var(--psp-text) !important;
    font-family: var(--psp-font-sans) !important;
}}

.psp-sidebar {{
    background: var(--psp-surface) !important;
    border-right: 1px solid var(--psp-border);
}}

.psp-sidebar .q-drawer__content {{
    display: flex !important;
    flex-direction: column !important;
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
}}

.psp-sidebar-inner {{
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
    overflow: hidden;
}}

.psp-sidebar-nav {{
    flex: 1 1 auto;
    min-height: 0;
    width: 100%;
}}

.psp-topbar {{
    background: var(--psp-surface) !important;
    border-bottom: 1px solid var(--psp-border);
}}

.psp-version-badge {{
    background: color-mix(in srgb, var(--psp-accent) 18%, var(--psp-surface));
    color: var(--psp-accent);
}}

.psp-card {{
    background: var(--psp-surface) !important;
    border: 1px solid var(--psp-border) !important;
    border-radius: 8px;
    padding: 1rem;
}}

.psp-mono {{
    font-family: var(--psp-font-mono) !important;
    font-size: 0.85rem;
}}

.psp-text-link {{
    color: var(--psp-muted) !important;
    text-decoration: none;
}}

.psp-text-link:hover {{
    color: var(--psp-accent) !important;
}}

.psp-icon-link {{
    color: var(--psp-muted);
    text-decoration: none;
    border-radius: 9999px;
    padding: 0.25rem;
}}

.psp-icon-link:hover {{
    color: var(--psp-accent);
    background: color-mix(in srgb, var(--psp-accent) 12%, transparent);
}}

.psp-terminal {{
    background: var(--psp-terminal-bg) !important;
    color: var(--psp-terminal-text) !important;
    min-height: 200px;
    max-height: 320px;
    overflow-y: auto;
    padding: 0.75rem;
    border: 1px solid var(--psp-border);
    border-radius: 6px;
    font-family: var(--psp-font-mono) !important;
}}

.q-drawer, .q-page-container {{
    background: var(--psp-bg) !important;
}}

html[data-psp-theme="light"] .text-gray-400,
html[data-psp-theme="light"] .text-gray-500,
html[data-psp-theme="light"] .text-gray-600 {{
    color: var(--psp-muted) !important;
}}

html[data-psp-theme="light"] .border-gray-800 {{
    border-color: var(--psp-border) !important;
}}
"""


def bootstrap_script() -> str:
    font_hrefs = {key: spec["href"] for key, spec in FONTS.items() if spec["href"]}
    return f"""
<script>
(function() {{
  const theme = localStorage.getItem({json.dumps(STORAGE_THEME)}) || {json.dumps(DEFAULT_THEME)};
  const font = localStorage.getItem({json.dumps(STORAGE_FONT)}) || {json.dumps(DEFAULT_FONT)};
  document.documentElement.setAttribute('data-psp-theme', theme);
  document.documentElement.setAttribute('data-psp-font', font);
  const hrefs = {json.dumps(font_hrefs)};
  const href = hrefs[font];
  if (href) {{
    const link = document.createElement('link');
    link.id = 'psp-font-link';
    link.rel = 'stylesheet';
    link.href = href;
    document.head.appendChild(link);
  }}
}})();
</script>
"""


def apply_preferences_js(theme_id: str, font_id: str) -> str:
    if theme_id not in THEMES:
        theme_id = DEFAULT_THEME
    if font_id not in FONTS:
        font_id = DEFAULT_FONT
    font_hrefs = {key: spec["href"] for key, spec in FONTS.items()}
    return f"""
(() => {{
  const theme = {json.dumps(theme_id)};
  const font = {json.dumps(font_id)};
  const hrefs = {json.dumps(font_hrefs)};
  document.documentElement.setAttribute('data-psp-theme', theme);
  document.documentElement.setAttribute('data-psp-font', font);
  localStorage.setItem({json.dumps(STORAGE_THEME)}, theme);
  localStorage.setItem({json.dumps(STORAGE_FONT)}, font);
  let link = document.getElementById('psp-font-link');
  const href = hrefs[font] || null;
  if (href) {{
    if (!link) {{
      link = document.createElement('link');
      link.id = 'psp-font-link';
      link.rel = 'stylesheet';
      document.head.appendChild(link);
    }}
    link.href = href;
  }} else if (link) {{
    link.remove();
  }}
}})();
"""
