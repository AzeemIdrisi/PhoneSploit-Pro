import re
import subprocess
from pathlib import Path
from typing import Literal

from rich.console import Console
from rich.theme import Theme

from modules.config import AppConfig

_theme = Theme(
    {
        "info": "cyan",
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


def submenu_row(*labels: str) -> None:
    """Compact one-line submenu: 1) …  2) …"""
    parts = [f"[dim]{i}[/dim] {text}" for i, text in enumerate(labels, 1)]
    console.print("  " + "   ".join(parts))


_ConfigDirAttr = Literal["pull_location", "screenshot_location", "screenrecord_location"]


def ensure_config_dir(
    config: AppConfig,
    field: _ConfigDirAttr,
    default: str = "Downloaded-Files",
) -> Path:
    """If config field empty, one-line prompt; mkdir; return Path."""
    val = getattr(config, field)
    if not val:
        val = (
            ask(
                f"[yellow]Output folder[/yellow] [dim](Enter={default})[/dim]> "
            ).strip()
            or default
        )
        setattr(config, field, val)
    p = Path(val)
    p.mkdir(parents=True, exist_ok=True)
    return p


def print_error(msg: str) -> None:
    console.print(f"[error]\\[Error][/error] [white]{msg}[/white]")


def print_success(msg: str) -> None:
    console.print(f"[success]{msg}[/success]")


def print_warning(msg: str) -> None:
    console.print(f"[warning]\\[Warning][/warning] [white]{msg}[/white]")


def print_info(msg: str) -> None:
    console.print(f"[info]{msg}[/info]")


def print_null_input() -> None:
    console.print("[error]Null input[/error]. [green]Returning to menu.[/green]")


def ask(prompt: str) -> str:
    """Styled input prompt that survives terminal line editing.

    readline redraws the entire line when you edit (backspace, arrow keys), so
    the prompt must be handed to readline itself via ``input()`` rather than
    printed beforehand — otherwise the redraw erases it. GNU readline miscounts
    the width of ANSI escape codes, so those are wrapped in the ``\\x01`` /
    ``\\x02`` markers readline ignores when measuring the prompt.
    """
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
    choice = ask(f"\n[white]{prompt}     [bold]Y / N[/bold][/white] > ").lower()
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
