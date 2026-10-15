from __future__ import annotations

from modules.config import AppConfig
from modules.ext_runner import authorized_warning, preflight_serial, report_dir, run_captured
from modules.tools import lockknife_argv, require_lockknife


def _append_case_dir(config: AppConfig, args: list[str]) -> list[str]:
    case = (config.lockknife_case_dir or "").strip()
    if not case:
        return args
    if "--case-dir" in args or "--case_dir" in args:
        return args
    supports_case = args and args[0] in (
        "extract",
        "forensics",
        "network",
        "crypto-wallet",
        "runtime",
        "report",
    )
    if supports_case or (len(args) >= 2 and args[0] == "crack" and args[1] in ("pin-device", "gesture", "wifi")):
        return [*args, "--case-dir", case]
    return args


def run_lk(
    config: AppConfig,
    args: list[str],
    *,
    serial: str | None = None,
    need_device: bool = True,
    timeout: float | None = None,
) -> bool:
    if not require_lockknife(config):
        return False
    if need_device:
        serial = serial or preflight_serial()
        if not serial:
            return False
    out = report_dir("lockknife")
    args = list(args)
    args = _append_case_dir(config, args)
    if "--output" not in args and "--output-dir" not in args and "-o" not in args:
        if any(x in args for x in ("pin-device", "gesture", "wifi", "keystore", "passkeys")):
            args = [*args, "--output-dir", str(out)]
        elif args and args[0] in ("extract", "forensics", "apk", "report", "security", "network", "crypto-wallet", "exploit", "crack"):
            pass
    argv = lockknife_argv(config, args, serial=serial if need_device else None)
    run_captured(argv, timeout=timeout)
    return True


def open_category(config: AppConfig, hub_key: str, title: str, actions) -> None:
    if not require_lockknife(config):
        return
    if not authorized_warning(hub_key, "LockKnife"):
        return
    from modules.ext_runner import run_internal_menu

    run_internal_menu(config, ["Main Menu", "LockKnife", title], actions)
