from __future__ import annotations

from modules.config import AppConfig
from modules.console import ask
from modules.ext_runner import report_dir
from modules.lockknife._common import open_category, run_lk


def _browser(config: AppConfig) -> None:
    app = ask("Browser (chrome|edge|brave|opera|firefox) [chrome]: ").strip() or "chrome"
    kind = ask("Kind (history|bookmarks|downloads|cookies|passwords|all) [all]: ").strip() or "all"
    out = report_dir("lockknife") / f"browser-{app}.json"
    run_lk(
        config,
        ["extract", "browser", "--app", app, "--kind", kind, "--output", str(out)],
    )


def _messaging(config: AppConfig) -> None:
    app = ask("App (telegram|signal) [telegram]: ").strip() or "telegram"
    mode = ask("Mode (messages|artifacts) [artifacts]: ").strip() or "artifacts"
    out = report_dir("lockknife") / f"messaging-{app}.json"
    run_lk(
        config,
        ["extract", "messaging", "--app", app, "--mode", mode, "--output", str(out)],
    )


def _media(config: AppConfig) -> None:
    out = report_dir("lockknife") / "media-exif"
    run_lk(config, ["extract", "media", "--output", str(out)])


def _location(config: AppConfig) -> None:
    mode = ask("Mode (snapshot|artifacts) [snapshot]: ").strip() or "snapshot"
    out = report_dir("lockknife") / "location.json"
    run_lk(config, ["extract", "location", "--mode", mode, "--output", str(out)])


def _extract_all(config: AppConfig) -> None:
    out = report_dir("lockknife") / "extract-all"
    run_lk(config, ["extract", "all", "--output", str(out)])


def _sms(config: AppConfig) -> None:
    fmt = ask("Format (json|csv) [json]: ").strip() or "json"
    out = report_dir("lockknife") / f"sms.{fmt}"
    run_lk(config, ["extract", "sms", "--format", fmt, "--output", str(out)])


def _call_logs(config: AppConfig) -> None:
    fmt = ask("Format (json|csv) [json]: ").strip() or "json"
    out = report_dir("lockknife") / f"call-logs.{fmt}"
    run_lk(config, ["extract", "call-logs", "--format", fmt, "--output", str(out)])


def _contacts(config: AppConfig) -> None:
    fmt = ask("Format (json|csv) [json]: ").strip() or "json"
    out = report_dir("lockknife") / f"contacts.{fmt}"
    run_lk(config, ["extract", "contacts", "--format", fmt, "--output", str(out)])


def open_menu(config: AppConfig) -> None:
    open_category(
        config,
        "lockknife-extract",
        "Extract extras",
        [
            ("SMS", _sms),
            ("Call logs", _call_logs),
            ("Contacts", _contacts),
            ("Browser artifacts", _browser),
            ("Telegram / Signal artifacts", _messaging),
            ("Media with EXIF", _media),
            ("Location artifacts", _location),
            ("Extract-all evidence dir", _extract_all),
        ],
    )
