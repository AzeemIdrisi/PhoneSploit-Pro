from __future__ import annotations

from modules.config import AppConfig
from modules.console import ask, confirm
from modules.ext_runner import report_dir
from modules.lockknife._common import open_category, run_lk
from modules.tools import require_aleapp


def _snapshot(config: AppConfig) -> None:
    full = confirm("Include full snapshot (--full)?")
    out = report_dir("lockknife") / "snapshot.tar"
    args = ["forensics", "snapshot", "--output", str(out)]
    if full:
        args.append("--full")
    run_lk(config, args)


def _sqlite(config: AppConfig) -> None:
    db = ask("SQLite DB path on device or host: ").strip()
    out = report_dir("lockknife") / "sqlite.json"
    run_lk(config, ["forensics", "sqlite", db, "--output", str(out)], need_device=False)


def _timeline(config: AppConfig) -> None:
    src = ask("Artifact file path: ").strip()
    out = report_dir("lockknife") / "timeline.json"
    run_lk(
        config,
        ["forensics", "timeline", "--parsed-artifacts", src, "--output", str(out)],
        need_device=False,
    )


def _parse_dir(config: AppConfig) -> None:
    indir = ask("Input directory: ").strip()
    out = report_dir("lockknife") / "parse.json"
    run_lk(
        config,
        ["forensics", "parse", "--input-dir", indir, "--output", str(out)],
        need_device=False,
    )


def _import_aleapp(config: AppConfig) -> None:
    indir = ask("ALEAPP output directory: ").strip()
    out = report_dir("lockknife") / "import-aleapp.json"
    run_lk(
        config,
        ["forensics", "import-aleapp", indir, "--output", str(out)],
        need_device=False,
    )


def _handoff_aleapp(config: AppConfig) -> None:
    if require_aleapp(config):
        from modules.aleapp import run_parse_menu

        run_parse_menu(config)


def _correlate(config: AppConfig) -> None:
    first = ask("First input file: ").strip()
    second = ask("Second input file (optional): ").strip()
    out = report_dir("lockknife") / "correlate.json"
    args = ["forensics", "correlate", "--input", first, "--output", str(out)]
    if second:
        args.extend(["--input", second])
    run_lk(config, args, need_device=False)


def _recover(config: AppConfig) -> None:
    db = ask("Database path: ").strip()
    out = report_dir("lockknife") / "recover.db"
    run_lk(config, ["forensics", "recover", db, "--output", str(out)], need_device=False)


def _carve(config: AppConfig) -> None:
    src = ask("Input file/image: ").strip()
    out = report_dir("lockknife") / "carve"
    run_lk(
        config,
        ["forensics", "carve", src, "--output-dir", str(out)],
        need_device=False,
    )


def open_menu(config: AppConfig) -> None:
    open_category(
        config,
        "lockknife-forensics",
        "Forensics",
        [
            ("Device snapshot (tar)", _snapshot),
            ("SQLite inspect", _sqlite),
            ("Timeline from artifacts", _timeline),
            ("Parse evidence directory", _parse_dir),
            ("Import ALEAPP output", _import_aleapp),
            ("Open ALEAPP hub (full parser)", _handoff_aleapp),
            ("Correlate inputs", _correlate),
            ("Recover deleted (best-effort)", _recover),
            ("Carve from image", _carve),
        ],
    )
