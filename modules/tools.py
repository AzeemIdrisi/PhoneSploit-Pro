"""
Resolve external binaries (ADB, Metasploit, scrcpy, nmap, HARDAX) the same way as startup:
PATH via shutil.which, plus Windows local copies next to the project (README).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from modules.config import AppConfig

HARDAX_MIN_VERSION = (6, 2, 0)


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


def _project_venv_hardax() -> str | None:
    root = Path(__file__).resolve().parent.parent
    for rel in (".venv/bin/hardax", ".venv/Scripts/hardax.exe"):
        candidate = root / rel
        if candidate.is_file():
            return str(candidate.resolve())
    return None


def find_hardax_argv0() -> list[str] | None:
    """Launch vector for HARDAX: project venv, PATH binary, or ``python -m hardax``."""
    venv_bin = _project_venv_hardax()
    if venv_bin:
        return [venv_bin]
    w = _which("hardax")
    if w:
        return [w]
    try:
        probe = subprocess.run(
            [sys.executable, "-m", "hardax", "--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if probe.returncode == 0:
            return [sys.executable, "-m", "hardax"]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _parse_hardax_version(text: str) -> tuple[int, int, int] | None:
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def hardax_version(argv0: list[str]) -> tuple[int, int, int] | None:
    try:
        result = subprocess.run(
            argv0 + ["--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    combined = (result.stdout or "") + (result.stderr or "")
    return _parse_hardax_version(combined)


def resolve_external_tools(config: AppConfig) -> None:
    config.adb_path = find_adb_exe(config.operating_system)
    config.msfvenom_path = find_msfvenom()
    config.msfconsole_path = find_msfconsole()
    config.scrcpy_path = find_scrcpy(config.operating_system)
    config.nmap_path = find_nmap()
    config.hardax_argv0 = find_hardax_argv0()


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


def require_hardax(config: AppConfig) -> bool:
    from modules.console import print_error

    if not config.hardax_argv0:
        resolve_external_tools(config)
    argv0 = config.hardax_argv0
    if not argv0:
        print_error(
            "HARDAX is not installed. Run: pip install -r requirements.txt "
            "(or pip install \"hardax>=6.2.0\" / ./install.sh --components hardax,pip). See README."
        )
        return False
    version = hardax_version(argv0)
    if version is None:
        print_error("Could not determine HARDAX version. Reinstall hardax and try again.")
        return False
    if version < HARDAX_MIN_VERSION:
        min_s = ".".join(str(x) for x in HARDAX_MIN_VERSION)
        got_s = ".".join(str(x) for x in version)
        print_error(
            f"HARDAX {got_s} is too old (need {min_s}+). Upgrade: pip install -U \"hardax>=6.2.0\""
        )
        return False
    return True


def hardax_argv(config: AppConfig, extra: list[str]) -> list[str]:
    """Build argv for subprocess; caller must ensure require_hardax(config) first."""
    base = config.hardax_argv0 or find_hardax_argv0() or ["hardax"]
    return base + extra


def scrcpy_argv(config: AppConfig, args: list[str]) -> list[str]:
    """Build argv for subprocess; caller must ensure require_scrcpy(config) first."""
    return [config.scrcpy_path or "scrcpy"] + args
