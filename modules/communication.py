from modules.config import AppConfig
from modules.console import console, print_error, print_success, print_null_input, confirm, adb


def send_sms(config: AppConfig) -> None:
    console.print(
        "\n[red]\\[Warning][/red] [cyan]This feature is currently in BETA, Tested on Android 12 only.[/cyan]"
    )
    number = console.input(
        "[yellow]Enter Phone number with country code[/yellow] (e.g. +91XXXXXXXXXX) > "
    )

    if not number:
        print_null_input()
        return

    message = console.input("[yellow]Enter your message[/yellow] > ")

    if not confirm(
        f"Send this SMS to [cyan]{number}[/cyan]? This may incur charges on the device account."
    ):
        return

    console.print(f"[cyan]Sending SMS to {number}...[/cyan]")

    with console.status(f"[info]Sending SMS to {number}...[/info]"):
        adb([
            "shell", "service", "call", "isms", "5",
            "i32", "0",
            "s16", "com.android.mms.service",
            "s16", "null",
            "s16", number,
            "s16", "null",
            "s16", message,
            "s16", "null",
            "s16", "null",
            "s16", "null",
            "s16", "null",
        ])

    print_success(f"SMS sent to {number}.")
    console.print()


def open_link(config: AppConfig) -> None:
    console.print(
        "\n[yellow]Enter URL              [cyan]Example : https://github.com[/cyan][/yellow]"
    )
    url = console.input("[prompt]> [/prompt]")

    if not url:
        print_null_input()
        return

    if not confirm(f'Open this URL on the device browser?\n[cyan]{url}[/cyan]'):
        return

    console.print(f'\n[yellow]Opening "[white]{url}[/white]" on device...[/yellow]\n')
    with console.status(f"[info]Opening {url}...[/info]"):
        adb(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url])
    print_success(f"Opened: {url}")
    console.print()
