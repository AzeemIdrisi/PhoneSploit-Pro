"""
Resolve external binaries (ADB, Metasploit, scrcpy, nmap, HARDAX) the same way as startup:
PATH via shutil.which, plus Windows local copies next to the project (README).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
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


def find_lockknife() -> str | None:
    return _which("lockknife")


def find_drozer() -> str | None:
    w = _which("drozer")
    if w:
        return w
    for candidate in (
        Path(__file__).resolve().parent.parent / ".venv/bin/drozer",
        Path(__file__).resolve().parent.parent / ".venv/Scripts/drozer.exe",
    ):
        if candidate.is_file():
            return str(candidate.resolve())
    return None


def find_frida() -> str | None:
    w = _which("frida")
    if w:
        return w
    root = Path(__file__).resolve().parent.parent
    for candidate in (root / ".venv/bin/frida", root / ".venv/Scripts/frida.exe"):
        if candidate.is_file():
            return str(candidate.resolve())
    return None


def frida_ps_argv(config: AppConfig) -> list[str]:
    """Resolve frida-ps next to the same frida binary used for version checks."""
    frida_bin = config.frida_path or find_frida()
    if frida_bin:
        sibling = Path(frida_bin).with_name("frida-ps")
        if sibling.is_file():
            return [str(sibling.resolve()), "-Uai"]
        sibling_exe = Path(frida_bin).with_name("frida-ps.exe")
        if sibling_exe.is_file():
            return [str(sibling_exe.resolve()), "-Uai"]
    w = _which("frida-ps")
    if w:
        return [w, "-Uai"]
    return ["frida-ps", "-Uai"]


def find_objection() -> str | None:
    w = _which("objection")
    if w:
        return w
    for candidate in (
        Path(__file__).resolve().parent.parent / ".venv/bin/objection",
        Path(__file__).resolve().parent.parent / ".venv/Scripts/objection.exe",
    ):
        if candidate.is_file():
            return str(candidate.resolve())
    return None


ALEAPP_CLONE_ROOT = Path.home() / ".phonesploit-pro" / "tools" / "ALEAPP"

_LOCKKNIFE_USE_CLI: bool | None = None


def find_aleapp_argv0() -> list[str] | None:
    w = _which("aleapp")
    if w:
        return [w]
    cloned = ALEAPP_CLONE_ROOT / "aleapp.py"
    if cloned.is_file():
        venv_py = ALEAPP_CLONE_ROOT / ".venv" / "bin" / "python"
        if sys.platform == "win32":
            venv_py = ALEAPP_CLONE_ROOT / ".venv" / "Scripts" / "python.exe"
        if venv_py.is_file():
            return [str(venv_py.resolve()), str(cloned.resolve())]
        return [sys.executable, str(cloned.resolve())]
    for name in ("aleapp.py", "ALEAPP/aleapp.py"):
        p = Path(name)
        if p.is_file():
            return [sys.executable, str(p.resolve())]
    try:
        probe = subprocess.run(
            [sys.executable, "-m", "aleapp", "--help"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if probe.returncode == 0 or "usage" in (probe.stdout + probe.stderr).lower():
            return [sys.executable, "-m", "aleapp"]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _mobsf_url_from_env() -> str:
    return (os.environ.get("MOBSF_URL") or "http://127.0.0.1:8000").rstrip("/")


def mobsf_reachable(url: str) -> bool:
    try:
        req = urllib.request.Request(url + "/", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status < 500
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def resolve_external_tools(config: AppConfig) -> None:
    config.adb_path = find_adb_exe(config.operating_system)
    config.msfvenom_path = find_msfvenom()
    config.msfconsole_path = find_msfconsole()
    config.scrcpy_path = find_scrcpy(config.operating_system)
    config.nmap_path = find_nmap()
    config.hardax_argv0 = find_hardax_argv0()
    config.lockknife_path = find_lockknife()
    config.drozer_path = find_drozer()
    config.frida_path = find_frida()
    config.objection_path = find_objection()
    config.aleapp_argv0 = find_aleapp_argv0()
    config.mobsf_url = _mobsf_url_from_env()


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


def require_lockknife(config: AppConfig) -> bool:
    from modules.console import print_error

    if not config.lockknife_path:
        resolve_external_tools(config)
    if not config.lockknife_path:
        print_error(
            "LockKnife is not on PATH (needs Python 3.12+ on the host). "
            "Install: brew install ImKKingshuk/tap/lockknife or "
            "curl -fsSL https://lockknife.vercel.app/install | bash"
        )
        return False
    return True


def require_drozer(config: AppConfig) -> bool:
    from modules.console import print_error

    if not config.drozer_path:
        resolve_external_tools(config)
    if not config.drozer_path:
        print_error(
            "drozer console not found. Install: pip install drozer "
            "(or ./install.sh --components drozer,pip). See README."
        )
        return False
    return True


def require_frida(config: AppConfig) -> bool:
    from modules.console import print_error

    if not config.frida_path:
        resolve_external_tools(config)
    if not config.frida_path:
        print_error(
            "Frida not found. Install frida-tools "
            "(./install.sh --components frida,pip). See README."
        )
        return False
    return True


def require_objection(config: AppConfig) -> bool:
    from modules.console import print_error

    if not config.objection_path:
        resolve_external_tools(config)
    if not config.objection_path:
        print_error(
            "objection not found. Install: pip install objection "
            "(./install.sh --components objection,pip). See README."
        )
        return False
    return True


def require_aleapp(config: AppConfig) -> bool:
    from modules.console import print_error

    if not config.aleapp_argv0:
        resolve_external_tools(config)
    if not config.aleapp_argv0:
        print_error(
            "ALEAPP not found. Clone https://github.com/abrignoni/ALEAPP and run "
            "python aleapp.py, or add aleapp to PATH. See README."
        )
        return False
    return True


def require_mobsf(config: AppConfig) -> bool:
    from modules.console import print_error

    config.mobsf_url = _mobsf_url_from_env()
    if not mobsf_reachable(config.mobsf_url):
        print_error(
            f"MobSF server not reachable at {config.mobsf_url}. "
            "Start Docker: docker run --rm -p 8000:8000 "
            "opensecurity/mobile-security-framework-mobsf:latest"
        )
        return False
    return True


def lockknife_needs_cli_flag(config: AppConfig) -> bool:
    global _LOCKKNIFE_USE_CLI
    if _LOCKKNIFE_USE_CLI is not None:
        return _LOCKKNIFE_USE_CLI
    path = config.lockknife_path or find_lockknife()
    if not path:
        _LOCKKNIFE_USE_CLI = False
        return False
    try:
        probe = subprocess.run(
            [path, "--help"],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        _LOCKKNIFE_USE_CLI = False
        return False
    help_text = (probe.stdout or "") + (probe.stderr or "")
    _LOCKKNIFE_USE_CLI = "--cli" in help_text or "--headless" in help_text
    return _LOCKKNIFE_USE_CLI


def lockknife_argv(config: AppConfig, extra: list[str], *, serial: str | None = None) -> list[str]:
    base = [config.lockknife_path or "lockknife"]
    if lockknife_needs_cli_flag(config):
        base.append("--cli")
    argv = base + extra
    has_serial_flag = any(flag in extra for flag in ("-s", "--serial"))
    if serial and not has_serial_flag:
        argv.extend(["-s", serial])
    return argv


def drozer_argv(config: AppConfig, extra: list[str]) -> list[str]:
    return [config.drozer_path or "drozer"] + extra


def drozer_console_argv(config: AppConfig, command: str) -> list[str]:
    return drozer_argv(
        config,
        ["console", "connect", "--no-password", "--no-ssl", "-c", command],
    )


def objection_argv(
    config: AppConfig,
    package: str,
    serial: str,
    run_args: list[str],
    *,
    spawn: bool = False,
) -> list[str]:
    base = [config.objection_path or "objection", "-n", package, "-S", serial]
    if spawn:
        return base + ["-s", "start", "--startup-command", " ".join(run_args)]
    return base + ["run", *run_args]


def aleapp_argv(config: AppConfig, extra: list[str]) -> list[str]:
    base = config.aleapp_argv0 or find_aleapp_argv0() or [sys.executable, "aleapp.py"]
    return base + extra


def scrcpy_argv(config: AppConfig, args: list[str]) -> list[str]:
    """Build argv for subprocess; caller must ensure require_scrcpy(config) first."""
    return [config.scrcpy_path or "scrcpy"] + args
