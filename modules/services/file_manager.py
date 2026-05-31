"""File management services."""

from __future__ import annotations

from pathlib import Path

from modules.services.adb import ADBService, OperationResult
from modules.services.context import ServiceContext


def list_sdcard(adb: ADBService, path: str = "/sdcard/") -> OperationResult:
    raw = adb.output(["shell", "ls", "-a", path])
    entries = [e.strip() for e in raw.splitlines() if e.strip()]
    return OperationResult(True, f"{len(entries)} entries", data=entries)


def pull_file(ctx: ServiceContext, remote_path: str) -> OperationResult:
    adb = ctx.adb
    if not remote_path.startswith("/"):
        remote_path = f"/sdcard/{remote_path.lstrip('/')}"

    check = adb.run(["shell", "test", "-e", remote_path])
    if check.returncode != 0:
        return OperationResult(False, f"Path does not exist: {remote_path}")

    out_dir = ctx.ensure_output_dir()
    result = adb.run(["pull", remote_path, str(out_dir)])
    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        local = out_dir / Path(remote_path).name
        return OperationResult(True, f"Saved under: {out_dir}", data=str(local))
    return OperationResult(False, f"Pull failed: {output}", error=output)


def push_file(
    adb: ADBService,
    local_path: Path,
    destination: str = "",
) -> OperationResult:
    if not local_path.exists():
        return OperationResult(False, "Local path does not exist")
    dest = f"/sdcard/{destination.lstrip('/')}" if destination else "/sdcard/"
    result = adb.run(["push", str(local_path), dest])
    output = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        return OperationResult(True, f"Pushed to {dest}")
    return OperationResult(False, f"Push failed: {output}", error=output)


def _pull_directory(ctx: ServiceContext, remote_path: str, label: str) -> OperationResult:
    out_dir = ctx.ensure_output_dir()
    result = ctx.adb.run(["pull", remote_path, str(out_dir)])
    if result.returncode == 0:
        return OperationResult(True, f"{label} saved to: {out_dir}")
    return OperationResult(False, (result.stdout + result.stderr).strip())


def copy_whatsapp(ctx: ServiceContext) -> OperationResult:
    adb = ctx.adb
    new_check = adb.run(["shell", "test", "-d", "/sdcard/Android/media/com.whatsapp/WhatsApp"])
    old_check = adb.run(["shell", "test", "-d", "/sdcard/WhatsApp"])
    if new_check.returncode == 0:
        location = "/sdcard/Android/media/com.whatsapp/WhatsApp"
    elif old_check.returncode == 0:
        location = "/sdcard/WhatsApp"
    else:
        return OperationResult(False, "WhatsApp folder does not exist")
    return _pull_directory(ctx, location, "WhatsApp Data")


def copy_screenshots(ctx: ServiceContext) -> OperationResult:
    paths = [
        "/sdcard/Pictures/Screenshots",
        "/sdcard/DCIM/Screenshots",
        "/sdcard/Screenshots",
    ]
    for p in paths:
        if ctx.adb.run(["shell", "test", "-d", p]).returncode == 0:
            return _pull_directory(ctx, p, "Screenshots")
    return OperationResult(False, "Screenshots folder does not exist")


def copy_camera(ctx: ServiceContext) -> OperationResult:
    if ctx.adb.run(["shell", "test", "-d", "/sdcard/DCIM/Camera"]).returncode != 0:
        return OperationResult(False, "Camera folder does not exist")
    return _pull_directory(ctx, "/sdcard/DCIM/Camera", "Camera Photos")
