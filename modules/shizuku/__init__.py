"""Shizuku APK install and lifecycle over ADB."""

from __future__ import annotations

from modules.config import AppConfig
from modules.console import adb, adb_output, ask, print_error, print_success, print_warning
from modules.ext_runner import adb_install_apk, authorized_warning, github_release_asset, preflight_serial
from modules.tools import require_adb

SHIZUKU_PKG = "moe.shizuku.privileged.api"
SHIZUKU_PERM_MARKERS = (
    "moe.shizuku.privileged.api.permission.API_V23",
    "moe.shizuku.api.permission.API_V23",
    "moe.shizuku.api.ShizukuProvider",
)
START_CANDIDATES = (
    f"/sdcard/Android/data/{SHIZUKU_PKG}/start.sh",
    f"/storage/emulated/0/Android/data/{SHIZUKU_PKG}/start.sh",
)
ROOT_START_SH = "/data/adb/shizuku/start.sh"


def _ensure_authorized(config: AppConfig) -> bool:
    if not require_adb(config):
        return False
    if not authorized_warning("shizuku", "Shizuku"):
        return False
    return preflight_serial() is not None


def sh_install(config: AppConfig) -> None:
    if not _ensure_authorized(config):
        return
    apk = github_release_asset("RikkaApps", "Shizuku", ".apk")
    if apk:
        adb_install_apk(apk)


def _run_start_script(script: str) -> bool:
    result = adb(["shell", "sh", script])
    if result.returncode == 0:
        print_success(f"start.sh invoked ({script}) — approve on device if prompted.")
        return True
    detail = (result.stdout + result.stderr).strip() or f"exit {result.returncode}"
    print_warning(f"start.sh failed for {script}: {detail}")
    return False


def sh_start(config: AppConfig) -> None:
    if not _ensure_authorized(config):
        return
    for script in START_CANDIDATES:
        test = adb(["shell", "test", "-f", script])
        if test.returncode == 0 and _run_start_script(script):
            return
    test_root = adb(["shell", "su", "-c", f"test -f {ROOT_START_SH}"])
    if test_root.returncode == 0:
        result = adb(["shell", "su", "-c", f"sh {ROOT_START_SH}"])
        if result.returncode == 0:
            print_success(f"start.sh invoked ({ROOT_START_SH}) — approve on device if prompted.")
            return
        detail = (result.stdout + result.stderr).strip() or f"exit {result.returncode}"
        print_error(f"Root start.sh failed: {detail}")
        return
    print_warning(
        "No start.sh found. Open the Shizuku app once on the device so it can install start.sh."
    )
    adb(["shell", "monkey", "-p", SHIZUKU_PKG, "1"])


def _shizuku_version() -> str:
    dump = adb_output(["shell", "dumpsys", "package", SHIZUKU_PKG])
    for line in dump.splitlines():
        line = line.strip()
        if line.startswith("versionName="):
            return line.split("=", 1)[1].strip()
        if "versionName" in line and "=" in line:
            return line.split("=", 1)[1].strip()
    return ""


def sh_status(config: AppConfig) -> None:
    if not _ensure_authorized(config):
        return
    ver = _shizuku_version()
    if ver:
        print_success(f"Installed Shizuku version: {ver}")
    out = adb_output(["shell", "dumpsys", "activity", "service", SHIZUKU_PKG])
    from rich.panel import Panel
    from modules.console import console

    console.print(Panel(out.strip() or "(no output)", title="Shizuku dumpsys", border_style="cyan"))
    svc = adb_output(["shell", "service", "list"])
    for line in svc.splitlines():
        if "shizuku" in line.lower():
            console.print(f"[green]{line.strip()}[/green]")


def sh_stop(config: AppConfig) -> None:
    if not _ensure_authorized(config):
        return
    result = adb(["shell", "am", "force-stop", SHIZUKU_PKG])
    if result.returncode != 0:
        print_error("Could not force-stop Shizuku.")
        return
    print_success("Shizuku app force-stopped.")


def sh_launch_app(config: AppConfig) -> None:
    if not _ensure_authorized(config):
        return
    adb(["shell", "monkey", "-p", SHIZUKU_PKG, "1"])


def _shizuku_client_packages() -> list[str]:
    dump = adb_output(["shell", "dumpsys", "package"])
    clients: list[str] = []
    current: str | None = None
    for line in dump.splitlines():
        stripped = line.strip()
        if stripped.startswith("Package [") and stripped.endswith("]"):
            current = stripped.split("[", 1)[1].rstrip("]")
            continue
        if not current or current == SHIZUKU_PKG:
            continue
        if any(marker in line for marker in SHIZUKU_PERM_MARKERS):
            if current not in clients:
                clients.append(current)
    return sorted(clients)


def sh_list_clients(config: AppConfig) -> None:
    if not _ensure_authorized(config):
        return
    from rich.panel import Panel
    from rich.table import Table
    from modules.console import console

    clients = _shizuku_client_packages()
    if not clients:
        console.print(
            Panel(
                "No apps declaring Shizuku API permission/provider were found.",
                title="Shizuku clients",
                border_style="yellow",
            )
        )
        return
    table = Table(title="Shizuku-aware packages", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim")
    table.add_column("Package")
    for idx, pkg in enumerate(clients[:80], start=1):
        table.add_row(str(idx), pkg)
    console.print(table)


def sh_launch_client(config: AppConfig) -> None:
    if not _ensure_authorized(config):
        return
    pkg = ask("Package to launch: ").strip()
    if pkg:
        adb(["shell", "monkey", "-p", pkg, "1"])


def sh_uninstall(config: AppConfig) -> None:
    if not _ensure_authorized(config):
        return
    result = adb(["uninstall", SHIZUKU_PKG])
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        print_error(f"Uninstall failed: {detail or result.returncode}")
        return
    print_success("Shizuku uninstalled.")
