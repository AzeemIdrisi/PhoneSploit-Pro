import subprocess
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
    adb,
    adb_output,
)


def list_files(config: AppConfig) -> None:
    with console.status("[info]Listing /sdcard/ contents...[/info]"):
        raw = adb_output(["shell", "ls", "-a", "/sdcard/"])

    entries = [e.strip() for e in raw.splitlines() if e.strip()]
    if not entries:
        console.print("\n[yellow]No files found.[/yellow]\n")
        return

    table = Table(title="/sdcard/ Contents", show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold green", justify="right")
    table.add_column("Name", style="white")

    for i, entry in enumerate(entries, 1):
        table.add_row(str(i), entry)

    console.print()
    console.print(table)
    console.print()


def pull_file(config: AppConfig) -> None:
    console.print(
        f"\n[cyan]Enter file path           [yellow]Example : Download/sample.jpg[/yellow][/cyan]"
    )
    location = console.input("\n[prompt]> /sdcard/[/prompt]")

    full_path = f"/sdcard/{location}"

    with console.status(f"[info]Checking if {full_path} exists...[/info]"):
        check = adb(["shell", "test", "-e", full_path])

    if check.returncode != 0:
        print_error(f"Specified path does not exist: {full_path}")
        return

    if not confirm(
        f"Download [cyan]{full_path}[/cyan] from the device to your computer? "
        "A local file with the same name may be overwritten."
    ):
        return

    if not config.pull_location:
        console.print("\n[yellow]Enter location to save all files, Press 'Enter' for default[/yellow]")
        config.pull_location = console.input("[prompt]> [/prompt]")
    if not config.pull_location:
        config.pull_location = "Downloaded-Files"
        console.print(f"\n[purple]Saving file to PhoneSploit-Pro/{config.pull_location}[/purple]\n")
    else:
        console.print(f"\n[purple]Saving file to {config.pull_location}[/purple]\n")

    Path(config.pull_location).mkdir(parents=True, exist_ok=True)

    with console.status(f"[info]Pulling {full_path}...[/info]"):
        result = adb(["pull", full_path, config.pull_location])

    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        print_success(f"Saved to: {config.pull_location}")
    else:
        print_error(f"Pull failed:\n{output}")
        return

    file_name = Path(location).name
    local_path = str(Path(config.pull_location) / file_name)
    open_file_prompt(config.opener, local_path)


def push_file(config: AppConfig) -> None:
    location = console.input(f"\n[cyan]Enter file path in computer[/cyan] > ").strip()

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
        f"\n[cyan]Enter destination path              [yellow]Example : Documents[/yellow][/cyan]\n[prompt]> /sdcard/[/prompt]"
    )

    with console.status(f"[info]Pushing {file_path.name}...[/info]"):
        result = adb(["push", str(file_path), f"/sdcard/{destination}"])

    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        print_success(f"Pushed to /sdcard/{destination}")
    else:
        print_error(f"Push failed:\n{output}")
    console.print()


def _pull_directory(config: AppConfig, remote_path: str, label: str) -> None:
    """Generic helper to pull a directory from the device."""
    if not config.pull_location:
        console.print(f"\n[yellow]Enter location to save {label}, Press 'Enter' for default[/yellow]")
        config.pull_location = console.input("[prompt]> [/prompt]")
    if not config.pull_location:
        config.pull_location = "Downloaded-Files"
        console.print(f"\n[purple]Saving {label} to PhoneSploit-Pro/{config.pull_location}[/purple]\n")
    else:
        console.print(f"\n[purple]Saving {label} to {config.pull_location}[/purple]\n")

    Path(config.pull_location).mkdir(parents=True, exist_ok=True)

    with console.status(f"[info]Pulling {label}...[/info]"):
        result = adb(["pull", remote_path, config.pull_location])

    if result.returncode == 0:
        print_success(f"{label} saved to: {config.pull_location}")
    else:
        print_error((result.stdout + result.stderr).strip())
    console.print()


def copy_whatsapp(config: AppConfig) -> None:
    with console.status("[info]Locating WhatsApp folder...[/info]"):
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
    with console.status("[info]Locating Screenshots folder...[/info]"):
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
    with console.status("[info]Locating Camera folder...[/info]"):
        check = adb(["shell", "test", "-d", "/sdcard/DCIM/Camera"])

    if check.returncode != 0:
        print_error("Camera folder does not exist.")
        return

    if not confirm(
        "Copy all camera photos from the device? This may transfer a large amount of personal media."
    ):
        return

    _pull_directory(config, "/sdcard/DCIM/Camera", "Camera Photos")
