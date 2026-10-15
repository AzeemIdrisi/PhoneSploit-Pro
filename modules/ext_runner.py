"""Shared helpers for external tool CLIs (LockKnife, drozer, Frida, etc.)."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from rich.panel import Panel

from modules.config import AppConfig
from modules.connection import list_ready_device_serials
from modules.console import (
    adb,
    ask,
    clear_terminal,
    confirm,
    console,
    get_adb_executable,
    print_error,
    print_option_list,
    print_success,
    print_warning,
    show_options,
)

CACHE_ROOT = Path.home() / ".phonesploit-pro" / "cache"
DOWNLOADED_ROOT = Path("Downloaded-Files")
_AUTHORIZED_HUBS: set[str] = set()
_CHECKSUM_SUFFIXES = (".sha256", ".sha1", ".asc", ".sig", ".md5", ".checksum")


def preflight_serial() -> str | None:
    ready = list_ready_device_serials()
    if not ready:
        print_error("No authorized ADB device connected.")
        return None
    serial = os.environ.get("ANDROID_SERIAL", "").strip()
    if not serial:
        if len(ready) == 1:
            return ready[0]
        print_error(
            "Multiple devices connected. Select a device at startup or set ANDROID_SERIAL."
        )
        return None
    if serial not in ready:
        print_error(f"Selected device {serial!r} is not in the ready device list.")
        return None
    return serial


def report_dir(tool: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = DOWNLOADED_ROOT / tool / stamp
    path.mkdir(parents=True, exist_ok=True)
    return path


def _print_captured_output(argv: list[str], result: subprocess.CompletedProcess[str]) -> None:
    combined = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    title = argv[0] if argv else "command"
    if combined:
        if combined.lstrip().startswith("{") or combined.lstrip().startswith("["):
            try:
                console.print_json(combined)
            except json.JSONDecodeError:
                console.print(Panel(combined, title=title, border_style="cyan"))
        else:
            console.print(Panel(combined, title=title, border_style="cyan"))
    if err:
        console.print(Panel(err, title=f"{title} (stderr)", border_style="yellow"))
    if result.returncode != 0:
        print_warning(f"Exit code {result.returncode}")


def run_captured(
    argv: list[str],
    *,
    timeout: float | None = None,
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        print_error(f"Command timed out after {timeout}s: {' '.join(argv)}")
        if out.strip():
            console.print(Panel(out.strip(), title="stdout (partial)", border_style="dim"))
        if err.strip():
            console.print(Panel(err.strip(), title="stderr (partial)", border_style="red"))
        return subprocess.CompletedProcess(argv, returncode=124, stdout=out, stderr=err)
    except OSError as exc:
        print_error(f"Failed to run {' '.join(argv)}: {exc}")
        return subprocess.CompletedProcess(argv, returncode=127, stdout="", stderr=str(exc))

    _print_captured_output(argv, result)
    return result


def run_adb_captured(args: list[str], *, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    """Run adb via resolved executable; returns synthetic failure if adb unavailable."""
    exe = get_adb_executable()
    if not exe:
        print_error("ADB is not available.")
        return subprocess.CompletedProcess(["adb", *args], returncode=127, stdout="", stderr="adb not available")
    return run_captured([exe, *args], timeout=timeout)


def resolve_base_apk_path(pm_path_output: str) -> str | None:
    """Pick base.apk from `pm path` output (split APKs emit multiple package: lines)."""
    lines = [ln.strip() for ln in pm_path_output.splitlines() if ln.strip()]
    paths: list[str] = []
    for line in lines:
        if line.startswith("package:"):
            paths.append(line.split(":", 1)[1].strip())
    if not paths:
        return None
    for p in paths:
        if p.endswith("base.apk"):
            return p
    return paths[0]


def pull_apk_to_local(package: str, dest: Path) -> Path | None:
    from modules.console import adb_output

    raw = adb_output(["shell", "pm", "path", package])
    remote = resolve_base_apk_path(raw)
    if not remote:
        print_error(f"Could not resolve APK path for {package!r}.")
        return None
    result = run_adb_captured(["pull", remote, str(dest)])
    if result.returncode != 0 or not dest.is_file():
        print_error(f"adb pull failed for {package!r}.")
        return None
    return dest


def _pick_release_asset(assets: list, name_substr: str) -> dict | None:
    needle = name_substr.lower()
    candidates: list[dict] = []
    for asset in assets:
        name = (asset.get("name") or "").lower()
        if needle not in name:
            continue
        if any(name.endswith(s) for s in _CHECKSUM_SUFFIXES):
            continue
        candidates.append(asset)
    if not candidates:
        return None
    apk_matches = [a for a in candidates if (a.get("name") or "").lower().endswith(".apk")]
    if apk_matches:
        return apk_matches[0]
    return candidates[0]


def github_release_asset(
    owner: str,
    repo: str,
    name_substr: str,
    *,
    quiet: bool = False,
) -> Path | None:
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    api = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    req = urllib.request.Request(api, headers={"User-Agent": "PhoneSploit-Pro"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        if not quiet:
            print_error(f"Could not fetch GitHub release for {owner}/{repo}: {exc}")
        return None

    assets = payload.get("assets") or []
    match = _pick_release_asset(assets, name_substr)
    if not match:
        if not quiet:
            print_error(f"No release asset matching {name_substr!r} for {owner}/{repo}.")
        return None

    url = match.get("browser_download_url")
    filename = match.get("name") or "download"
    expected_size = int(match.get("size") or 0)
    dest = CACHE_ROOT / filename
    if dest.is_file():
        size = dest.stat().st_size
        if expected_size <= 0 or size >= max(expected_size // 2, 1024):
            return dest

    if not quiet:
        print_warning(f"Downloading {filename}…")
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "PhoneSploit-Pro"}),
            timeout=300,
        ) as resp:
            data = resp.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        if not quiet:
            print_error(f"Download failed: {exc}")
        return None
    if expected_size and len(data) < expected_size // 2:
        if not quiet:
            print_error(f"Download incomplete for {filename} ({len(data)} bytes).")
        return None
    dest.write_bytes(data)
    return dest


def authorized_warning(hub_key: str, tool_label: str) -> bool:
    if hub_key in _AUTHORIZED_HUBS:
        return True
    ok = confirm(
        f"[bold red]Authorized testing only.[/bold red] {tool_label} can access sensitive "
        "device data or change security posture. Continue?"
    )
    if ok:
        _AUTHORIZED_HUBS.add(hub_key)
    return ok


def adb_install_apk(apk: Path) -> bool:
    adb_exe = get_adb_executable() or "adb"
    install = subprocess.run(
        [adb_exe, "install", "-r", str(apk)],
        capture_output=True,
        text=True,
    )
    if install.returncode != 0 and "INSTALL_FAILED_DEPRECATED_SDK_VERSION" in (
        install.stdout + install.stderr
    ):
        print_warning(
            "Device rejects old targetSdkVersion — retrying with --bypass-low-target-sdk-block…"
        )
        install = subprocess.run(
            [
                adb_exe,
                "install",
                "--bypass-low-target-sdk-block",
                "-r",
                str(apk),
            ],
            capture_output=True,
            text=True,
        )
    if install.returncode != 0:
        detail = (install.stdout + install.stderr).strip() or f"exit {install.returncode}"
        print_error(f"adb install failed: {detail}")
        return False
    print_success(f"Installed {apk.name}")
    return True


def pick_package(config: AppConfig) -> str | None:
    last = (config.ext_target_package or "").strip()
    if last and confirm(f"Use target app [bold cyan]{last}[/bold cyan]?"):
        return last
    from modules.app_manager import select_package_from_list

    pkg = select_package_from_list(config)
    if pkg:
        config.ext_target_package = pkg
    return pkg


MenuAction = tuple[str, Callable[[AppConfig], None]]


def run_internal_menu(
    config: AppConfig,
    breadcrumb: list[str],
    actions: list[MenuAction],
) -> None:
    labels = [label for label, _ in actions]

    def _render() -> None:
        show_options(config, breadcrumb[-1], labels, breadcrumb=breadcrumb)

    _render()
    while True:
        choice = ask("Select option (0 = back): ").strip().lower()
        if choice in ("0", "b", "back"):
            clear_terminal(config)
            return
        if choice == "99":
            _render()
            continue
        if not choice.isdigit():
            print_error("Invalid selection")
            print_option_list(labels)
            continue
        idx = int(choice)
        if idx < 1 or idx > len(actions):
            print_error("Invalid selection")
            print_option_list(labels)
            continue
        _, handler = actions[idx - 1]
        console.print()
        handler(config)
        console.print()
        _render()


def drozer_agent_packages() -> list[str]:
    return ["com.mwr.dz", "com.reversec.dz"]


def drozer_installed_package() -> str | None:
    for pkg in drozer_agent_packages():
        out = adb(["shell", "pm", "path", pkg])
        if out.returncode == 0 and "package:" in (out.stdout or ""):
            return pkg
    return None


def drozer_forward() -> None:
    adb(["forward", "tcp:31415", "tcp:31415"])


def drozer_start_embedded(agent_pkg: str | None = None) -> bool:
    pkg = agent_pkg or drozer_installed_package() or "com.mwr.dz"
    drozer_forward()
    svc = adb(
        [
            "shell",
            "am",
            "startservice",
            "-n",
            f"{pkg}/.services.ServerService",
            "-c",
            f"{pkg}.START_EMBEDDED",
        ]
    )
    if svc.returncode == 0:
        return True
    print_warning("Embedded server start failed — launching agent UI; tap Enable if prompted.")
    adb(["shell", "monkey", "-p", pkg, "1"])
    return False


def frida_map_abi(raw: str) -> str:
    raw = raw.strip().lower()
    if "arm64" in raw or raw == "aarch64":
        return "arm64"
    if raw.startswith("arm"):
        return "arm"
    if "x86_64" in raw or raw == "amd64":
        return "x86_64"
    if "x86" in raw:
        return "x86"
    return "arm64"


def device_cpu_abi() -> str:
    out = adb(["shell", "getprop", "ro.product.cpu.abi"])
    return frida_map_abi(out.stdout or "arm64-v8a")
