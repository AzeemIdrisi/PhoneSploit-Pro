from pathlib import Path
from rich.panel import Panel
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
    ask,
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
        console.print("[bold yellow]No third-party apps found.[/bold yellow]")
        return None

    table = Table(title="Installed Third-Party Apps", show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold green", justify="right")
    table.add_column("Package Name", style="bold white")

    for i, pkg in enumerate(app_list, 1):
        table.add_row(str(i), pkg)

    console.print(table)
    selection = ask("[prompt]Enter Selection > [/prompt]")
    if not selection.isdigit():
        print_error("Expected an Integer Value\n[bold green] Going back to Main Menu[/bold green]")
        return None
    idx = int(selection)
    if idx < 1 or idx > len(app_list):
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return None
    return app_list[idx - 1]


def install_app(config: AppConfig) -> None:
    file_location = ask("[bold cyan]APK path on computer[/bold cyan] > ").strip()

    if not file_location:
        print_null_input()
        return

    file_location = file_location.rstrip().strip("'\"")
    apk_path = Path(file_location)

    if not apk_path.is_file():
        print_error("This file does not exist.")
        return

    if not confirm(
        f"Install [bold cyan]{apk_path.name}[/bold cyan] on the connected device? "
        "This may replace an existing installation."
    ):
        return

    with task_status(f"[info]Installing {apk_path.name}…[/info]"):
        result = adb(["install","-r", str(apk_path)])

    output = (result.stdout + result.stderr).strip()
    if "Success" in output:
        print_success(f"Installed: {apk_path.name}")
    else:
        print_error(f"Installation failed: {output}")


def uninstall_app(config: AppConfig) -> None:
    submenu_row("Select from app list", "Enter package name manually")
    mode = ask("[prompt]> [/prompt]")

    if mode == "1":
        package_name = _select_app_from_list()
        if not package_name:
            return
    elif mode == "2":
        package_name = ask(
            "[bold cyan]Package name[/bold cyan] [dim](e.g. com.spotify.music)[/dim]> "
        ).strip()
        if not package_name:
            print_null_input()
            return
    else:
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return

    if not confirm(
        f"Uninstall [bold yellow]{package_name}[/bold yellow] from the device? "
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
    mode = ask("[prompt]> [/prompt]")

    if mode == "1":
        package_name = _select_app_from_list()
        if not package_name:
            return
    elif mode == "2":
        package_name = ask(
            "[bold cyan]Package name[/bold cyan] [dim](e.g. com.spotify.music)[/dim]> "
        ).strip()
        if not package_name:
            print_null_input()
            return
    else:
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return

    with task_status(f"[info]Launching {package_name}…[/info]"):
        adb(["shell", "monkey", "-p", package_name, "1"])
    print_success(f"Launched: {package_name}")


def list_apps(config: AppConfig) -> None:
    submenu_row("Third-party packages only", "All packages")
    mode = ask("[prompt]> [/prompt]")

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
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return

    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold green", justify="right")
    table.add_column("Package Name", style="bold white")

    for i, pkg in enumerate(app_list, 1):
        table.add_row(str(i), pkg)

    console.print(table)


def extract_apk(config: AppConfig) -> None:
    submenu_row("Select from app list", "Enter package name manually")
    mode = ask("[prompt]> [/prompt]")

    if mode == "1":
        package_name = _select_app_from_list()
        if not package_name:
            return
    elif mode == "2":
        package_name = ask(
            "[bold cyan]Package name[/bold cyan] [dim](e.g. com.spotify.music)[/dim]> "
        ).strip()
        if not package_name:
            print_null_input()
            return
    else:
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return

    if not confirm(
        f"Extract APK for [bold yellow]{package_name}[/bold yellow] to your computer? "
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


def _list_all_apps() -> list[str]:
    raw = adb_output(["shell", "pm", "list", "packages"])
    return [line.replace("package:", "").strip() for line in raw.splitlines() if line.strip()]


def _select_app_from_packages(app_list: list[str], title: str) -> str | None:
    if not app_list:
        console.print("[bold yellow]No apps found.[/bold yellow]")
        return None
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold green", justify="right")
    table.add_column("Package Name", style="bold white")
    for i, pkg in enumerate(app_list, 1):
        table.add_row(str(i), pkg)
    console.print(table)
    selection = ask("[prompt]Enter Selection > [/prompt]")
    if not selection.isdigit():
        print_error("Expected an Integer Value")
        return None
    idx = int(selection)
    if idx < 1 or idx > len(app_list):
        print_error("Invalid selection")
        return None
    return app_list[idx - 1]


def prompt_package(*, include_system: bool = False) -> str | None:
    """Pick a package from third-party list, all packages, or manual entry."""
    if include_system:
        submenu_row("Third-party apps", "All packages", "Enter package name manually")
    else:
        submenu_row("Third-party apps", "Enter package name manually")
    mode = ask("[prompt]> [/prompt]").strip()
    if mode == "1":
        return _select_app_from_list()
    if mode == "2" and include_system:
        with task_status("[info]Fetching all packages…[/info]"):
            apps = _list_all_apps()
        return _select_app_from_packages(apps, "All Installed Packages")
    manual_mode = "3" if include_system else "2"
    if mode == manual_mode:
        pkg = ask("[bold cyan]Package name[/bold cyan]> ").strip()
        return pkg or None
    print_error("Invalid selection")
    return None


def _pm_report(r: object, verb_past: str) -> None:
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0 and not any(t in out.lower() for t in ("error", "exception", "failure")):
        print_success(out or f"Done ({verb_past}).")
    else:
        print_error(out or f"failed ({verb_past})")


def disable_app(config: AppConfig) -> None:
    pkg = prompt_package(include_system=True)
    if not pkg:
        return
    if not confirm(f"[bold yellow]Disable[/bold yellow] [cyan]{pkg}[/cyan]? (can be re-enabled later)"):
        return
    with task_status("[info]Disabling app…[/info]"):
        _pm_report(adb(["shell", "pm", "disable-user", "--user", "0", pkg]), "disabled")


def enable_app(config: AppConfig) -> None:
    pkg = prompt_package(include_system=True)
    if not pkg:
        return
    if not confirm(f"[bold green]Enable[/bold green] [cyan]{pkg}[/cyan]?"):
        return
    with task_status("[info]Enabling app…[/info]"):
        _pm_report(adb(["shell", "pm", "enable", pkg]), "enabled")


def suspend_app(config: AppConfig) -> None:
    pkg = prompt_package(include_system=True)
    if not pkg:
        return
    if not confirm(f"[bold yellow]Suspend[/bold yellow] [cyan]{pkg}[/cyan]?"):
        return
    with task_status("[info]Suspending app…[/info]"):
        _pm_report(adb(["shell", "pm", "suspend", "--user", "0", pkg]), "suspended")


def unsuspend_app(config: AppConfig) -> None:
    pkg = prompt_package(include_system=True)
    if not pkg:
        return
    if not confirm(f"[bold green]Unsuspend[/bold green] [cyan]{pkg}[/cyan]?"):
        return
    with task_status("[info]Unsuspending app…[/info]"):
        _pm_report(adb(["shell", "pm", "unsuspend", "--user", "0", pkg]), "unsuspended")


def battery_whitelist_show(config: AppConfig) -> None:
    with task_status("[info]Reading whitelist…[/info]"):
        whitelist = adb_output(["shell", "cmd", "deviceidle", "whitelist"])
    console.print(Panel(whitelist.strip() or "[dim]Empty[/dim]", title="[bold cyan]Whitelist[/bold cyan]", border_style="bold cyan"))


def battery_whitelist(config: AppConfig) -> None:
    pkg = prompt_package(include_system=True)
    if not pkg:
        return
    if not confirm(f"Whitelist [bold cyan]{pkg}[/bold cyan] (ignore battery optimizations)?"):
        return
    with task_status("[info]Whitelist…[/info]"):
        _pm_report(adb(["shell", "cmd", "deviceidle", "whitelist", f"+{pkg}"]), "whitelist")


def battery_unwhitelist(config: AppConfig) -> None:
    pkg = prompt_package(include_system=True)
    if not pkg:
        return
    if not confirm(f"Un-whitelist [bold cyan]{pkg}[/bold cyan] (ignore battery optimizations)?"):
        return
    with task_status("[info]Un-whitelist…[/info]"):
        _pm_report(adb(["shell", "cmd", "deviceidle", "whitelist", f"-{pkg}"]), "un-whitelist")


def show_home_app(config: AppConfig) -> None:
    with task_status("[info]Reading current home app…[/info]"):
        current = adb_output(
            [
                "shell",
                "cmd",
                "package",
                "resolve-activity",
                "--brief",
                "-a",
                "android.intent.action.MAIN",
                "-c",
                "android.intent.category.HOME",
            ]
        )
    home = current.strip().splitlines()[-1] if current.strip() else "[dim]Unknown[/dim]"
    console.print(Panel(home, title="[bold cyan]Current Home App[/bold cyan]", border_style="bold cyan"))


def set_home_app(config: AppConfig) -> None:
    show_home_app(config)
    pkg = ask("[bold cyan]Launcher package name[/bold cyan] [dim](e.g. com.android.launcher3)[/dim]> ").strip()
    if not pkg:
        print_error("Null input")
        return
    with task_status("[info]Resolving launcher activity…[/info]"):
        resolved = adb_output(
            [
                "shell",
                "cmd",
                "package",
                "query-activities",
                "--brief",
                "-a",
                "android.intent.action.MAIN",
                "-c",
                "android.intent.category.LAUNCHER",
                pkg,
            ]
        ).strip()
    component = None
    for line in resolved.splitlines():
        line = line.strip()
        if not line or line.startswith("Warning") or "query intent" in line.lower():
            continue
        component = line
        break
    if not component or "/" not in component:
        print_error("Could not auto-resolve the launcher activity for that package.")
        component = ask("[bold cyan]Enter component manually[/bold cyan] [dim](pkg/.Activity)[/dim]> ").strip()
        if not component:
            return
    if not confirm(f"Set default home app to [bold cyan]{component}[/bold cyan]?"):
        return
    with task_status("[info]Setting home app…[/info]"):
        _pm_report(
            adb(["shell", "cmd", "package", "set-home-activity", "--user", "0", component]),
            "home set",
        )
