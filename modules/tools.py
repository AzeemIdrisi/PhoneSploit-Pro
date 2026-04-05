"""
Resolve external binaries (ADB, Metasploit, scrcpy, nmap) the same way as startup:
PATH via shutil.which, plus Windows local copies next to the project (README).
"""

from __future__ import annotations

import shutil
from pathlib import Path

from modules.config import AppConfig


def _which(name: str) -> str | None:
    return shutil.which(name)


def find_adb_exe(operating_system: str) -> str | None:
    w = _which("adb")
    if w:
        return w
    if operating_system == "Windows":
        cwd = Path.cwd()
        for candidate in (cwd / "adb.exe", cwd / "adb"):
            if candidate.is_file():
                return str(candidate.resolve())
    return None


def find_msfvenom() -> str | None:
    return _which("msfvenom")


def find_msfconsole() -> str | None:
    return _which("msfconsole")


def find_scrcpy(operating_system: str) -> str | None:
    w = _which("scrcpy") or (_which("scrcpy.exe") if operating_system == "Windows" else None)
    if w:
        return w
    if operating_system == "Windows":
        cwd = Path.cwd()
        for candidate in (cwd / "scrcpy.exe", cwd / "scrcpy"):
            if candidate.is_file():
                return str(candidate.resolve())
    return None


def find_nmap() -> str | None:
    return _which("nmap")


def resolve_external_tools(config: AppConfig) -> None:
    config.adb_path = find_adb_exe(config.operating_system)
    config.msfvenom_path = find_msfvenom()
    config.msfconsole_path = find_msfconsole()
    config.scrcpy_path = find_scrcpy(config.operating_system)
    config.nmap_path = find_nmap()


def require_adb(config: AppConfig) -> bool:
    if config.adb_path:
        return True
    from modules.console import print_error

    print_error(
        "ADB is not installed or not on PATH. "
        "Install Android SDK Platform Tools (or place adb next to this program on Windows)."
    )
    return False


def require_scrcpy(config: AppConfig) -> bool:
    if config.scrcpy_path:
        return True
    from modules.console import print_error

    print_error("Scrcpy is not installed or not on PATH. Install scrcpy and try again.")
    return False


def require_nmap(config: AppConfig) -> bool:
    if config.nmap_path:
        return True
    from modules.console import print_error

    print_error("Nmap is not installed or not on PATH. Install nmap and try again.")
    return False


def require_metasploit(config: AppConfig) -> bool:
    if config.msfvenom_path and config.msfconsole_path:
        return True
    from modules.console import print_error

    print_error(
        "Metasploit-Framework (msfvenom and msfconsole) not found on PATH. "
        "Install Metasploit and try again."
    )
    return False


def scrcpy_argv(config: AppConfig, args: list[str]) -> list[str]:
    """Build argv for subprocess; caller must ensure require_scrcpy(config) first."""
    return [config.scrcpy_path or "scrcpy"] + args
