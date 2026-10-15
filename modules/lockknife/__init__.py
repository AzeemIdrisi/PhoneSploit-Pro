"""LockKnife menu-driven CLI wrappers."""

from __future__ import annotations

import subprocess

from modules.config import AppConfig
from modules.ext_runner import authorized_warning
from modules.lockknife import apk, case, crack, extract, forensics, report, security, usb
from modules.tools import require_lockknife


def lk_case(config: AppConfig) -> None:
    case.open_menu(config)


def lk_crack(config: AppConfig) -> None:
    crack.open_menu(config)


def lk_extract(config: AppConfig) -> None:
    extract.open_menu(config)


def lk_forensics(config: AppConfig) -> None:
    forensics.open_menu(config)


def lk_apk(config: AppConfig) -> None:
    apk.open_menu(config)


def lk_report(config: AppConfig) -> None:
    report.open_menu(config)


def lk_security(config: AppConfig) -> None:
    security.open_menu(config)


def lk_usb(config: AppConfig) -> None:
    usb.open_menu(config)


def lk_interactive(config: AppConfig) -> None:
    if not require_lockknife(config):
        return
    if not authorized_warning("lockknife-interactive", "LockKnife"):
        return
    from modules.ext_runner import preflight_serial

    serial = preflight_serial()
    argv = [config.lockknife_path or "lockknife"]
    if serial:
        argv.extend(["-s", serial])
    subprocess.run(argv)
