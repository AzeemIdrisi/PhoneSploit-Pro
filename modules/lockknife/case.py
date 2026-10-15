from __future__ import annotations

from pathlib import Path

from modules.config import AppConfig
from modules.console import ask, confirm, print_success
from modules.ext_runner import report_dir
from modules.lockknife._common import open_category, run_lk


def _init(config: AppConfig) -> None:
    case_id = ask("Case ID [PhoneSploitCase]: ").strip() or "PhoneSploitCase"
    examiner = ask("Examiner name [Analyst]: ").strip() or "Analyst"
    title = ask("Case title [Android assessment]: ").strip() or "Android assessment"
    out = report_dir("lockknife") / "cases" / case_id
    out.mkdir(parents=True, exist_ok=True)
    run_lk(
        config,
        [
            "case",
            "init",
            "--case-id",
            case_id,
            "--examiner",
            examiner,
            "--title",
            title,
            "--output",
            str(out),
        ],
        need_device=False,
    )
    config.lockknife_case_dir = str(out.resolve())
    print_success(f"Active case: {config.lockknife_case_dir}")


def _use_existing(config: AppConfig) -> None:
    path = ask("Case directory path: ").strip()
    if path and Path(path).is_dir():
        config.lockknife_case_dir = str(Path(path).resolve())
        print_success(f"Active case: {config.lockknife_case_dir}")
    elif config.lockknife_case_dir and confirm(f"Keep current case {config.lockknife_case_dir}?"):
        return


def _summary(config: AppConfig) -> None:
    case = config.lockknife_case_dir or ask("Case directory: ").strip()
    if not case:
        return
    run_lk(config, ["case", "summary", "--case-dir", case], need_device=False)


def _export(config: AppConfig) -> None:
    case = config.lockknife_case_dir or ask("Case directory: ").strip()
    if not case:
        return
    dest = ask("Export zip path: ").strip()
    if not dest:
        dest = str(report_dir("lockknife") / "case-export.zip")
    args = ["case", "export", "--case-dir", case, "--include-registered-artifacts", "--output", dest]
    run_lk(config, args, need_device=False)


def _doctor(config: AppConfig) -> None:
    run_lk(config, ["doctor"], need_device=False)


def _features(config: AppConfig) -> None:
    run_lk(config, ["features"], need_device=False)


def open_menu(config: AppConfig) -> None:
    open_category(
        config,
        "lockknife-case",
        "Case",
        [
            ("Init new case", _init),
            ("Set active case directory", _use_existing),
            ("Case summary", _summary),
            ("Export case bundle", _export),
            ("Doctor (host checks)", _doctor),
            ("Features / capabilities", _features),
        ],
    )
