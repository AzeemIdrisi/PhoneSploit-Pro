from __future__ import annotations

from pathlib import Path

from modules.config import AppConfig
from modules.console import ask, print_error
from modules.ext_runner import pick_package, pull_apk_to_local, report_dir
from modules.lockknife._common import open_category, run_lk
from modules.tools import require_mobsf


def _apk_path_or_pull(config: AppConfig) -> str | None:
    local = ask("Local APK path (leave empty to use package on device): ").strip()
    if local:
        p = Path(local)
        if not p.is_file():
            print_error(f"APK not found: {local}")
            return None
        return str(p.resolve())
    pkg = pick_package(config)
    if not pkg:
        return None
    out = report_dir("lockknife") / f"{pkg}.apk"
    pulled = pull_apk_to_local(pkg, out)
    return str(pulled) if pulled else None


def _permissions(config: AppConfig) -> None:
    apk = _apk_path_or_pull(config)
    if not apk:
        return
    run_lk(config, ["apk", "permissions", apk], need_device=False)


def _analyze(config: AppConfig) -> None:
    apk = _apk_path_or_pull(config)
    if not apk:
        return
    out = report_dir("lockknife") / "apk-analyze.json"
    run_lk(config, ["apk", "analyze", apk, "--output", str(out)], need_device=False)


def _decompile(config: AppConfig) -> None:
    apk = _apk_path_or_pull(config)
    if not apk:
        return
    mode = ask("Decompile mode (auto|jadx|apktool) [auto]: ").strip() or "auto"
    out = report_dir("lockknife") / "decompile"
    run_lk(config, ["apk", "decompile", apk, "--mode", mode, "--output", str(out)], need_device=False)


def _vulnerability(config: AppConfig) -> None:
    apk = _apk_path_or_pull(config)
    if not apk:
        return
    out = report_dir("lockknife") / "apk-vuln.json"
    run_lk(config, ["apk", "vulnerability", apk, "--output", str(out)], need_device=False)


def _scan(config: AppConfig) -> None:
    apk = _apk_path_or_pull(config)
    if not apk:
        return
    rule = ask("YARA rule path: ").strip()
    run_lk(
        config,
        ["apk", "scan", "--apk", apk, "--yara", rule],
        need_device=False,
    )


def _mobsf_handoff(config: AppConfig) -> None:
    if require_mobsf(config):
        from modules.mobsf import scan_apk_menu

        scan_apk_menu(config)


def open_menu(config: AppConfig) -> None:
    open_category(
        config,
        "lockknife-apk",
        "APK (thin)",
        [
            ("Manifest / permissions", _permissions),
            ("Analyze APK", _analyze),
            ("Decompile APK", _decompile),
            ("APK vulnerability scan", _vulnerability),
            ("YARA scan", _scan),
            ("Full static analysis (MobSF hub)", _mobsf_handoff),
        ],
    )
