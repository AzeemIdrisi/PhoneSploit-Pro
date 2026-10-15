from __future__ import annotations

from modules.config import AppConfig
from modules.console import ask, confirm
from modules.ext_runner import report_dir
from modules.lockknife._common import open_category, run_lk


def _backup_extract(config: AppConfig) -> None:
    out = report_dir("lockknife") / "backup"
    decrypt = confirm("Attempt decrypt?")
    args = ["exploit", "--lab-mode", "usb", "backup-extract", "-o", str(out)]
    if decrypt:
        args.append("--decrypt")
    if confirm("Include all packages (--include-all)?"):
        args.append("--include-all")
    run_lk(config, args)


def _content_access(config: AppConfig) -> None:
    provider = ask("Provider (contacts|call-log|sms|calendar|settings) [contacts]: ").strip() or "contacts"
    out = report_dir("lockknife") / f"content-{provider}.xml"
    run_lk(
        config,
        [
            "exploit",
            "usb",
            "content-access",
            "--provider",
            provider,
            "--output",
            str(out),
        ],
    )


def _intent_inject(config: AppConfig) -> None:
    if not confirm("[bold red]Lab mode[/bold red] intent injection — continue?"):
        return
    component = ask("Component PKG/ActivityClass: ").strip()
    run_lk(
        config,
        [
            "exploit",
            "--lab-mode",
            "usb",
            "intent-inject",
            "--operation",
            "start",
            "--component",
            component,
        ],
    )


def _lock_bypass(config: AppConfig) -> None:
    if not confirm("[bold red]Lock bypass[/bold red] — authorized lab use only?"):
        return
    method = ask("Method (ui-automation|screenshot|backup) [ui-automation]: ").strip() or "ui-automation"
    run_lk(
        config,
        ["exploit", "--lab-mode", "usb", "lock-bypass", "--method", method],
    )


def _other_vectors(config: AppConfig) -> None:
    run_lk(config, ["exploit", "--help"], need_device=False)


def open_menu(config: AppConfig) -> None:
    open_category(
        config,
        "lockknife-usb",
        "USB exploit (official CLI)",
        [
            ("Backup extract", _backup_extract),
            ("Content provider access", _content_access),
            ("Intent injection (lab mode)", _intent_inject),
            ("Lock bypass (lab mode)", _lock_bypass),
            ("Other exploit vectors (help)", _other_vectors),
        ],
    )
