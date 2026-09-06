import os
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from rich.console import Console
from rich.text import Text
from rich.theme import Theme

from modules.config import AppConfig

_theme = Theme(
    {
        "info": "bold cyan",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "prompt": "bold white",
        "highlight": "bold cyan",
        "muted": "dim white",
    }
)

console = Console(theme=_theme, highlight=False)

STATUS_SPINNER = "dots"


def task_status(message: str):
    """Transient operation line — Rich updates in place until the block exits."""
    return console.status(message, spinner=STATUS_SPINNER)


def _format_menu_entry(number: int, label: str) -> str:
    return f"[bold white]{number:>2}.[/bold white] [bold green]{label}[/bold green]"


def show_options(
    config: AppConfig,
    title: str,
    labels: list[str] | tuple[str, ...],
    *,
    breadcrumb: list[str] | None = None,
) -> None:
    """Clear the screen and render an option list with the shared breadcrumb
    header and vertical XX-padded indices (same style as hub submenus)."""
    clear_terminal(config)
    crumbs = breadcrumb if breadcrumb is not None else ["Main Menu", title]
    console.print(_format_submenu_header(crumbs))
    _render_menu_grid(list(labels), columns=1)


SubmenuAction = Literal["exit", "redraw", "proceed"]

_SUBMENU_COL_WIDTH = 42


def _compute_menu_layout(item_count: int) -> tuple[int, int]:
    """Return (columns, column_width). The main menu is fixed at 3 columns."""
    term_width = shutil.get_terminal_size().columns
    gaps = (3 - 1) * 2
    cw = max(item_count, (term_width - gaps) // 3)
    return 3, cw


def _pad_markup(markup: str, width: int) -> str:
    """Pad Rich markup to a visible column width (ignores escape codes)."""
    pad = max(0, width - len(Text.from_markup(markup).plain))
    return markup + " " * pad


def _cell_text(number: int, label: str, width: int) -> Text:
    """Rich Text cell exactly `width` plain chars wide, number in white, label in green.
    Labels longer than the column width are elided so they never wrap into a
    neighbouring grid cell."""
    num_part = f"{number:>2}. "
    t = Text(num_part, style="bold white")
    avail = max(0, width - len(num_part))
    if len(label) > avail:
        label = label[: max(0, avail - 1)] + "…"
    t.append(label, style="bold green")
    t.append(" " * max(0, width - len(t.plain)))
    return t


def _render_menu_grid(labels: list[str], *, columns: int = 1) -> None:
    """Render numbered menu rows in one or two columns."""
    if not labels:
        return
    if columns <= 1 or len(labels) <= 6:
        for i, label in enumerate(labels, 1):
            console.print(f"    {_format_menu_entry(i, label)}")
        return

    half = (len(labels) + 1) // 2
    left = labels[:half]
    right = labels[half:]
    for row in range(half):
        left_part = _pad_markup(_format_menu_entry(row + 1, left[row]), _SUBMENU_COL_WIDTH)
        if row < len(right):
            right_part = _pad_markup(
                _format_menu_entry(half + row + 1, right[row]), _SUBMENU_COL_WIDTH
            )
            console.print(f"    {left_part}{right_part}")
        else:
            console.print(f"    {left_part}")


def clear_terminal(config: AppConfig) -> None:
    os.system(config.clear_cmd)


def _format_submenu_header(breadcrumb: list[str]) -> str:
    """Build header: PhoneSploit Pro · Hub · Nested (skip Main Menu)."""
    parts = [p for p in breadcrumb if p != "Main Menu"]
    trail = " · ".join(parts)
    return f"\n  [bold cyan]PhoneSploit Pro[/bold cyan]  ·  [bold white]{trail}[/bold white]\n"


def render_submenu_screen(
    title: str,
    items: list[str],
    *,
    breadcrumb: list[str] | None = None,
    columns: int | None = None,
) -> None:
    """Unified submenu layout."""
    if breadcrumb:
        console.print(_format_submenu_header(breadcrumb))
    else:
        console.print(f"\n  [bold cyan]PhoneSploit Pro[/bold cyan]  ·  [bold white]{title}[/bold white]\n")
    col_count = columns if columns is not None else (2 if len(items) > 6 else 1)
    _render_menu_grid(items, columns=col_count)
    console.print("\n  [bold dim]0:[/bold dim] Back    [bold dim]99:[/bold dim] Clear")


def render_main_menu(page_items: list[tuple[int, str]]) -> None:
    """Render the single-page main menu (fixed 3-column grid)."""
    n = len(page_items)
    ncols, cw = _compute_menu_layout(n)
    per_col = [n // ncols] * ncols
    for i in range(n % ncols):
        per_col[i] += 1
    offsets = [0]
    for s in per_col:
        offsets.append(offsets[-1] + s)
    max_rows = max(per_col)
    gap = Text("  ")
    for row in range(max_rows):
        cells: list[Text] = []
        for col in range(ncols):
            idx = offsets[col] + row
            if idx < n:
                num, label = page_items[idx]
                cells.append(_cell_text(num, label, cw))
            else:
                cells.append(Text(" " * cw))
        console.print(Text.join(gap, cells))

    console.print()
    console.print("  [bold dim]99:[/bold dim] Clear   [bold dim]0:[/bold dim] Exit")


def submenu_prompt(breadcrumb: list[str]) -> str:
    trail = " › ".join(breadcrumb)
    return f"[bold red]\\[{trail}][/bold red] > "


def parse_submenu_choice(
    choice: str,
    config: AppConfig,
    reprint_fn: Callable[[], None],
    *,
    back_label: str = "Back",
) -> SubmenuAction:
    """Handle 0 (exit submenu) and 99 (clear + reprint)."""
    if choice == "0":
        clear_terminal(config)
        return "exit"
    if choice == "99":
        clear_terminal(config)
        reprint_fn()
        return "redraw"
    return "proceed"


def print_error(msg: str) -> None:
    console.print(f"[error]\\[Error][/error] [white]{msg}[/white]")


def go_back_to_main_menu(config: AppConfig, message: str = "Invalid selection") -> None:
    """Print '<message> / Going back to Main Menu' and flag the dispatch loop
    to pop back to the main menu. The main menu is rendered without clearing
    so this message stays visible on screen."""
    print_error(f"{message}\n[bold green] Going back to Main Menu[/bold green]")
    config.return_to_main = True


def print_success(msg: str) -> None:
    console.print(f"[success]{msg}[/success]")


def print_warning(msg: str) -> None:
    console.print(f"[warning]\\[Warning][/warning] [white]{msg}[/white]")


def print_info(msg: str) -> None:
    console.print(f"[info]{msg}[/info]")


def print_null_input() -> None:
    console.print("[error]Null input[/error]. [green]Returning to menu.[/green]")


def ensure_config_dir(
    config: AppConfig,
    field: str,
    default: str = "Downloaded-Files",
) -> Path:
    """If config field empty, one-line prompt; mkdir; return Path."""
    val = getattr(config, field)
    if not val:
        val = (
            ask(
                f"[bold yellow]Output folder[/bold yellow] [dim](Enter={default})[/dim]> "
            ).strip()
            or default
        )
        setattr(config, field, val)
    p = Path(val)
    p.mkdir(parents=True, exist_ok=True)
    return p


def ask(prompt: str) -> str:
    """Styled input prompt that survives terminal line editing."""
    rendered = _render_prompt(prompt)
    if _readline_is_gnu():
        rendered = _wrap_ansi_escapes(rendered)
    return input(rendered)


def _render_prompt(prompt: str) -> str:
    """Render rich-markup prompt to the ANSI string shown by input()."""
    with console.capture() as capture:
        console.print(prompt, end="")
    return capture.get()


_readline_backend_checked = False
_readline_backend_gnu = False


def _readline_is_gnu() -> bool:
    """True when the active readline is GNU readline (not libedit/None)."""
    global _readline_backend_checked, _readline_backend_gnu
    if not _readline_backend_checked:
        try:
            import readline
        except ImportError:
            _readline_backend_gnu = False
        else:
            _readline_backend_gnu = "GNU" in (getattr(readline, "__doc__", "") or "")
        _readline_backend_checked = True
    return _readline_backend_gnu


_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def _wrap_ansi_escapes(text: str) -> str:
    """Wrap ANSI escapes in \\x01..\\x02 so GNU readline ignores their width."""
    return _ANSI_ESCAPE.sub(lambda m: f"\x01{m.group(0)}\x02", text)


def confirm(prompt: str = "Do you want to continue?") -> bool:
    """Ask Y/N confirmation. Returns True for yes/enter, False for no."""
    choice = ask(f"\n[bold white]{prompt}     Y / N[/bold white] > ").lower()
    while choice not in ("y", "n", ""):
        choice = ask("[error]Invalid choice![/error] Press Y or N > ").lower()
    return choice in ("y", "")


def open_file_prompt(opener: str, path: str) -> None:
    """Ask user if they want to open the resulting file."""
    if confirm("Do you want to open the file?"):
        subprocess.run([opener, path], check=False)


_adb_executable: str | None = None


def set_adb_executable(path: str | None) -> None:
    """Set after tools.resolve_external_tools; None means ADB was not found."""
    global _adb_executable
    _adb_executable = path


def get_adb_executable() -> str | None:
    """Resolved adb path from startup, or None if not available."""
    return _adb_executable


def adb(args: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    """
    Run an adb command.
    - capture=True  → stdout/stderr captured, returned (use for data queries)
    - capture=False → output streams to terminal (use for interactive commands)
    """
    if _adb_executable is None:
        return subprocess.CompletedProcess(
            args=[],
            returncode=127,
            stdout="",
            stderr="adb not available",
        )
    cmd = [_adb_executable] + args
    if capture:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    return subprocess.run(cmd)


def adb_output(args: list[str]) -> str:
    """Run an adb command and return stripped stdout."""
    return adb(args).stdout.strip()
