import os
import re
import select
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
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


def print_submenu_header(*titles: str) -> None:
    """Print breadcrumb header for content screens (Main Menu is implied)."""
    console.print(_format_submenu_header(["Main Menu", *titles]))


def print_option_list(labels: list[str] | tuple[str, ...]) -> None:
    """Numbered option rows matching show_options, without clearing the screen."""
    _render_menu_grid(list(labels), columns=1)


def _is_termux() -> bool:
    if os.environ.get("TERMUX_VERSION"):
        return True
    return os.path.isdir("/data/data/com.termux/files/usr")


def _print_menu_footer(*, main_menu: bool) -> None:
    """Termux: typed 0/99. Desktop: keyboard shortcuts only (no 0/99 in footer)."""
    if _is_termux():
        if main_menu:
            console.print(
                "  [bold dim]0:[/bold dim] Exit  [bold dim]99:[/bold dim] Clear  "
                "[bold dim]/[/bold dim] Search"
            )
        else:
            console.print(
                "\n  [bold dim]0:[/bold dim] Back  [bold dim]99:[/bold dim] Clear"
            )
        return
    if main_menu:
        console.print(
            "  [bold dim]Ctrl+D[/bold dim] Exit  [bold dim]Ctrl+L[/bold dim] Clear  "
            "[bold dim]Ctrl+C[/bold dim] Cancel input  [bold dim]/[/bold dim] Search"
        )
    else:
        console.print(
            "\n  [bold dim]ESC[/bold dim] Back  [bold dim]Ctrl+L[/bold dim] Clear  "
            "[bold dim]Ctrl+C[/bold dim] Cancel  [bold dim]Ctrl+D[/bold dim] Exit"
        )


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
    _print_menu_footer(main_menu=False)


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
    _print_menu_footer(main_menu=True)


_IPV4_ADB_SERIAL = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?$")


def _is_ipv4_adb_serial(serial: str) -> bool:
    if not _IPV4_ADB_SERIAL.match(serial):
        return False
    host = serial.rsplit(":", 1)[0]
    return all(0 <= int(octet) <= 255 for octet in host.split("."))


def format_device_suffix(max_len: int = 14) -> str:
    """ANDROID_SERIAL in prompts; full IPv4:port, truncated USB serials."""
    serial = os.environ.get("ANDROID_SERIAL", "").strip()
    if not serial:
        return " [dim]no device[/dim]"
    if _is_ipv4_adb_serial(serial) or len(serial) <= max_len:
        shown = serial
    else:
        head = max(4, (max_len - 1) // 2)
        tail = max_len - head - 1
        shown = f"{serial[:head]}…{serial[-tail:]}"
    return f" [bold cyan]·[/bold cyan] [bold white]{shown}[/bold white]"


def main_menu_prompt() -> str:
    return f"[bold red]\\[Main Menu{format_device_suffix()}][/bold red] > "


def submenu_prompt(breadcrumb: list[str]) -> str:
    trail = " › ".join(breadcrumb)
    return f"[bold red]\\[{trail}{format_device_suffix()}][/bold red] > "


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
    console.print("[muted]Cancelled.[/muted] [green]Returning to menu.[/green]")


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


CommandKind = Literal["submit", "back", "cancel", "eof", "search"]


@dataclass(frozen=True)
class CommandInput:
    kind: CommandKind
    text: str = ""


_INPUT_HISTORY: list[str] = []
_HISTORY_INDEX: int = -1
_ESC_FOLLOWUP_SEC = 0.08


def _stdin_is_tty() -> bool:
    try:
        return sys.stdin.isatty()
    except Exception:
        return False


def _can_raw_read() -> bool:
    if not _stdin_is_tty():
        return False
    if os.name == "nt":
        try:
            import msvcrt  # noqa: F401
        except ImportError:
            return False
        return True
    try:
        import termios  # noqa: F401
        import tty  # noqa: F401
    except ImportError:
        return False
    return True


def _read_char_unix(timeout: float | None = None) -> str | None:
    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        if timeout is not None:
            ready, _, _ = select.select([sys.stdin], [], [], timeout)
            if not ready:
                return None
        ch = sys.stdin.read(1)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _read_char_windows() -> str:
    import msvcrt

    ch = msvcrt.getwch()
    if ch in ("\x00", "\xe0"):
        msvcrt.getwch()
        return ""
    return ch


def _read_char_raw(timeout: float | None = None) -> str | None:
    if os.name == "nt":
        return _read_char_windows()
    return _read_char_unix(timeout)


def _redraw_input_line(prompt: str, buffer: str) -> None:
    rendered = _render_prompt(prompt)
    plain_prompt = Text.from_markup(prompt).plain
    sys.stdout.write("\r" + " " * (len(plain_prompt) + len(buffer) + 4))
    sys.stdout.write("\r" + rendered + buffer)
    sys.stdout.flush()


def _read_line_interactive(
    prompt: str,
    *,
    config: AppConfig | None = None,
    on_clear: Callable[[], None] | None = None,
    allow_esc_back: bool = False,
    esc_noop: bool = False,
    allow_search: bool = False,
) -> CommandInput:
    """Raw TTY line editor; returns structured command results."""
    global _HISTORY_INDEX
    rendered = _render_prompt(prompt)
    buffer = ""
    _HISTORY_INDEX = len(_INPUT_HISTORY)

    sys.stdout.write(rendered)
    sys.stdout.flush()

    while True:
        if os.name == "nt":
            ch = _read_char_raw()
            if ch is None:
                ch = ""
        else:
            ch = _read_char_raw()

        if ch is None:
            continue

        if ch == "\x04":  # Ctrl+D
            if not buffer:
                sys.stdout.write("\n")
                sys.stdout.flush()
                return CommandInput("eof")
            continue

        if ch == "\x03":  # Ctrl+C
            sys.stdout.write("\n")
            sys.stdout.flush()
            return CommandInput("cancel")

        if ch == "\x0c":  # Ctrl+L
            if config is not None:
                clear_terminal(config)
            if on_clear is not None:
                on_clear()
            else:
                sys.stdout.write(rendered)
                sys.stdout.flush()
            _redraw_input_line(prompt, buffer)
            continue

        if ch in ("\r", "\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
            text = buffer.strip()
            if allow_search and text.startswith("/"):
                return CommandInput("search", text[1:].strip())
            if buffer and (_HISTORY_INDEX >= len(_INPUT_HISTORY) or _INPUT_HISTORY[-1] != buffer):
                _INPUT_HISTORY.append(buffer)
                if len(_INPUT_HISTORY) > 100:
                    del _INPUT_HISTORY[0]
            return CommandInput("submit", buffer)

        if ch == "\x7f" or ch == "\b":
            if buffer:
                buffer = buffer[:-1]
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            continue

        if ch == "\x1b":
            if os.name == "nt":
                if allow_esc_back:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return CommandInput("back")
                if not esc_noop:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return CommandInput("cancel")
                continue
            follow = _read_char_raw(timeout=_ESC_FOLLOWUP_SEC)
            if follow is None:
                if allow_esc_back:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return CommandInput("back")
                if esc_noop:
                    continue
                sys.stdout.write("\n")
                sys.stdout.flush()
                return CommandInput("cancel")
            if follow == "[":
                seq = ""
                while True:
                    c = _read_char_raw(timeout=0.05)
                    if c is None or not c:
                        break
                    seq += c
                    if 0x40 <= ord(c) <= 0x7E:
                        break
                if seq.endswith("A") and _INPUT_HISTORY:
                    _HISTORY_INDEX = max(0, _HISTORY_INDEX - 1)
                    buffer = _INPUT_HISTORY[_HISTORY_INDEX]
                    _redraw_input_line(prompt, buffer)
                elif seq.endswith("B") and _INPUT_HISTORY:
                    _HISTORY_INDEX = min(len(_INPUT_HISTORY), _HISTORY_INDEX + 1)
                    buffer = (
                        _INPUT_HISTORY[_HISTORY_INDEX]
                        if _HISTORY_INDEX < len(_INPUT_HISTORY)
                        else ""
                    )
                    _redraw_input_line(prompt, buffer)
            continue

        if len(ch) == 1 and ord(ch) >= 32:
            buffer += ch
            sys.stdout.write(ch)
            sys.stdout.flush()
    return CommandInput("eof")


def _read_line_fallback(prompt: str, *, allow_search: bool = False) -> CommandInput:
    rendered = _render_prompt(prompt)
    if _readline_is_gnu():
        rendered = _wrap_ansi_escapes(rendered)
    try:
        line = input(rendered)
    except EOFError:
        return CommandInput("eof")
    except KeyboardInterrupt:
        console.print()
        return CommandInput("cancel")
    text = line.strip()
    if allow_search and text.startswith("/"):
        return CommandInput("search", text[1:].strip())
    return CommandInput("submit", line)


def read_command(
    prompt: str,
    config: AppConfig,
    *,
    on_clear: Callable[[], None] | None = None,
    allow_esc_back: bool = False,
    esc_noop: bool = False,
    allow_search: bool = False,
) -> CommandInput:
    """Menu-oriented line input with hotkeys."""
    if _can_raw_read():
        return _read_line_interactive(
            prompt,
            config=config,
            on_clear=on_clear,
            allow_esc_back=allow_esc_back,
            esc_noop=esc_noop,
            allow_search=allow_search,
        )
    return _read_line_fallback(prompt, allow_search=allow_search)


def ask(prompt: str) -> str:
    """Styled input prompt that survives terminal line editing."""
    if _can_raw_read():
        result = _read_line_interactive(prompt, esc_noop=False)
        if result.kind in ("cancel", "back"):
            return ""
        if result.kind == "eof":
            return ""
        if result.kind == "search":
            return result.text
        return result.text
    rendered = _render_prompt(prompt)
    if _readline_is_gnu():
        rendered = _wrap_ansi_escapes(rendered)
    try:
        return input(rendered)
    except KeyboardInterrupt:
        console.print()
        return ""
    except EOFError:
        return ""


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
    """Ask Y/N confirmation. Enter = Yes; N / ESC / Ctrl+C = No."""
    prompt_markup = (
        f"\n[bold white]{prompt}     Y / N  [dim][Enter = Yes][/dim][/bold white] > "
    )
    while True:
        if _can_raw_read():
            result = _read_line_interactive(prompt_markup, esc_noop=False)
            if result.kind in ("cancel", "back", "eof"):
                return False
            choice = result.text.strip().lower()
        else:
            rendered = _render_prompt(prompt_markup)
            if _readline_is_gnu():
                rendered = _wrap_ansi_escapes(rendered)
            try:
                choice = input(rendered).strip().lower()
            except KeyboardInterrupt:
                console.print()
                return False
            except EOFError:
                return False
        if choice in ("y", ""):
            return True
        if choice in ("n",):
            return False
        prompt_markup = "[error]Invalid choice![/error] Press Y or N > "


def open_path(opener: str, path: str) -> None:
    """Open a file with the platform default handler."""
    try:
        if os.name == "nt":
            os.startfile(os.path.normpath(path))  # type: ignore[attr-defined]
        else:
            subprocess.run([opener, path], check=False)
    except OSError:
        print_error(f"Could not open: {path}")


def open_file_prompt(opener: str, path: str) -> None:
    """Ask user if they want to open the resulting file."""
    if confirm("Do you want to open the file?"):
        open_path(opener, path)


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
