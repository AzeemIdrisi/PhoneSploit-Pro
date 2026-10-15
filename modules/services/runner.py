"""Serial-aware ADB runner.

The CLI targets one device via the process-global ANDROID_SERIAL variable.
The web console can talk to several devices at once, so every call passes
``-s <serial>`` and never mutates that environment variable.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from modules.console import get_adb_executable

_SERIAL_RE = re.compile(r"^[A-Za-z0-9._:\-]{1,128}$")
_PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")


class AdbError(RuntimeError):
    pass


@dataclass
class CmdResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""

    @property
    def text(self) -> str:
        return (self.stdout + self.stderr).strip()

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def validate_serial(serial: str) -> str:
    serial = (serial or "").strip()
    if not _SERIAL_RE.match(serial):
        raise AdbError("Invalid device serial.")
    return serial


def validate_package(package: str) -> str:
    package = (package or "").strip()
    if not _PACKAGE_RE.match(package):
        raise AdbError("Invalid package name.")
    return package


def validate_remote_path(path: str) -> str:
    path = (path or "").strip()
    if not path.startswith("/") or ".." in path.split("/"):
        raise AdbError("Remote path must be absolute and must not contain '..'.")
    return path


def adb_executable() -> str:
    exe = get_adb_executable()
    if not exe:
        raise AdbError("ADB executable not available. Install platform-tools and restart.")
    return exe


def run(
    args: list[str],
    *,
    serial: str | None = None,
    timeout: float | None = 60,
) -> CmdResult:
    """Run adb. ``serial`` inserts ``-s`` and is required for device commands."""
    cmd = [adb_executable()]
    if serial:
        cmd += ["-s", validate_serial(serial)]
    cmd += args
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise AdbError(f"adb timed out: {' '.join(args[:4])}") from exc
    except OSError as exc:
        raise AdbError(str(exc)) from exc
    return CmdResult(completed.returncode, completed.stdout or "", completed.stderr or "")


def run_bytes(
    args: list[str],
    *,
    serial: str | None = None,
    timeout: float | None = 20,
) -> tuple[int, bytes, bytes]:
    cmd = [adb_executable()]
    if serial:
        cmd += ["-s", validate_serial(serial)]
    cmd += args
    try:
        completed = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise AdbError("adb timed out") from exc
    except OSError as exc:
        raise AdbError(str(exc)) from exc
    return completed.returncode, completed.stdout or b"", completed.stderr or b""


def shell(serial: str, *args: str, timeout: float | None = 60) -> CmdResult:
    return run(["shell", *args], serial=serial, timeout=timeout)


def shell_text(serial: str, *args: str, timeout: float | None = 60) -> str:
    return shell(serial, *args, timeout=timeout).stdout.strip()


def command_failed(result: CmdResult) -> bool:
    lowered = result.text.lower()
    if result.returncode != 0:
        return True
    return any(
        token in lowered
        for token in (
            "unknown command",
            "securityexception",
            "permission denial",
            "not found",
            "inaccessible or not found",
            "not allowed",
            "exception:",
            "usage: cmd",
        )
    )
