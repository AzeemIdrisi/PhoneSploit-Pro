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
            console.input(
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
    """Styled input prompt."""
    return console.input(f"[prompt]{prompt}[/prompt]")


def confirm(prompt: str = "Do you want to continue?") -> bool:
    """Ask Y/N confirmation. Returns True for yes/enter, False for no."""
    choice = console.input(f"\n[white]{prompt}     [bold]Y / N[/bold][/white] > ").lower()
    while choice not in ("y", "n", ""):
        choice = console.input("[error]Invalid choice![/error] Press Y or N > ").lower()
    return choice in ("y", "")


def open_file_prompt(opener: str, path: str) -> None:
    """Ask user if they want to open the resulting file."""
    if confirm("Do you want to open the file?"):
        subprocess.run([opener, path], check=False)


def adb(args: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    """
    Run an adb command.
    - capture=True  → stdout/stderr captured, returned (use for data queries)
    - capture=False → output streams to terminal (use for interactive commands)
    """
    cmd = ["adb"] + args
    if capture:
        return subprocess.run(cmd, capture_output=True, text=True)
    return subprocess.run(cmd)


def adb_output(args: list[str]) -> str:
    """Run an adb command and return stripped stdout."""
    return adb(args).stdout.strip()
