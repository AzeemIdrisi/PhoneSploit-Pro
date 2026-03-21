import subprocess
from pathlib import Path
from rich.table import Table

from modules.config import AppConfig
from modules.console import console, print_error, print_success, print_null_input, confirm, adb, adb_output


def _list_third_party_apps() -> list[str]:
    """Return list of third-party package names."""
    raw = adb_output(["shell", "pm", "list", "packages", "-3"])
    return [line.replace("package:", "").strip() for line in raw.splitlines() if line.strip()]


def _select_app_from_list() -> str | None:
    """Display numbered app list, return selected package name or None."""
    app_list = _list_third_party_apps()
    if not app_list:
        console.print("\n[yellow]No third-party apps found.[/yellow]\n")
        return None

    table = Table(title="Installed Third-Party Apps", show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold green", justify="right")
    table.add_column("Package Name", style="white")

    for i, pkg in enumerate(app_list, 1):
        table.add_row(str(i), pkg)

    console.print()
    console.print(table)

    selection = console.input("\n[prompt]Enter Selection > [/prompt]")
    if not selection.isdigit():
        print_error("Expected an Integer Value\n[green] Going back to Main Menu[/green]")
        return None
    idx = int(selection)
    if idx < 1 or idx > len(app_list):
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return None
    return app_list[idx - 1]


def install_app(config: AppConfig) -> None:
    file_location = console.input(f"\n[cyan]Enter APK path in computer[/cyan] > ").strip()

    if not file_location:
        print_null_input()
        return

    file_location = file_location.rstrip().strip("'\"")
    apk_path = Path(file_location)

    if not apk_path.is_file():
        print_error("This file does not exist.")
        return

    if not confirm(
        f"Install [cyan]{apk_path.name}[/cyan] on the connected device? "
        "This may replace an existing installation."
    ):
        return

    with console.status(f"[info]Installing {apk_path.name}...[/info]"):
        result = subprocess.run(
            ["adb", "install", str(apk_path)],
            capture_output=True,
            text=True,
        )

    output = (result.stdout + result.stderr).strip()
    if "Success" in output:
        print_success(f"Installed: {apk_path.name}")
    else:
        print_error(f"Installation failed:\n{output}")
    console.print()


def uninstall_app(config: AppConfig) -> None:
    console.print(
        "\n    [white]1. [green]Select from App List\n"
        "    [white]2. [green]Enter Package Name Manually[/green]\n"
    )
    mode = console.input("[prompt]> [/prompt]")

    if mode == "1":
        package_name = _select_app_from_list()
        if not package_name:
            return
    elif mode == "2":
        console.print(f"\n[cyan]Enter package name     [white]Example : com.spotify.music [/white][/cyan]")
        package_name = console.input("[prompt]> [/prompt]")
        if not package_name:
            print_null_input()
            return
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return

    if not confirm(
        f"Uninstall [yellow]{package_name}[/yellow] from the device? "
        "This removes the app and its user data."
    ):
        return

    console.print(f"\n[red]Uninstalling [yellow]{package_name}[/yellow]...[/red]")
    with console.status(f"[info]Uninstalling {package_name}...[/info]"):
        result = adb(["uninstall", package_name])

    output = (result.stdout + result.stderr).strip()
    if "Success" in output:
        print_success(f"Uninstalled: {package_name}")
    else:
        print_error(f"Uninstall failed:\n{output}")
    console.print()


def launch_app(config: AppConfig) -> None:
    console.print(
        "\n    [white]1. [green]Select from App List\n"
        "    [white]2. [green]Enter Package Name Manually[/green]\n"
    )
    mode = console.input("[prompt]> [/prompt]")

    if mode == "1":
        package_name = _select_app_from_list()
        if not package_name:
            return
    elif mode == "2":
        console.print(f"\n[cyan]Enter package name     [white]Example : com.spotify.music [/white][/cyan]")
        package_name = console.input("[prompt]> [/prompt]")
        if not package_name:
            print_null_input()
            return
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return

    with console.status(f"[info]Launching {package_name}...[/info]"):
        adb(["shell", "monkey", "-p", package_name, "1"])
    print_success(f"Launched: {package_name}")
    console.print()


def list_apps(config: AppConfig) -> None:
    console.print(
        "\n    [white]1. [green]List third party packages\n"
        "    [white]2. [green]List all packages[/green]\n"
    )
    mode = console.input("[prompt]> [/prompt]")

    if mode == "1":
        with console.status("[info]Fetching third-party packages...[/info]"):
            app_list = _list_third_party_apps()
        title = "Third-Party Apps"
    elif mode == "2":
        with console.status("[info]Fetching all packages...[/info]"):
            raw = adb_output(["shell", "pm", "list", "packages"])
            app_list = [line.replace("package:", "").strip() for line in raw.splitlines() if line.strip()]
        title = "All Installed Packages"
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return

    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold green", justify="right")
    table.add_column("Package Name", style="white")

    for i, pkg in enumerate(app_list, 1):
        table.add_row(str(i), pkg)

    console.print()
    console.print(table)
    console.print()


def extract_apk(config: AppConfig) -> None:
    console.print(
        "\n    [white]1. [green]Select from App List\n"
        "    [white]2. [green]Enter Package Name Manually[/green]\n"
    )
    mode = console.input("[prompt]> [/prompt]")

    if mode == "1":
        package_name = _select_app_from_list()
        if not package_name:
            return
        console.print(f"\n[red]Extracting [yellow]{package_name}[/yellow]...[/red]")
    elif mode == "2":
        console.print(f"\n[cyan]Enter package name     [white]Example : com.spotify.music [/white][/cyan]")
        package_name = console.input("[prompt]> [/prompt]")
        if not package_name:
            print_null_input()
            return
        console.print(f"\n[red]Extracting [yellow]{package_name}[/yellow]...[/red]")
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return

    if not confirm(
        f"Extract APK for [yellow]{package_name}[/yellow] to your computer? "
        "An existing file with the same name may be overwritten."
    ):
        return

    if not config.pull_location:
        console.print("\n[yellow]Enter location to save APK file, Press 'Enter' for default[/yellow]")
        config.pull_location = console.input("[prompt]> [/prompt]")
    if not config.pull_location:
        config.pull_location = "Downloaded-Files"
        console.print(f"\n[purple]Saving APK to PhoneSploit-Pro/{config.pull_location}[/purple]\n")
    else:
        console.print(f"\n[purple]Saving APK to {config.pull_location}[/purple]\n")

    save_dir = Path(config.pull_location)
    save_dir.mkdir(parents=True, exist_ok=True)

    with console.status(f"[info]Extracting APK for {package_name}...[/info]"):
        path_output = adb_output(["shell", "pm", "path", package_name])
        apk_path = path_output.replace("package:", "").strip()

        if not apk_path:
            print_error(f"App not found: {package_name}")
            return

        pull_result = adb(["pull", apk_path])

    file_name = package_name.replace(".", "_") + ".apk"
    dest = save_dir / file_name
    try:
        Path("base.apk").rename(dest)
        print_success(f"Saved to: {dest}")
    except FileNotFoundError:
        print_error("APK file not found after pull.")
    except FileExistsError:
        print_error(f"APK already exists at {dest}")
    console.print()
