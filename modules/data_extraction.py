import subprocess
from pathlib import Path
from datetime import datetime

from modules.config import AppConfig
from modules.console import print_success, print_error, confirm, task_status, ensure_config_dir, adb


def _timestamp() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}"


def _write_dump(dest: Path, result: subprocess.CompletedProcess[str]) -> None:
    """Persist adb output: stdout only on success; on failure, record stderr in a sibling file."""
    if result.returncode != 0:
        err_msg = result.stderr.strip() or "(no stderr from adb)"
        print_error(f"Dump failed: {err_msg}")
        err_dest = dest.with_suffix(".error.txt")
        detail = result.stderr.strip() or f"adb exited with code {result.returncode} (no stderr output)."
        try:
            err_dest.write_text(detail, encoding="utf-8")
        except OSError as e:
            print_error(f"Could not save error details to {err_dest}: {e}")
        return
    try:
        dest.write_text(result.stdout, encoding="utf-8")
    except OSError as e:
        print_error(f"Could not write dump file {dest}: {e}")
        return
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    print_success(f"Saved {len(lines)} records to: {dest}")


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

    _write_dump(dest, result)


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

    _write_dump(dest, result)


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

    _write_dump(dest, result)
