"""ALEAPP dump acquisition and parsing."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from modules.config import AppConfig
from modules.console import ask, confirm, open_file_prompt, print_error, print_option_list, print_success, print_warning
from modules.ext_runner import authorized_warning, preflight_serial, report_dir, run_adb_captured, run_captured
from modules.tools import aleapp_argv, require_aleapp, require_lockknife

_LATEST = Path("Downloaded-Files") / "aleapp" / "latest.json"


def _save_latest(out_dir: Path, html: Path | None) -> None:
    _LATEST.parent.mkdir(parents=True, exist_ok=True)
    _LATEST.write_text(
        json.dumps(
            {
                "out_dir": str(out_dir.resolve()),
                "html": str(html.resolve()) if html else "",
                "saved_at": datetime.now().isoformat(timespec="seconds"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _find_index_html(root: Path) -> Path | None:
    for path in root.rglob("index.html"):
        return path
    return None


_INPUT_TYPES = ("zip", "tar", "fs", "gz", "raw")


def _pick_input_type(default: str = "zip") -> str | None:
    labels = [f"{t}" for t in _INPUT_TYPES]
    print_option_list(labels)
    pick = ask(f"Input type # (1-{len(labels)}) or name [{default}]: ").strip() or default
    if pick.isdigit():
        idx = int(pick) - 1
        if 0 <= idx < len(_INPUT_TYPES):
            return _INPUT_TYPES[idx]
    pick = pick.lower()
    if pick in _INPUT_TYPES:
        return pick
    print_error("Invalid input type.")
    return None


def _run_parse(config: AppConfig, inp: str, typ: str, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    argv = aleapp_argv(config, ["-t", typ, "-i", inp, "-o", str(out)])
    result = run_captured(argv, timeout=3600)
    if result.returncode != 0:
        print_warning("ALEAPP parse did not finish successfully.")
        return
    html = _find_index_html(out)
    if html:
        _save_latest(out, html)
        print_success(f"Report: {html}")
        open_file_prompt(config.opener, str(html.resolve()))
        _offer_lockknife_import(config, out)
    else:
        print_warning(f"Parse finished; no index.html under {out}")


def _offer_lockknife_import(config: AppConfig, out_dir: Path) -> None:
    if not require_lockknife(config):
        return
    if not confirm("Import this ALEAPP output into LockKnife (forensics import-aleapp)?"):
        return
    from modules.lockknife._common import run_lk

    dest = report_dir("lockknife") / "import-aleapp.json"
    run_lk(
        config,
        ["forensics", "import-aleapp", str(out_dir), "--output", str(dest)],
        need_device=False,
    )


def run_parse_menu(config: AppConfig) -> None:
    if not require_aleapp(config):
        return
    if not authorized_warning("aleapp", "ALEAPP"):
        return
    inp = ask("Input dump path (zip/tar/fs/raw image/folder): ").strip()
    if not inp:
        return
    typ = _pick_input_type()
    if not typ:
        return
    out = report_dir("aleapp")
    _run_parse(config, inp, typ, out)


def al_acquire_fs(config: AppConfig) -> None:
    """Pull user-confirmed paths from a rooted device, then parse as ALEAPP fs input."""
    if not preflight_serial():
        return
    if not authorized_warning("aleapp", "ALEAPP"):
        return
    if not require_aleapp(config):
        return
    print_warning("Requires root/adb pull access. Enter one remote path per line; empty line to finish.")
    paths: list[str] = []
    while True:
        line = ask("Remote path (or Enter to finish): ").strip()
        if not line:
            break
        paths.append(line)
    if not paths:
        return
    pull_root = report_dir("aleapp")
    dest = pull_root / "fs_pull"
    dest.mkdir(parents=True, exist_ok=True)
    ok = False
    for remote in paths:
        label = remote.rstrip("/").split("/")[-1] or "data"
        local = dest / label
        result = run_adb_captured(["pull", remote, str(local)], timeout=3600)
        if result.returncode == 0:
            ok = True
        else:
            print_warning(f"adb pull failed for {remote!r}")
    if not ok:
        print_warning("No paths pulled successfully.")
        return
    print_success(f"Pulled data under {dest}")
    if confirm("Run ALEAPP parse on this folder now (-t fs)?"):
        out = pull_root / "report"
        _run_parse(config, str(dest), "fs", out)


def al_acquire_tar(config: AppConfig) -> None:
    """Create a tar on device (root) of common paths, pull, and parse with ALEAPP."""
    if not preflight_serial():
        return
    if not authorized_warning("aleapp", "ALEAPP"):
        return
    if not require_aleapp(config):
        return
    print_warning(
        "Requires root (su). Archives /data/data, /data/system, /data/misc — large and slow on some devices."
    )
    remote_tar = "/sdcard/phonesploit_aleapp.tar"
    paths = "/data/data /data/system /data/misc"
    tar_cmd = f"su -c 'tar -cf {remote_tar} {paths} 2>/dev/null'"
    result = run_adb_captured(["shell", tar_cmd], timeout=3600)
    if result.returncode != 0:
        print_warning("tar on device failed — ensure root/su access.")
        return
    pull_root = report_dir("aleapp")
    local_tar = pull_root / "device_pull.tar"
    pull = run_adb_captured(["pull", remote_tar, str(local_tar)], timeout=3600)
    run_adb_captured(["shell", "rm", "-f", remote_tar], timeout=60)
    if pull.returncode != 0 or not local_tar.is_file():
        print_warning("adb pull of tar failed.")
        return
    print_success(f"Pulled tar to {local_tar}")
    if confirm("Run ALEAPP parse on this tar now (-t tar)?"):
        out = pull_root / "report_tar"
        _run_parse(config, str(local_tar), "tar", out)


def al_acquire_backup(config: AppConfig) -> None:
    if not preflight_serial():
        return
    if not authorized_warning("aleapp", "ALEAPP"):
        return
    dest = report_dir("aleapp") / "backup.ab"
    print_warning(
        "Full adb backup may require user confirmation on device. "
        "ALEAPP does not parse .ab directly — convert to tar/fs or use rooted tar pull instead."
    )
    result = run_adb_captured(["backup", "-all", "-f", str(dest)], timeout=600)
    if result.returncode != 0 or not dest.is_file() or dest.stat().st_size == 0:
        print_warning("adb backup failed or produced an empty file.")
        return
    print_success(f"Backup written to {dest} — convert externally or use Acquire rooted tar.")


def al_open_last(config: AppConfig) -> None:
    if not _LATEST.is_file():
        print_warning("No previous ALEAPP run recorded.")
        return
    data = json.loads(_LATEST.read_text(encoding="utf-8"))
    html = data.get("html") or ""
    if html and Path(html).is_file():
        open_file_prompt(config.opener, html)
    else:
        print_warning("Last report HTML is missing.")
