"""MobSF REST static analysis."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

from rich.panel import Panel
from rich.table import Table

from modules.config import AppConfig
from modules.console import ask, confirm, console, print_error, print_success, print_warning
from modules.ext_runner import (
    authorized_warning,
    pick_package,
    preflight_serial,
    pull_apk_to_local,
    report_dir,
)
from modules.tools import require_mobsf


def _api_key(config: AppConfig) -> str:
    key = (os.environ.get("MOBSF_API_KEY") or "").strip()
    if key:
        return key
    cached = (config.mobsf_api_key or "").strip()
    if cached:
        return cached
    entered = ask("MobSF API key (or set MOBSF_API_KEY): ").strip()
    if entered:
        config.mobsf_api_key = entered
    return entered


def _request(
    config: AppConfig,
    method: str,
    path: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    content_type: str | None = None,
    timeout: float = 120,
) -> tuple[int, bytes]:
    url = config.mobsf_url.rstrip("/") + path
    hdrs = dict(headers or {})
    if content_type:
        hdrs["Content-Type"] = content_type
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        print_error(str(exc))
        return 0, b""


def _auth_headers(key: str) -> dict[str, str]:
    return {"Authorization": key, "X-Mobsf-Api-Key": key}


def _open_mobsf_url(url: str) -> None:
    webbrowser.open(url)


def _resolve_apk(config: AppConfig) -> Path | None:
    local = ask("Local APK path (empty = pull from device): ").strip()
    if local:
        p = Path(local)
        if not p.is_file():
            print_error(f"APK not found: {local}")
            return None
        return p
    if not preflight_serial():
        return None
    pkg = pick_package(config)
    if not pkg:
        return None
    out = report_dir("mobsf") / f"{pkg}.apk"
    return pull_apk_to_local(pkg, out)


def _form_body(fields: dict[str, str]) -> bytes:
    return urllib.parse.urlencode(fields).encode("utf-8")


def _print_findings(report: dict) -> None:
    appsec = report.get("appsec") or {}
    if isinstance(appsec, dict):
        score = appsec.get("security_score") or appsec.get("score")
        if score is not None:
            console.print(Panel(f"Security score: {score}", title="MobSF", border_style="green"))

    table = Table(title="MobSF findings (sample)", show_header=True, header_style="bold cyan")
    table.add_column("Severity")
    table.add_column("Title")

    buckets: list[tuple[str, object]] = []
    if isinstance(appsec, dict):
        for sev in ("high", "warning", "info", "secure", "hotspot"):
            if sev in appsec:
                buckets.append((sev, appsec[sev]))
    if not buckets:
        for sev in ("high", "warning", "info", "secure"):
            if sev in report:
                buckets.append((sev, report[sev]))

    for sev, bucket in buckets:
        if isinstance(bucket, dict):
            bucket = list(bucket.values())
        if not isinstance(bucket, list):
            continue
        for item in bucket[:15]:
            if isinstance(item, dict):
                title = item.get("title") or item.get("description") or str(item)
            else:
                title = str(item)
            table.add_row(sev, title[:80])
    console.print(table)


def scan_apk_menu(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    if not authorized_warning("mobsf", "MobSF"):
        return
    apk = _resolve_apk(config)
    if not apk:
        return
    key = _api_key(config)
    if not key:
        print_error("API key required.")
        return

    out_dir = report_dir("mobsf")

    boundary = "----PhoneSploitMobSF"
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="file"; filename="' + apk.name.encode() + b'"\r\n'
    body += b"Content-Type: application/octet-stream\r\n\r\n"
    body += apk.read_bytes()
    body += f"\r\n--{boundary}--\r\n".encode()

    status, raw = _request(
        config,
        "POST",
        "/api/v1/upload",
        data=body,
        headers=_auth_headers(key),
        content_type=f"multipart/form-data; boundary={boundary}",
        timeout=120,
    )
    if status != 200:
        print_error(f"Upload failed ({status}): {raw[:500]!r}")
        return
    try:
        upload = json.loads(raw.decode())
    except json.JSONDecodeError:
        print_error("Invalid upload response")
        return
    file_hash = upload.get("hash") or upload.get("scan_hash")
    if not file_hash:
        print_error("No hash in upload response")
        return
    print_success(f"Uploaded — hash {file_hash}")

    scan_fields: dict[str, str] = {"hash": file_hash}
    for field in ("scan_type", "file_name"):
        val = upload.get(field)
        if val is not None and str(val).strip():
            scan_fields[field] = str(val).strip()
    scan_body = _form_body(scan_fields)
    status, scan_raw = _request(
        config,
        "POST",
        "/api/v1/scan",
        data=scan_body,
        headers={
            **_auth_headers(key),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=600,
    )
    if status != 200:
        print_error(f"Scan failed ({status}): {scan_raw[:300]!r}")
        return

    _, report_raw = _request(
        config,
        "POST",
        "/api/v1/report_json",
        data=scan_body,
        headers={
            **_auth_headers(key),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=120,
    )
    try:
        report = json.loads(report_raw.decode())
    except json.JSONDecodeError:
        print_warning("Could not parse report_json")
        return

    report_path = out_dir / "report_json.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    _print_findings(report)

    sc_status, sc_raw = _request(
        config,
        "POST",
        "/api/v1/scorecard",
        data=scan_body,
        headers={
            **_auth_headers(key),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=60,
    )
    if sc_status == 200 and sc_raw:
        score_path = out_dir / "scorecard.json"
        score_path.write_text(sc_raw.decode(errors="replace"), encoding="utf-8")
        try:
            scorecard = json.loads(sc_raw.decode())
            console.print_json(data=scorecard)
        except json.JSONDecodeError:
            console.print(Panel(sc_raw.decode(errors="replace")[:2000], title="Scorecard"))

    if confirm("Download PDF report?"):
        pdf_status, pdf_raw = _request(
            config,
            "POST",
            "/api/v1/download_pdf",
            data=scan_body,
            headers={
                **_auth_headers(key),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=120,
        )
        if pdf_status == 200 and pdf_raw.startswith(b"%PDF"):
            pdf_path = out_dir / f"{file_hash}.pdf"
            pdf_path.write_bytes(pdf_raw)
            print_success(f"PDF saved: {pdf_path}")
        else:
            print_warning(f"PDF download failed ({pdf_status}).")

    if confirm("Open MobSF web UI?"):
        _open_mobsf_url(config.mobsf_url.rstrip("/") + "/")


def mf_open_ui(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    _open_mobsf_url(config.mobsf_url)


def _parse_scans_list(raw: bytes) -> list[dict]:
    try:
        data = json.loads(raw.decode())
    except json.JSONDecodeError:
        return []
    scans = data if isinstance(data, list) else data.get("scans") or data.get("content") or []
    if not isinstance(scans, list):
        return []
    return [s for s in scans if isinstance(s, dict)]


def _scan_hash_from_item(item: dict) -> str:
    return str(item.get("MD5") or item.get("md5") or item.get("hash") or "").strip()


def _fetch_recent_scans(config: AppConfig, api_key: str) -> list[dict]:
    status, raw = _request(
        config,
        "GET",
        "/api/v1/scans",
        headers=_auth_headers(api_key),
        timeout=60,
    )
    if status != 200:
        return []
    return _parse_scans_list(raw)


def pick_scan_hash(config: AppConfig, *, api_key: str | None = None) -> str | None:
    """Pick a scan hash from recent list or manual entry."""
    key = api_key or _api_key(config)
    if not key:
        print_error("API key required.")
        return None
    scans = _fetch_recent_scans(config, key)
    if scans:
        table = Table(title="Recent scans (pick # or enter hash)", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim")
        table.add_column("Hash")
        table.add_column("File")
        for idx, item in enumerate(scans[:30], start=1):
            h = _scan_hash_from_item(item)
            name = item.get("FILE_NAME") or item.get("file_name") or item.get("name") or ""
            table.add_row(str(idx), h[:32], str(name)[:40])
        console.print(table)
        pick = ask("Scan # (1-30), full MD5, or Enter to cancel: ").strip()
        if not pick:
            return None
        if pick.isdigit():
            idx = int(pick) - 1
            shown = min(len(scans), 30)
            if 0 <= idx < shown:
                h = _scan_hash_from_item(scans[idx])
                return h or None
            print_error(f"Invalid selection — choose 1-{shown}.")
            return None
        return pick
    file_hash = ask("Scan hash (MD5): ").strip()
    return file_hash or None


def _scan_hash_body(config: AppConfig) -> tuple[str, bytes] | None:
    key = _api_key(config)
    if not key:
        print_error("API key required.")
        return None
    file_hash = pick_scan_hash(config, api_key=key)
    if not file_hash:
        return None
    return key, _form_body({"hash": file_hash})


def _post_form(
    config: AppConfig,
    api_key: str,
    path: str,
    fields: dict[str, str],
    *,
    timeout: float = 120,
) -> tuple[int, bytes]:
    body = _form_body(fields)
    return _request(
        config,
        "POST",
        path,
        data=body,
        headers={**_auth_headers(api_key), "Content-Type": "application/x-www-form-urlencoded"},
        timeout=timeout,
    )


def mf_recent_scans(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    key = _api_key(config)
    if not key:
        print_error("API key required.")
        return
    status, raw = _request(
        config,
        "GET",
        "/api/v1/scans",
        headers=_auth_headers(key),
        timeout=60,
    )
    if status != 200:
        print_error(f"Could not list scans ({status}): {raw[:300]!r}")
        return
    scans = _parse_scans_list(raw)
    if not scans:
        print_warning("No scans returned.")
        try:
            console.print(Panel(raw.decode(errors="replace")[:4000], title="MobSF scans"))
        except UnicodeDecodeError:
            pass
        return
    table = Table(title="Recent MobSF scans", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim")
    table.add_column("Hash")
    table.add_column("File")
    table.add_column("Type")
    for idx, item in enumerate(scans[:30], start=1):
        h = _scan_hash_from_item(item)
        name = item.get("FILE_NAME") or item.get("file_name") or item.get("name") or ""
        typ = item.get("SCAN_TYPE") or item.get("scan_type") or ""
        table.add_row(str(idx), h[:32], str(name)[:40], str(typ))
    console.print(table)


def mf_search(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    key = _api_key(config)
    if not key:
        print_error("API key required.")
        return
    query = ask("Search query (MD5, package, or filename): ").strip()
    if not query:
        return
    status, raw = _post_form(config, key, "/api/v1/search", {"query": query})
    if status != 200:
        print_error(f"Search failed ({status}): {raw[:500]!r}")
        return
    try:
        data = json.loads(raw.decode())
        console.print_json(data=data)
    except json.JSONDecodeError:
        console.print(Panel(raw.decode(errors="replace")[:4000], title="MobSF search"))


def mf_tasks(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    key = _api_key(config)
    if not key:
        print_error("API key required.")
        return
    status, raw = _request(
        config,
        "POST",
        "/api/v1/tasks",
        data=b"",
        headers=_auth_headers(key),
        timeout=60,
    )
    if status != 200:
        print_error(f"Tasks request failed ({status}): {raw[:300]!r}")
        return
    try:
        data = json.loads(raw.decode())
        console.print_json(data=data)
    except json.JSONDecodeError:
        console.print(Panel(raw.decode(errors="replace")[:4000], title="MobSF tasks"))


def mf_scan_logs(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    key = _api_key(config)
    if not key:
        print_error("API key required.")
        return
    file_hash = pick_scan_hash(config, api_key=key)
    if not file_hash:
        return
    status, raw = _post_form(config, key, "/api/v1/scan_logs", {"hash": file_hash}, timeout=120)
    if status != 200:
        print_error(f"Scan logs failed ({status}): {raw[:300]!r}")
        return
    text = raw.decode(errors="replace")
    console.print(Panel(text[:8000] or "(empty)", title="MobSF scan logs", border_style="cyan"))


def mf_view_source(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    key = _api_key(config)
    if not key:
        print_error("API key required.")
        return
    file_hash = pick_scan_hash(config, api_key=key)
    if not file_hash:
        return
    file_path = ask("Source file path (as shown in MobSF report): ").strip()
    if not file_path:
        return
    typ = ask("Type (apk|java|smali|eclipse|studio) [java]: ").strip() or "java"
    status, raw = _post_form(
        config,
        key,
        "/api/v1/view_source",
        {"hash": file_hash, "file": file_path, "type": typ},
        timeout=120,
    )
    if status != 200:
        print_error(f"view_source failed ({status}): {raw[:300]!r}")
        return
    try:
        data = json.loads(raw.decode())
        content = data.get("content") or data.get("data") or json.dumps(data, indent=2)
        if isinstance(content, str):
            out = report_dir("mobsf") / "view_source.txt"
            out.write_text(content[:500_000], encoding="utf-8")
            print_success(f"Saved excerpt: {out}")
            console.print(Panel(content[:6000], title=file_path[:60], border_style="dim"))
        else:
            console.print_json(data=data)
    except json.JSONDecodeError:
        console.print(Panel(raw.decode(errors="replace")[:6000], title="Source"))


def mf_compare(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    key = _api_key(config)
    if not key:
        print_error("API key required.")
        return
    print_warning("Pick first scan hash:")
    hash1 = pick_scan_hash(config, api_key=key)
    if not hash1:
        return
    print_warning("Pick second scan hash:")
    hash2 = pick_scan_hash(config, api_key=key)
    if not hash2:
        return
    status, raw = _post_form(
        config,
        key,
        "/api/v1/compare",
        {"hash1": hash1, "hash2": hash2},
        timeout=180,
    )
    if status != 200:
        print_error(f"Compare failed ({status}): {raw[:300]!r}")
        return
    try:
        data = json.loads(raw.decode())
        out = report_dir("mobsf") / "compare.json"
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print_success(f"Compare saved: {out}")
        console.print_json(data=data)
    except json.JSONDecodeError:
        console.print(Panel(raw.decode(errors="replace")[:4000], title="Compare"))


def mf_rescan(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    key = _api_key(config)
    if not key:
        print_error("API key required.")
        return
    file_hash = pick_scan_hash(config, api_key=key)
    if not file_hash:
        return
    fields: dict[str, str] = {"hash": file_hash, "re_scan": "1"}
    status, raw = _post_form(config, key, "/api/v1/scan", fields, timeout=600)
    if status != 200:
        print_error(f"Re-scan failed ({status}): {raw[:300]!r}")
        return
    print_success("Re-scan completed.")
    try:
        console.print_json(data=json.loads(raw.decode()))
    except json.JSONDecodeError:
        console.print(Panel(raw.decode(errors="replace")[:2000], title="Re-scan"))


def mf_open_report(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    key = _api_key(config)
    file_hash = pick_scan_hash(config, api_key=key) if key else None
    if not file_hash:
        file_hash = ask("Scan hash (MD5): ").strip()
    if not file_hash:
        return
    url = config.mobsf_url.rstrip("/") + f"/static_analyzer/{file_hash}/"
    print_success(f"Opening {url}")
    _open_mobsf_url(url)


def mf_delete_scan(config: AppConfig) -> None:
    if not require_mobsf(config):
        return
    if not authorized_warning("mobsf", "MobSF"):
        return
    packed = _scan_hash_body(config)
    if not packed:
        return
    key, body = packed
    if not confirm("Delete this scan from MobSF?"):
        return
    status, raw = _request(
        config,
        "POST",
        "/api/v1/delete_scan",
        data=body,
        headers={**_auth_headers(key), "Content-Type": "application/x-www-form-urlencoded"},
        timeout=60,
    )
    if status == 200:
        print_success("Scan deleted.")
    else:
        print_error(f"Delete failed ({status}): {raw[:300]!r}")
