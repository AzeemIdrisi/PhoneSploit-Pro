import subprocess
from contextlib import contextmanager
from rich.console import Console
from rich.theme import Theme

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


def print_error(msg: str) -> None:
    console.print(f"[error]\\[Error][/error] [white]{msg}[/white]")


def print_success(msg: str) -> None:
    console.print(f"[success]{msg}[/success]")


def print_warning(msg: str) -> None:
    console.print(f"[warning]\\[Warning][/warning] [white]{msg}[/white]")


def print_info(msg: str) -> None:
    console.print(f"[info]{msg}[/info]")


def print_null_input() -> None:
    console.print("\n[error] Null Input[/error]\n[success] Going back to Main Menu[/success]")


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
