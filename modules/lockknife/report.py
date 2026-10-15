from __future__ import annotations

from modules.config import AppConfig
from modules.console import ask
from modules.lockknife._common import open_category, run_lk


def _generate(config: AppConfig) -> None:
    case = ask("Case / evidence directory: ").strip()
    fmt = ask("Format (html|json|csv|pdf) [html]: ").strip() or "html"
    template = ask("Template (optional, e.g. technical) [default]: ").strip()
    args = ["report", "generate", "--case-dir", case, "--format", fmt]
    if template:
        args.extend(["--template", template])
    run_lk(config, args, need_device=False)


def _chain(config: AppConfig) -> None:
    case = ask("Case directory: ").strip()
    run_lk(config, ["report", "chain-of-custody", "--case-dir", case], need_device=False)


def _integrity(config: AppConfig) -> None:
    case = ask("Case directory: ").strip()
    run_lk(config, ["report", "integrity", "--case-dir", case], need_device=False)


def open_menu(config: AppConfig) -> None:
    open_category(
        config,
        "lockknife-report",
        "Report",
        [
            ("Generate report", _generate),
            ("Chain of custody", _chain),
            ("Integrity check", _integrity),
        ],
    )
