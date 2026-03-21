import subprocess
from pathlib import Path
from datetime import datetime

from modules.config import AppConfig
from modules.console import console, print_success, print_error, confirm


def _timestamp() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}"


def _ensure_pull_location(config: AppConfig, label: str) -> str:
    if not config.pull_location:
        console.print(f"\n[yellow]Enter location to save {label}, Press 'Enter' for default[/yellow]")
        config.pull_location = console.input("[prompt]> [/prompt]")
    if not config.pull_location:
        config.pull_location = "Downloaded-Files"
        console.print(f"\n[purple]Saving {label} to PhoneSploit-Pro/{config.pull_location}[/purple]\n")
    else:
        console.print(f"\n[purple]Saving {label} to {config.pull_location}[/purple]\n")
    Path(config.pull_location).mkdir(parents=True, exist_ok=True)
    return config.pull_location


def dump_sms(config: AppConfig) -> None:
    if not confirm(
        "Export all SMS messages from the device to a file on this computer? "
        "This accesses private communications."
    ):
        return
    save_dir = _ensure_pull_location(config, "SMS file")
    file_name = f"sms_dump-{_timestamp()}.txt"
    dest = Path(save_dir) / file_name

    console.print("[green]Extracting all SMS...[/green]")
    with console.status("[info]Dumping SMS messages...[/info]"):
        result = subprocess.run(
            [
                "adb", "shell", "content", "query",
                "--uri", "content://sms/",
                "--projection", "address:date:body",
            ],
            capture_output=True,
            text=True,
        )

    dest.write_text(result.stdout, encoding="utf-8")
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    if result.returncode == 0:
        print_success(f"Saved {len(lines)} records to: {dest}")
    else:
        print_error(f"Dump failed:\n{result.stderr.strip()}")
    console.print()


def dump_contacts(config: AppConfig) -> None:
    if not confirm(
        "Export all contacts from the device to a file on this computer? "
        "This accesses private contact data."
    ):
        return
    save_dir = _ensure_pull_location(config, "Contacts file")
    file_name = f"contacts_dump-{_timestamp()}.txt"
    dest = Path(save_dir) / file_name

    console.print("[green]Extracting all Contacts...[/green]")
    with console.status("[info]Dumping contacts...[/info]"):
        result = subprocess.run(
            [
                "adb", "shell", "content", "query",
                "--uri", "content://contacts/phones/",
                "--projection", "display_name:number",
            ],
            capture_output=True,
            text=True,
        )

    dest.write_text(result.stdout, encoding="utf-8")
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    if result.returncode == 0:
        print_success(f"Saved {len(lines)} records to: {dest}")
    else:
        print_error(f"Dump failed:\n{result.stderr.strip()}")
    console.print()


def dump_call_logs(config: AppConfig) -> None:
    if not confirm(
        "Export all call logs from the device to a file on this computer? "
        "This accesses private call history."
    ):
        return
    save_dir = _ensure_pull_location(config, "Call Logs file")
    file_name = f"call_logs_dump-{_timestamp()}.txt"
    dest = Path(save_dir) / file_name

    console.print("[green]Extracting all Call Logs...[/green]")
    with console.status("[info]Dumping call logs...[/info]"):
        result = subprocess.run(
            [
                "adb", "shell", "content", "query",
                "--uri", "content://call_log/calls",
                "--projection", "name:number:duration:date",
            ],
            capture_output=True,
            text=True,
        )

    dest.write_text(result.stdout, encoding="utf-8")
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    if result.returncode == 0:
        print_success(f"Saved {len(lines)} records to: {dest}")
    else:
        print_error(f"Dump failed:\n{result.stderr.strip()}")
    console.print()
