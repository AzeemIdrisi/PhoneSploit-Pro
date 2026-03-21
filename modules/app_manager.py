from pathlib import Path
from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_null_input,
    confirm,
    task_status,
    submenu_row,
    ensure_config_dir,
    adb,
    adb_output,
)


def _list_third_party_apps() -> list[str]:
    """Return list of third-party package names."""
    raw = adb_output(["shell", "pm", "list", "packages", "-3"])
    return [line.replace("package:", "").strip() for line in raw.splitlines() if line.strip()]


def select_package_from_list() -> str | None:
    """Display numbered third-party app list; return package name or None."""
    return _select_app_from_list()


def _select_app_from_list() -> str | None:
    """Display numbered app list, return selected package name or None."""
    app_list = _list_third_party_apps()
    if not app_list:
        console.print("[yellow]No third-party apps found.[/yellow]")
        return None

    table = Table(title="Installed Third-Party Apps", show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold green", justify="right")
    table.add_column("Package Name", style="white")

    for i, pkg in enumerate(app_list, 1):
        table.add_row(str(i), pkg)

    console.print(table)
    selection = console.input("[prompt]Enter Selection > [/prompt]")
    if not selection.isdigit():
        print_error("Expected an Integer Value\n[green] Going back to Main Menu[/green]")
        return None
    idx = int(selection)
    if idx < 1 or idx > len(app_list):
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return None
    return app_list[idx - 1]


def install_app(config: AppConfig) -> None:
    file_location = console.input("[cyan]APK path on computer[/cyan] > ").strip()

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

    with task_status(f"[info]Installing {apk_path.name}…[/info]"):
        result = adb(["install", str(apk_path)])

    output = (result.stdout + result.stderr).strip()
    if "Success" in output:
        print_success(f"Installed: {apk_path.name}")
    else:
        print_error(f"Installation failed: {output}")


def uninstall_app(config: AppConfig) -> None:
    submenu_row("Select from app list", "Enter package name manually")
    mode = console.input("[prompt]> [/prompt]")

    if mode == "1":
        package_name = _select_app_from_list()
        if not package_name:
            return
    elif mode == "2":
        package_name = console.input(
            "[cyan]Package name[/cyan] [dim](e.g. com.spotify.music)[/dim]> "
        ).strip()
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

    with task_status(f"[info]Uninstalling {package_name}…[/info]"):
        result = adb(["uninstall", package_name])

    output = (result.stdout + result.stderr).strip()
    if "Success" in output:
        print_success(f"Uninstalled: {package_name}")
    else:
        print_error(f"Uninstall failed: {output}")


def launch_app(config: AppConfig) -> None:
    submenu_row("Select from app list", "Enter package name manually")
    mode = console.input("[prompt]> [/prompt]")

    if mode == "1":
        package_name = _select_app_from_list()
        if not package_name:
            return
    elif mode == "2":
        package_name = console.input(
            "[cyan]Package name[/cyan] [dim](e.g. com.spotify.music)[/dim]> "
        ).strip()
        if not package_name:
            print_null_input()
            return
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return

    with task_status(f"[info]Launching {package_name}…[/info]"):
        adb(["shell", "monkey", "-p", package_name, "1"])
    print_success(f"Launched: {package_name}")


def list_apps(config: AppConfig) -> None:
    submenu_row("Third-party packages only", "All packages")
    mode = console.input("[prompt]> [/prompt]")

    if mode == "1":
        with task_status("[info]Fetching third-party packages…[/info]"):
            app_list = _list_third_party_apps()
        title = "Third-Party Apps"
    elif mode == "2":
        with task_status("[info]Fetching all packages…[/info]"):
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

    console.print(table)


def extract_apk(config: AppConfig) -> None:
    submenu_row("Select from app list", "Enter package name manually")
    mode = console.input("[prompt]> [/prompt]")

    if mode == "1":
        package_name = _select_app_from_list()
        if not package_name:
            return
    elif mode == "2":
        package_name = console.input(
            "[cyan]Package name[/cyan] [dim](e.g. com.spotify.music)[/dim]> "
        ).strip()
        if not package_name:
            print_null_input()
            return
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return

    if not confirm(
        f"Extract APK for [yellow]{package_name}[/yellow] to your computer? "
        "An existing file with the same name may be overwritten."
    ):
        return

    save_dir = ensure_config_dir(config, "pull_location")
    file_name = package_name.replace(".", "_") + ".apk"
    dest = save_dir / file_name

    with task_status(f"[info]Querying APK path for {package_name}…[/info]"):
        path_output = adb_output(["shell", "pm", "path", package_name])

    lines = [l.strip() for l in path_output.splitlines() if l.strip().startswith("package:")]
    paths = [l.replace("package:", "").strip() for l in lines]
    if not paths:
        print_error(f"App not found: {package_name}")
        return

    apk_path = None
    for p in paths:
        if p.endswith("base.apk") or "/base.apk" in p:
            apk_path = p
            break
    if apk_path is None:
        apk_path = paths[0]

    with task_status(f"[info]Pulling {Path(apk_path).name}…[/info]"):
        pull_result = adb(["pull", apk_path])

    if pull_result.returncode != 0:
        print_error((pull_result.stdout + pull_result.stderr).strip() or "adb pull failed.")
        return

    pulled_name = Path(apk_path).name
    src = Path(pulled_name)
    if not src.is_file() and Path("base.apk").is_file():
        src = Path("base.apk")

    ok = False
    with task_status("[info]Moving into output folder…[/info]"):
        try:
            if src.is_file():
                src.rename(dest)
                ok = dest.is_file()
            else:
                print_error("Pulled APK not found in current directory after adb pull.")
        except FileExistsError:
            print_error(f"APK already exists at {dest}")
        except OSError as e:
            print_error(str(e))
    if ok:
        print_success(f"Saved to: {dest}")
