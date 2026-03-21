from pathlib import Path
from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_null_input,
    open_file_prompt,
    confirm,
    task_status,
    ensure_config_dir,
    adb,
    adb_output,
)


def list_files(config: AppConfig) -> None:
    with task_status("[info]Listing /sdcard/…[/info]"):
        raw = adb_output(["shell", "ls", "-a", "/sdcard/"])

    entries = [e.strip() for e in raw.splitlines() if e.strip()]
    if not entries:
        console.print("[yellow]No files found.[/yellow]")
        return

    table = Table(title="/sdcard/ Contents", show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold green", justify="right")
    table.add_column("Name", style="white")

    for i, entry in enumerate(entries, 1):
        table.add_row(str(i), entry)

    console.print(table)


def pull_file(config: AppConfig) -> None:
    console.print(
        "[cyan]Path under /sdcard/[/cyan] [dim](e.g. Download/sample.jpg)[/dim]"
    )
    location = console.input("[prompt]> /sdcard/[/prompt]").strip()

    full_path = f"/sdcard/{location}"

    with task_status(f"[info]Checking {full_path}…[/info]"):
        check = adb(["shell", "test", "-e", full_path])

    if check.returncode != 0:
        print_error(f"Specified path does not exist: {full_path}")
        return

    if not confirm(
        f"Download [cyan]{full_path}[/cyan] from the device? "
        "A local file with the same name may be overwritten."
    ):
        return

    out_dir = ensure_config_dir(config, "pull_location")

    with task_status(f"[info]Pulling {full_path}…[/info]"):
        result = adb(["pull", full_path, str(out_dir)])

    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        print_success(f"Saved under: {out_dir}")
    else:
        print_error(f"Pull failed: {output}")
        return

    file_name = Path(location).name
    local_path = str(out_dir / file_name)
    open_file_prompt(config.opener, local_path)


def push_file(config: AppConfig) -> None:
    location = console.input("[cyan]File path on computer[/cyan] > ").strip()

    if not location:
        print_null_input()
        return

    location = location.rstrip().strip("'\"")
    file_path = Path(location)

    if not file_path.exists():
        print_error("Specified path does not exist.")
        return

    if not confirm(
        f"Upload [cyan]{file_path.name}[/cyan] to the device? "
        "An existing file at the destination path may be overwritten."
    ):
        return

    destination = console.input(
        "[cyan]Destination under /sdcard/[/cyan] [dim](e.g. Documents)[/dim]> "
    ).strip()

    with task_status(f"[info]Pushing {file_path.name}…[/info]"):
        result = adb(["push", str(file_path), f"/sdcard/{destination}"])

    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        print_success(f"Pushed to /sdcard/{destination}")
    else:
        print_error(f"Push failed: {output}")


def _pull_directory(config: AppConfig, remote_path: str, label: str) -> None:
    """Generic helper to pull a directory from the device."""
    out_dir = ensure_config_dir(config, "pull_location")

    with task_status(f"[info]Pulling {label}…[/info]"):
        result = adb(["pull", remote_path, str(out_dir)])

    if result.returncode == 0:
        print_success(f"{label} saved to: {out_dir}")
    else:
        print_error((result.stdout + result.stderr).strip())


def copy_whatsapp(config: AppConfig) -> None:
    with task_status("[info]Locating WhatsApp folder…[/info]"):
        new_path_check = adb(["shell", "test", "-d", "/sdcard/Android/media/com.whatsapp/WhatsApp"])
        old_path_check = adb(["shell", "test", "-d", "/sdcard/WhatsApp"])

    if new_path_check.returncode == 0:
        location = "/sdcard/Android/media/com.whatsapp/WhatsApp"
    elif old_path_check.returncode == 0:
        location = "/sdcard/WhatsApp"
    else:
        print_error("WhatsApp folder does not exist.")
        return

    if not confirm(
        "Copy WhatsApp data from the device? This may transfer a large amount of sensitive data."
    ):
        return

    _pull_directory(config, location, "WhatsApp Data")


def copy_screenshots(config: AppConfig) -> None:
    paths = [
        "/sdcard/Pictures/Screenshots",
        "/sdcard/DCIM/Screenshots",
        "/sdcard/Screenshots",
    ]
    location = None
    with task_status("[info]Locating Screenshots folder…[/info]"):
        for p in paths:
            if adb(["shell", "test", "-d", p]).returncode == 0:
                location = p
                break

    if not location:
        print_error("Screenshots folder does not exist.")
        return

    if not confirm(
        "Copy all screenshots from the device? This may transfer many personal images."
    ):
        return

    _pull_directory(config, location, "Screenshots")


def copy_camera(config: AppConfig) -> None:
    with task_status("[info]Locating Camera folder…[/info]"):
        check = adb(["shell", "test", "-d", "/sdcard/DCIM/Camera"])

    if check.returncode != 0:
        print_error("Camera folder does not exist.")
        return

    if not confirm(
        "Copy all camera photos from the device? This may transfer a large amount of personal media."
    ):
        return

    _pull_directory(config, "/sdcard/DCIM/Camera", "Camera Photos")
