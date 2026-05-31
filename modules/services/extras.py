"""Diagnostics and extras services."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from modules.services.adb import ADBService, OperationResult
from modules.services.context import ServiceContext


def save_logcat_snippet(ctx: ServiceContext, lines: int = 500) -> OperationResult:
    out_dir = ctx.ensure_output_dir()
    name = f"logcat-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
    path = out_dir / name
    r = ctx.adb.run(["logcat", "-d", "-t", str(lines)])
    text = r.stdout + r.stderr
    try:
        path.write_text(text, encoding="utf-8", errors="replace")
    except OSError as e:
        return OperationResult(False, str(e))
    return OperationResult(True, f"Saved: {path}", data=str(path))


def grant_revoke_permission(
    adb: ADBService,
    package: str,
    permission: str,
    grant: bool = True,
) -> OperationResult:
    verb = "grant" if grant else "revoke"
    r = adb.run(["shell", "pm", verb, package, permission])
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        return OperationResult(True, out or "Done")
    return OperationResult(False, out or "failed")


def network_snapshot(adb: ADBService) -> OperationResult:
    ip_addr = adb.output(["shell", "ip", "addr"])
    if "not found" in ip_addr.lower() or not ip_addr.strip():
        ip_addr = adb.output(["shell", "ifconfig"])
    route = adb.output(["shell", "ip", "route"])
    dns = adb.output(["shell", "getprop", "net.dns1"])
    return OperationResult(
        True,
        "Network snapshot",
        data={"interfaces": ip_addr, "routes": route, "dns": dns},
    )


def read_developer_settings(adb: ADBService) -> OperationResult:
    keys = [
        "animator_duration_scale",
        "transition_animation_scale",
        "window_animation_scale",
        "adb_enabled",
    ]
    rows = {k: adb.output(["shell", "settings", "get", "global", k]) for k in keys}
    return OperationResult(True, "Developer settings", data=rows)


def write_developer_setting(adb: ADBService, key: str, value: str) -> OperationResult:
    r = adb.run(["shell", "settings", "put", "global", key, value])
    if r.returncode == 0:
        return OperationResult(True, "Updated")
    return OperationResult(False, (r.stdout + r.stderr).strip())


def read_locale(adb: ADBService) -> OperationResult:
    rows = {
        "settings system system_locales": adb.output(
            ["shell", "settings", "get", "system", "system_locales"]
        ),
        "persist.sys.locale": adb.output(["shell", "getprop", "persist.sys.locale"]),
        "ro.product.locale": adb.output(["shell", "getprop", "ro.product.locale"]),
    }
    return OperationResult(True, "Locale", data=rows)


def screen_stay_on(adb: ADBService, target: str) -> OperationResult:
    if target not in ("usb", "true", "false"):
        return OperationResult(False, "Invalid target (usb, true, false)")
    r = adb.run(["shell", "svc", "power", "stayon", target])
    if r.returncode == 0:
        return OperationResult(True, f"Stay-on set to {target}")
    return OperationResult(False, (r.stdout + r.stderr).strip())
