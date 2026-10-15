"""Frida server setup and objection one-shots."""

from __future__ import annotations

import lzma
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

from modules.config import AppConfig
from modules.console import adb, ask, print_error, print_success, print_warning
from modules.ext_runner import (
    authorized_warning,
    device_cpu_abi,
    pick_package,
    preflight_serial,
    run_captured,
    run_internal_menu,
)
from modules.tools import frida_ps_argv, objection_argv, require_frida, require_objection


def _frida_version(config: AppConfig) -> str | None:
    if not require_frida(config):
        return None
    result = subprocess.run(
        [config.frida_path or "frida", "--version"],
        capture_output=True,
        text=True,
    )
    ver = (result.stdout or result.stderr or "").strip()
    m = re.search(r"(\d+\.\d+\.\d+)", ver)
    return m.group(1) if m else None


def _fetch_frida_server(version: str, abi: str) -> Path | None:
    name = f"frida-server-{version}-android-{abi}.xz"
    url = f"https://github.com/frida/frida/releases/download/{version}/{name}"
    dest_xz = Path.home() / ".phonesploit-pro" / "cache" / name
    dest_xz.parent.mkdir(parents=True, exist_ok=True)
    binary = dest_xz.with_suffix("")
    min_ok = 50_000
    if binary.is_file() and binary.stat().st_size >= min_ok:
        return binary
    if not dest_xz.is_file() or dest_xz.stat().st_size < 1024:
        print_warning(f"Downloading {name}…")
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                data = resp.read()
        except OSError as exc:
            print_error(f"Download failed: {exc}")
            return None
        if len(data) < 1024:
            print_error("Downloaded frida-server archive looks truncated.")
            return None
        dest_xz.write_bytes(data)
    try:
        with lzma.open(dest_xz) as src, open(binary, "wb") as dst:
            shutil.copyfileobj(src, dst)
    except (lzma.LZMAError, OSError) as exc:
        print_error(f"Could not decompress frida-server: {exc}")
        if dest_xz.is_file():
            dest_xz.unlink(missing_ok=True)
        return None
    if not binary.is_file() or binary.stat().st_size < min_ok:
        print_error("frida-server binary missing or too small after decompress.")
        return None
    binary.chmod(0o755)
    return binary


def _start_frida_server_detached(remote: str) -> bool:
    """Start frida-server without blocking the adb shell session."""
    start_cmd = f"nohup {remote} >/dev/null 2>&1 </dev/null &"
    root = adb(["root"])
    if root.returncode == 0:
        adb(["shell", start_cmd])
        return True
    su = adb(["shell", "su", "-c", start_cmd])
    if su.returncode == 0:
        return True
    return False


def _push_frida_server(config: AppConfig) -> None:
    if not preflight_serial():
        return
    ver = _frida_version(config)
    if not ver:
        return
    abi = device_cpu_abi()
    server = _fetch_frida_server(ver, abi)
    if not server:
        return
    remote = "/data/local/tmp/frida-server"
    adb(["push", str(server), remote])
    adb(["shell", "chmod", "755", remote])
    if _start_frida_server_detached(remote):
        print_success("frida-server start requested (detached).")
        return
    print_warning(
        "Could not start frida-server (no adb root/su). Use objection patchapk (gadget) instead."
    )


def _patchapk(config: AppConfig) -> None:
    if not require_objection(config):
        return
    apk = ask("Path to APK to patch: ").strip()
    if not apk:
        return
    run_captured([config.objection_path or "objection", "patchapk", "-s", apk], timeout=600)
    from glob import glob
    from pathlib import Path

    from modules.console import confirm
    from modules.ext_runner import adb_install_apk

    candidates = sorted(glob("*objection*.apk") + glob("*gadget*.apk"), key=lambda p: Path(p).stat().st_mtime)
    patched = candidates[-1] if candidates else ask("Path to patched APK: ").strip()
    if patched and Path(patched).is_file() and preflight_serial() and confirm("Install patched APK now?"):
        adb_install_apk(Path(patched))
        print_warning("Launch the app, then attach to Gadget in objection.")
    else:
        print_warning("Install the patched APK from cwd, then attach to Gadget.")


def _list_processes(config: AppConfig) -> None:
    if not require_frida(config) or not preflight_serial():
        return
    run_captured(frida_ps_argv(config))


def _frida_server_status(config: AppConfig) -> None:
    if not preflight_serial():
        return
    remote = "/data/local/tmp/frida-server"
    out = adb(["shell", "pgrep", "-f", "frida-server"])
    text = (out.stdout or out.stderr or "").strip()
    if out.returncode == 0 and text:
        print_success(f"frida-server appears running (PIDs: {text})")
        return
    su = adb(["shell", "su", "-c", "pgrep -f frida-server"])
    text = (su.stdout or su.stderr or "").strip()
    if su.returncode == 0 and text:
        print_success(f"frida-server appears running as root (PIDs: {text})")
        return
    print_warning(f"No frida-server process found (expected at {remote}).")


def _frida_server_stop(config: AppConfig) -> None:
    if not preflight_serial():
        return
    if not authorized_warning("frida-stop", "Stopping frida-server"):
        return
    for cmd in (
        ["shell", "pkill", "-f", "frida-server"],
        ["shell", "su", "-c", "pkill -f frida-server"],
    ):
        result = adb(cmd)
        if result.returncode == 0:
            print_success("frida-server stop requested.")
            return
    print_warning("Could not stop frida-server (may not be running).")


def _objection_streams(run_args: list[str]) -> bool:
    joined = " ".join(run_args).lower()
    for token in ("monitor", "watch", "implicit_intents"):
        if token in joined:
            return True
    return False


def _objection_run(config: AppConfig, run_args: list[str], *, spawn: bool = False) -> None:
    if not require_objection(config):
        return
    serial = preflight_serial()
    if not serial:
        return
    pkg = pick_package(config)
    if not pkg:
        return
    argv = objection_argv(config, pkg, serial, run_args, spawn=spawn)
    if _objection_streams(run_args):
        print_warning("Streaming command — press Ctrl+C in the terminal when done.")
        subprocess.run(argv)
    else:
        run_captured(argv, timeout=120)


def fr_setup_menu(config: AppConfig) -> None:
    if not authorized_warning("frida", "Frida / objection"):
        return
    run_internal_menu(
        config,
        ["Main Menu", "Instrument Apps with Frida", "Setup"],
        [
            ("Push & start frida-server", _push_frida_server),
            ("frida-server status", _frida_server_status),
            ("Stop frida-server", _frida_server_stop),
            ("objection patchapk (gadget)", _patchapk),
            ("List processes (frida-ps)", _list_processes),
        ],
    )


def fr_actions_menu(config: AppConfig) -> None:
    if not authorized_warning("frida", "Frida / objection"):
        return

    def _search_classes(c: AppConfig) -> None:
        query = ask("Query: ").strip()
        if query:
            _objection_run(c, ["android", "hooking", "search", "classes", query])

    def _search_methods(c: AppConfig) -> None:
        query = ask("Method query: ").strip()
        if query:
            _objection_run(c, ["android", "hooking", "search", "methods", query])

    def _fs_ls(c: AppConfig) -> None:
        path = ask("Remote path [.]: ").strip() or "."
        _objection_run(c, ["ls", path])

    def _fs_download(c: AppConfig) -> None:
        remote = ask("Remote file path: ").strip()
        local = ask("Local path: ").strip()
        if remote and local:
            _objection_run(c, ["file", "download", remote, local])

    def _fs_upload(c: AppConfig) -> None:
        local = ask("Local file path: ").strip()
        remote = ask("Remote destination: ").strip()
        if local and remote:
            _objection_run(c, ["file", "upload", local, remote])

    def _memory_dump(c: AppConfig) -> None:
        from modules.ext_runner import report_dir

        dest = report_dir("frida") / "memory"
        dest.mkdir(parents=True, exist_ok=True)
        _objection_run(c, ["memory", "dump", "all", str(dest)])

    def _ui_screenshot(c: AppConfig) -> None:
        from modules.ext_runner import report_dir

        path = str(report_dir("frida") / "screenshot.png")
        _objection_run(c, ["android", "ui", "screenshot", path])

    def _list_class_methods(c: AppConfig) -> None:
        cls = ask("Fully qualified class name: ").strip()
        if cls:
            _objection_run(c, ["android", "hooking", "list", "class_methods", cls])

    def _watch_class(c: AppConfig) -> None:
        cls = ask("Class to watch: ").strip()
        if cls:
            _objection_run(
                c,
                [
                    "android",
                    "hooking",
                    "watch",
                    "class",
                    cls,
                    "--dump-args",
                    "--dump-return",
                ],
            )

    def _watch_method(c: AppConfig) -> None:
        method = ask("Class.method (fully qualified): ").strip()
        if method:
            _objection_run(
                c,
                [
                    "android",
                    "hooking",
                    "watch",
                    "class_method",
                    method,
                    "--dump-args",
                    "--dump-return",
                    "--dump-backtrace",
                ],
            )

    def _set_return_value(c: AppConfig) -> None:
        method = ask("Class.method: ").strip()
        val = ask("Return value (true/false): ").strip().lower()
        if not method or not val:
            return
        if val not in ("true", "false"):
            print_error("Return value must be true or false.")
            return
        _objection_run(c, ["android", "hooking", "set", "return_value", method, val])

    def _proxy_set(c: AppConfig) -> None:
        host = ask("Proxy host: ").strip()
        port = ask("Proxy port: ").strip()
        if host and port:
            _objection_run(c, ["android", "proxy", "set", host, port])

    def _launch_activity(c: AppConfig) -> None:
        if not authorized_warning("frida-intent", "Launching exported activity"):
            return
        activity = ask("Activity class (fully qualified): ").strip()
        if activity:
            _objection_run(c, ["android", "intent", "launch_activity", activity])

    def _launch_service(c: AppConfig) -> None:
        if not authorized_warning("frida-intent", "Starting exported service"):
            return
        service = ask("Service class (fully qualified): ").strip()
        if service:
            _objection_run(c, ["android", "intent", "launch_service", service])

    def _heap_search(c: AppConfig) -> None:
        cls = ask("Class to search on heap: ").strip()
        if cls:
            _objection_run(c, ["android", "heap", "search", "instances", cls])

    def _heap_print_fields(c: AppConfig) -> None:
        handle = ask("Object handle (from heap search): ").strip()
        if handle:
            _objection_run(c, ["android", "heap", "print", "fields", handle])

    def _heap_print_methods(c: AppConfig) -> None:
        handle = ask("Object handle: ").strip()
        if handle:
            _objection_run(c, ["android", "heap", "print", "methods", handle, "--without-arguments"])

    def _heap_execute(c: AppConfig) -> None:
        handle = ask("Object handle: ").strip()
        method = ask("Method name: ").strip()
        if handle and method:
            _objection_run(c, ["android", "heap", "execute", handle, method, "--return-string"])

    def _jobs_kill(c: AppConfig) -> None:
        ident = ask("Job identifier to kill: ").strip()
        if ident:
            _objection_run(c, ["jobs", "kill", ident])

    run_internal_menu(
        config,
        ["Main Menu", "Instrument Apps with Frida", "Runtime actions"],
        [
            ("Show app paths (env)", lambda c: _objection_run(c, ["env"])),
            ("ART deoptimize", lambda c: _objection_run(c, ["android", "deoptimize"])),
            ("Disable SSL pinning", lambda c: _objection_run(c, ["android", "sslpinning", "disable"])),
            ("Monitor SSL pinning", lambda c: _objection_run(c, ["android", "sslpinning", "monitor"])),
            ("Disable root detection", lambda c: _objection_run(c, ["android", "root", "disable"])),
            ("Simulate rooted device", lambda c: _objection_run(c, ["android", "root", "simulate"])),
            (
                "SSL pinning at spawn",
                lambda c: _objection_run(c, ["android", "sslpinning", "disable"], spawn=True),
            ),
            ("Set app HTTP proxy", _proxy_set),
            ("Disable FLAG_SECURE (screenshots)", lambda c: _objection_run(c, ["android", "ui", "FLAG_SECURE", "false"])),
            ("Keystore list", lambda c: _objection_run(c, ["android", "keystore", "list"])),
            ("Keystore detail", lambda c: _objection_run(c, ["android", "keystore", "detail"])),
            ("Clipboard monitor", lambda c: _objection_run(c, ["android", "clipboard", "monitor"])),
            ("List activities", lambda c: _objection_run(c, ["android", "hooking", "list", "activities"])),
            ("List services", lambda c: _objection_run(c, ["android", "hooking", "list", "services"])),
            ("List receivers", lambda c: _objection_run(c, ["android", "hooking", "list", "receivers"])),
            ("List classes", lambda c: _objection_run(c, ["android", "hooking", "list", "classes"])),
            ("List class methods", _list_class_methods),
            ("Search classes", _search_classes),
            ("Search methods", _search_methods),
            ("Watch class (dump args/return)", _watch_class),
            ("Watch method (dump args/backtrace)", _watch_method),
            ("Set method return value", _set_return_value),
            ("Launch activity", _launch_activity),
            ("Launch service", _launch_service),
            (
                "Monitor implicit intents",
                lambda c: _objection_run(c, ["android", "intent", "implicit_intents", "--dump-backtrace"]),
            ),
            ("Heap search instances", _heap_search),
            ("Heap print fields", _heap_print_fields),
            ("Heap print methods", _heap_print_methods),
            ("Heap execute method", _heap_execute),
            ("List background jobs", lambda c: _objection_run(c, ["jobs", "list"])),
            ("Kill background job", _jobs_kill),
            ("Filesystem ls", _fs_ls),
            ("File download", _fs_download),
            ("File upload", _fs_upload),
            ("Memory dump all", _memory_dump),
            ("UI screenshot", _ui_screenshot),
            ("Interactive REPL (objection start)", _repl),
        ],
    )


def _repl(config: AppConfig) -> None:
    if not require_objection(config):
        return
    serial = preflight_serial()
    if not serial:
        return
    pkg = pick_package(config)
    if not pkg:
        return
    subprocess.run([config.objection_path or "objection", "-n", pkg, "-S", serial, "start"])
