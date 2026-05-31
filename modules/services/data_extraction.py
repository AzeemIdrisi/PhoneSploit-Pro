"""Data extraction services."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from modules.services.adb import OperationResult
from modules.services.context import ServiceContext


def _timestamp() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}"


def _write_dump(dest: Path, result) -> OperationResult:
    if result.returncode != 0:
        err_msg = result.stderr.strip() or "(no stderr from adb)"
        err_dest = dest.with_suffix(".error.txt")
        detail = result.stderr.strip() or f"adb exited with code {result.returncode}"
        try:
            err_dest.write_text(detail, encoding="utf-8")
        except OSError as e:
            return OperationResult(False, f"Could not save error: {e}")
        return OperationResult(False, f"Dump failed: {err_msg}", error=err_msg)

    try:
        dest.write_text(result.stdout, encoding="utf-8")
    except OSError as e:
        return OperationResult(False, f"Could not write dump: {e}")

    lines = [l for l in result.stdout.splitlines() if l.strip()]
    return OperationResult(
        True,
        f"Saved {len(lines)} records to: {dest}",
        data=str(dest),
    )


def dump_sms(ctx: ServiceContext) -> OperationResult:
    out_dir = ctx.ensure_output_dir()
    dest = out_dir / f"sms_dump-{_timestamp()}.txt"
    result = ctx.adb.run(
        [
            "shell",
            "content",
            "query",
            "--uri",
            "content://sms/",
            "--projection",
            "address:date:body",
        ]
    )
    return _write_dump(dest, result)


def dump_contacts(ctx: ServiceContext) -> OperationResult:
    out_dir = ctx.ensure_output_dir()
    dest = out_dir / f"contacts_dump-{_timestamp()}.txt"
    result = ctx.adb.run(
        [
            "shell",
            "content",
            "query",
            "--uri",
            "content://contacts/phones/",
            "--projection",
            "display_name:number",
        ]
    )
    return _write_dump(dest, result)


def dump_call_logs(ctx: ServiceContext) -> OperationResult:
    out_dir = ctx.ensure_output_dir()
    dest = out_dir / f"call_logs_dump-{_timestamp()}.txt"
    result = ctx.adb.run(
        [
            "shell",
            "content",
            "query",
            "--uri",
            "content://call_log/calls",
            "--projection",
            "name:number:duration:date",
        ]
    )
    return _write_dump(dest, result)
