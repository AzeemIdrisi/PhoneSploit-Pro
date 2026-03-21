from modules.config import AppConfig
from modules.console import console, print_error, print_success, print_null_input, confirm, task_status, adb


def send_sms(config: AppConfig) -> None:
    console.print(
        "[red]\\[Warning][/red] [cyan]BETA — tested on Android 12 only.[/cyan]"
    )
    number = console.input(
        "[yellow]Phone + country code[/yellow] [dim](e.g. +91…)[/dim]> "
    ).strip()

    if not number:
        print_null_input()
        return

    message = console.input("[yellow]Message[/yellow]> ").strip()

    if not confirm(
        f"Send SMS to [cyan]{number}[/cyan]? May incur charges."
    ):
        return

    with task_status(f"[info]Sending SMS…[/info]"):
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


def open_link(config: AppConfig) -> None:
    url = console.input(
        "[yellow]URL[/yellow] [dim](e.g. https://github.com)[/dim]> "
    ).strip()

    if not url:
        print_null_input()
        return

    if not confirm(f"Open on device? [cyan]{url}[/cyan]"):
        return

    with task_status(f"[info]Opening URL…[/info]"):
        adb(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url])
    print_success(f"Opened: {url}")
