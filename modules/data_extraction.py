from pathlib import Path
from datetime import datetime

from modules.config import AppConfig
from modules.console import print_success, print_error, confirm, task_status, ensure_config_dir, adb


def _timestamp() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}"


def dump_sms(config: AppConfig) -> None:
    if not confirm(
        "Export all SMS messages from the device to a file on this computer? "
        "This accesses private communications."
    ):
        return
    save_dir = ensure_config_dir(config, "pull_location")
    file_name = f"sms_dump-{_timestamp()}.txt"
    dest = Path(save_dir) / file_name

    with task_status("[info]Dumping SMS…[/info]"):
        result = adb(
            [
                "shell", "content", "query",
                "--uri", "content://sms/",
                "--projection", "address:date:body",
            ]
        )

    dest.write_text(result.stdout, encoding="utf-8")
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    if result.returncode == 0:
        print_success(f"Saved {len(lines)} records to: {dest}")
    else:
        print_error(f"Dump failed: {result.stderr.strip()}")


def dump_contacts(config: AppConfig) -> None:
    if not confirm(
        "Export all contacts from the device to a file on this computer? "
        "This accesses private contact data."
    ):
        return
    save_dir = ensure_config_dir(config, "pull_location")
    file_name = f"contacts_dump-{_timestamp()}.txt"
    dest = Path(save_dir) / file_name

    with task_status("[info]Dumping contacts…[/info]"):
        result = adb(
            [
                "shell", "content", "query",
                "--uri", "content://contacts/phones/",
                "--projection", "display_name:number",
            ]
        )

    dest.write_text(result.stdout, encoding="utf-8")
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    if result.returncode == 0:
        print_success(f"Saved {len(lines)} records to: {dest}")
    else:
        print_error(f"Dump failed: {result.stderr.strip()}")


def dump_call_logs(config: AppConfig) -> None:
    if not confirm(
        "Export all call logs from the device to a file on this computer? "
        "This accesses private call history."
    ):
        return
    save_dir = ensure_config_dir(config, "pull_location")
    file_name = f"call_logs_dump-{_timestamp()}.txt"
    dest = Path(save_dir) / file_name

    with task_status("[info]Dumping call logs…[/info]"):
        result = adb(
            [
                "shell", "content", "query",
                "--uri", "content://call_log/calls",
                "--projection", "name:number:duration:date",
            ]
        )

    dest.write_text(result.stdout, encoding="utf-8")
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    if result.returncode == 0:
        print_success(f"Saved {len(lines)} records to: {dest}")
    else:
        print_error(f"Dump failed: {result.stderr.strip()}")
