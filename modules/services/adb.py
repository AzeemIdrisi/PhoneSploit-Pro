"""Device-scoped ADB wrapper."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DeviceSession:
    serial: str | None = None
    output_dir: Path = field(default_factory=lambda: Path("Downloaded-Files"))


@dataclass
class OperationResult:
    success: bool
    message: str
    data: Any = None
    error: str | None = None


class ADBService:
    """Run adb commands with optional device serial targeting."""

    def __init__(self, executable: str | None, serial: str | None = None) -> None:
        self.executable = executable
        self.serial = serial if serial is not None else os.environ.get("ANDROID_SERIAL")

    def with_serial(self, serial: str | None) -> ADBService:
        return ADBService(self.executable, serial)

    def _build_cmd(self, args: list[str], *, host_level: bool = False) -> list[str]:
        if not self.executable:
            return []
        cmd = [self.executable]
        if not host_level and self.serial:
            cmd.extend(["-s", self.serial])
        cmd.extend(args)
        return cmd

    def run(
        self,
        args: list[str],
        *,
        capture: bool = True,
        host_level: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        if self.executable is None:
            return subprocess.CompletedProcess(
                args=[],
                returncode=127,
                stdout="",
                stderr="adb not available",
            )
        cmd = self._build_cmd(args, host_level=host_level)
        if capture:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        return subprocess.run(cmd)

    def output(self, args: list[str], *, host_level: bool = False) -> str:
        return self.run(args, host_level=host_level).stdout.strip()

    def available(self) -> bool:
        return self.executable is not None


# Module-level instance used by CLI via console.py
_global_adb: ADBService | None = None


def set_global_adb(executable: str | None) -> None:
    global _global_adb
    _global_adb = ADBService(executable)


def get_global_adb() -> ADBService:
    if _global_adb is None:
        return ADBService(None)
    return _global_adb


def adb(args: list[str], capture: bool = True) -> subprocess.CompletedProcess[str]:
    """Backward-compatible adb() for CLI modules."""
    return get_global_adb().run(args, capture=capture)


def adb_output(args: list[str]) -> str:
    return get_global_adb().output(args)
