"""drozer console + agent menu integration."""

from __future__ import annotations

import subprocess
from pathlib import Path

from modules.config import AppConfig
from modules.console import ask, print_success, print_warning
from modules.ext_runner import (
    adb_install_apk,
    authorized_warning,
    drozer_start_embedded,
    github_release_asset,
    pick_package,
    preflight_serial,
    report_dir,
    run_captured,
    run_internal_menu,
)
from modules.tools import drozer_argv, drozer_console_argv, require_drozer


def _setup(config: AppConfig) -> None:
    if not preflight_serial():
        return
    apk_path = github_release_asset(
        "ReversecLabs", "drozer-agent", "drozer-agent", quiet=True
    )
    if not apk_path:
        apk_path = github_release_asset("WithSecureLabs", "drozer-agent", "drozer-agent")
    if not apk_path:
        return
    if not adb_install_apk(apk_path):
        return
    agent = drozer_start_embedded()
    if agent:
        print_success("drozer agent forward + embedded server started (port 31415).")
    else:
        print_warning("Complete agent pairing in the UI if needed, then retry assessment.")


def _drozer_run(config: AppConfig, command: str) -> None:
    if not require_drozer(config):
        return
    if not preflight_serial():
        return
    drozer_start_embedded()
    run_captured(drozer_console_argv(config, command))


def _list_packages(config: AppConfig) -> None:
    _drozer_run(config, "run app.package.list")


def _package_info(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run app.package.info -a {pkg}")


def _attack_surface(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run app.package.attacksurface {pkg}")


def _activities(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run app.activity.info -a {pkg}")


def _services(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run app.service.info -a {pkg}")


def _receivers(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run app.broadcast.info -a {pkg}")


def _providers(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run app.provider.info -a {pkg}")


def _find_uris(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run scanner.provider.finduris -a {pkg}")


def _injection(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run scanner.provider.injection -a {pkg}")


def _traversal(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run scanner.provider.traversal -a {pkg}")


def _permissions(config: AppConfig) -> None:
    _drozer_run(config, "run permissions")


def _provider_query(config: AppConfig) -> None:
    uri = ask("Content URI (run Find URIs first if needed): ").strip()
    if uri:
        _drozer_run(config, f"run app.provider.query {uri}")


def _broadcast_send(config: AppConfig) -> None:
    pkg = pick_package(config)
    if not pkg:
        return
    component = ask("Broadcast receiver component (PKG/Class): ").strip()
    action = ask("Intent action: ").strip()
    if component and action:
        _drozer_run(
            config,
            f"run app.broadcast.send --component {component} --action {action}",
        )


def _service_start(config: AppConfig) -> None:
    pkg = pick_package(config)
    if not pkg:
        return
    component = ask("Service component (PKG/Class): ").strip()
    if component:
        _drozer_run(config, f"run app.service.start --component {component}")


def _pick_drozer_host_item(config: AppConfig, argv_tail: list[str], title: str) -> str | None:
    if not require_drozer(config):
        return None
    result = run_captured(drozer_argv(config, argv_tail))
    names: list[str] = []
    for line in (result.stdout or "").splitlines():
        line = line.strip()
        if not line or line.lower().startswith("attempting"):
            continue
        token = line.split()[0]
        if "." in token and token not in names:
            names.append(token)
    if not names:
        return None
    from rich.table import Table
    from modules.console import console

    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("#", justify="right")
    table.add_column("Name")
    for i, name in enumerate(names[:50], 1):
        table.add_row(str(i), name)
    console.print(table)
    pick = ask(f"Select # (1-{min(len(names), 50)}), or type name: ").strip()
    if pick.isdigit():
        idx = int(pick) - 1
        if 0 <= idx < len(names[:50]):
            return names[idx]
    return pick if pick else None


def _start_exported_activity(config: AppConfig) -> None:
    pkg = pick_package(config)
    if not pkg:
        return
    if not require_drozer(config) or not preflight_serial():
        return
    drozer_start_embedded()
    result = run_captured(drozer_console_argv(config, f"run app.activity.info -a {pkg}"))
    lines = (result.stdout or "").splitlines()
    activities: list[tuple[str, str]] = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("Package:"):
            continue
        if "/" in line and pkg in line:
            parts = line.split()
            token = parts[0] if parts else line
            if "/" in token:
                activities.append((pkg, token.split("/", 1)[1]))
    if not activities:
        component = ask("Activity class (PKG/ActivityName or ActivityName): ").strip()
        if not component:
            return
        if "/" not in component:
            component = f"{pkg}/{component}"
        _drozer_run(config, f"run app.activity.start --component {component}")
        return
    from modules.console import print_option_list

    labels = [f"{cls}" for _, cls in activities[:30]]
    print_option_list(labels)
    pick = ask(f"Activity # (1-{len(labels)}): ").strip()
    if not pick.isdigit():
        return
    idx = int(pick) - 1
    if idx < 0 or idx >= len(activities):
        return
    p, cls = activities[idx]
    _drozer_run(config, f"run app.activity.start --component {p}/{cls}")


def _exploit_list(config: AppConfig) -> None:
    _pick_drozer_host_item(config, ["exploit", "list"], "drozer exploits")


def _payload_list(config: AppConfig) -> None:
    _pick_drozer_host_item(config, ["payload", "list"], "drozer payloads")


def _exploit_build(config: AppConfig) -> None:
    if not require_drozer(config):
        return
    exploit = _pick_drozer_host_item(config, ["exploit", "list"], "Pick exploit") or ask(
        "Exploit name: "
    ).strip()
    payload = _pick_drozer_host_item(config, ["payload", "list"], "Pick payload") or ask(
        "Payload name: "
    ).strip()
    if not exploit or not payload:
        return
    server = ask("Server LHOST:LPORT [127.0.0.1:31415]: ").strip() or "127.0.0.1:31415"
    run_captured(
        drozer_argv(
            config,
            ["exploit", "build", exploit, "--payload", payload, "--server", server],
        )
    )


def _server_start(config: AppConfig) -> None:
    if not require_drozer(config):
        return
    print_warning("Starting drozer server in foreground (Ctrl+C to stop).")
    run_captured(drozer_argv(config, ["server", "start"]), timeout=None)


def _agent_create(config: AppConfig) -> None:
    if not require_drozer(config):
        return
    from modules.ext_runner import adb_install_apk, report_dir

    label = ask("Agent name [PhoneSploitAgent]: ").strip() or "PhoneSploitAgent"
    out_apk = report_dir("drozer") / f"{label}.apk"
    result = run_captured(
        drozer_argv(config, ["agent", "create", label, "--file", str(out_apk)])
    )
    if result.returncode != 0 or not out_apk.is_file():
        run_captured(drozer_argv(config, ["agent", "create", "--help"]))
        manual = ask("Path to generated agent APK (if created): ").strip()
        if manual:
            out_apk = Path(manual)
        else:
            return
    if Path(out_apk).is_file() and preflight_serial():
        adb_install_apk(Path(out_apk))


def _raw_console(config: AppConfig) -> None:
    cmd = ask('drozer module command (e.g. run app.package.list): ').strip()
    if cmd:
        _drozer_run(config, cmd)


def _manifest(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run app.package.manifest {pkg}")


def _debuggable_apps(config: AppConfig) -> None:
    _drozer_run(config, "run scanner.misc.debuggable")


def _exported_components(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run scanner.misc.exportedcomponents -a {pkg}")


def _browsable(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run scanner.activity.browsable -a {pkg}")


def _native_scan(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run scanner.misc.native -a {pkg}")


def _provider_columns(config: AppConfig) -> None:
    uri = ask("Content URI: ").strip()
    if uri:
        _drozer_run(config, f"run app.provider.columns {uri}")


def _provider_read(config: AppConfig) -> None:
    uri = ask("Content URI (file provider): ").strip()
    if uri:
        _drozer_run(config, f"run app.provider.read {uri}")


def _provider_download(config: AppConfig) -> None:
    uri = ask("Content URI to download: ").strip()
    if not uri:
        return
    dest = report_dir("drozer") / "provider-download"
    dest.mkdir(parents=True, exist_ok=True)
    local = ask(f"Local filename under {dest} [download.bin]: ").strip() or "download.bin"
    _drozer_run(config, f"run app.provider.download {uri} {dest / local}")


def _sqltables(config: AppConfig) -> None:
    pkg = pick_package(config)
    if pkg:
        _drozer_run(config, f"run scanner.provider.sqltables -a {pkg}")


def _provider_insert(config: AppConfig) -> None:
    if not authorized_warning("drozer-write", "Provider INSERT"):
        return
    uri = ask("Content URI: ").strip()
    if uri:
        _drozer_run(config, f"run app.provider.insert {uri}")


def _provider_update(config: AppConfig) -> None:
    if not authorized_warning("drozer-write", "Provider UPDATE"):
        return
    uri = ask("Content URI: ").strip()
    if uri:
        _drozer_run(config, f"run app.provider.update {uri}")


def _provider_delete(config: AppConfig) -> None:
    if not authorized_warning("drozer-write", "Provider DELETE"):
        return
    uri = ask("Content URI: ").strip()
    if uri:
        _drozer_run(config, f"run app.provider.delete {uri}")


def _device_info(config: AppConfig) -> None:
    _drozer_run(config, "run information.deviceinfo")


def _file_upload(config: AppConfig) -> None:
    local = ask("Local file path: ").strip()
    remote = ask("Remote path on device: ").strip()
    if local and remote:
        _drozer_run(config, f"run tools.file.upload {local} {remote}")


def _file_download(config: AppConfig) -> None:
    remote = ask("Remote file path on device: ").strip()
    if not remote:
        return
    dest = report_dir("drozer") / Path(remote).name
    _drozer_run(config, f"run tools.file.download {remote} {dest}")


def _interactive_shell(config: AppConfig) -> None:
    if not require_drozer(config):
        return
    if not preflight_serial():
        return
    drozer_start_embedded()
    print_warning("Interactive drozer console (type exit to leave).")
    subprocess.run(
        drozer_argv(config, ["console", "connect", "--no-password", "--no-ssl"]),
    )


def dz_assess_menu(config: AppConfig) -> None:
    if not authorized_warning("drozer", "drozer"):
        return
    run_internal_menu(
        config,
        ["Main Menu", "Assess IPC with drozer", "Assessment"],
        [
            ("List packages", _list_packages),
            ("Package info", _package_info),
            ("Dump manifest", _manifest),
            ("Attack surface", _attack_surface),
            ("Debuggable apps (device)", _debuggable_apps),
            ("Exported components scan", _exported_components),
            ("Browsable / deep links", _browsable),
            ("Native libraries scan", _native_scan),
            ("Activities", _activities),
            ("Start exported activity", _start_exported_activity),
            ("Services", _services),
            ("Receivers", _receivers),
            ("Content providers", _providers),
            ("Find content URIs", _find_uris),
            ("Provider columns", _provider_columns),
            ("Provider read (file URI)", _provider_read),
            ("Provider download to host", _provider_download),
            ("Provider SQL tables scan", _sqltables),
            ("Provider SQL injection scan", _injection),
            ("Provider traversal scan", _traversal),
            ("Query content provider", _provider_query),
            ("Provider insert (authorized)", _provider_insert),
            ("Provider update (authorized)", _provider_update),
            ("Provider delete (authorized)", _provider_delete),
            ("Send broadcast", _broadcast_send),
            ("Start exported service", _service_start),
            ("Permissions dump", _permissions),
            ("Device info (agent)", _device_info),
            ("Upload file to device", _file_upload),
            ("Download file from device", _file_download),
            ("Interactive agent shell", _interactive_shell),
            ("Custom console command", _raw_console),
        ],
    )


def dz_deploy_menu(config: AppConfig) -> None:
    if not authorized_warning("drozer", "drozer"):
        return
    run_internal_menu(
        config,
        ["Main Menu", "Assess IPC with drozer", "Deploy / exploit"],
        [
            ("Create & install agent APK", _agent_create),
            ("List payloads", _payload_list),
            ("List exploits", _exploit_list),
            ("Build exploit APK", _exploit_build),
            ("Start drozer server", _server_start),
        ],
    )


def dz_setup(config: AppConfig) -> None:
    if not require_drozer(config):
        return
    if not authorized_warning("drozer", "drozer"):
        return
    _setup(config)
