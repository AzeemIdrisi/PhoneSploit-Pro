from modules.config import AppConfig
from modules.console import console, print_error, print_success, print_null_input, confirm, task_status, adb, ask


def send_sms(config: AppConfig) -> None:
    console.print(
        "[bold red]\\[Warning][/bold red] [bold cyan]BETA — tested on Android 12 only.[/bold cyan]"
    )
    number = ask(
        "[bold yellow]Phone + country code[/bold yellow] [dim](e.g. +91…)[/dim]> "
    ).strip()

    if not number:
        print_null_input()
        return

    message = ask("[bold yellow]Message[/bold yellow]> ").strip()

    if not confirm(
        f"Send SMS to [bold cyan]{number}[/bold cyan]? May incur charges."
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
    url = ask(
        "[bold yellow]URL[/bold yellow] [dim](e.g. https://github.com)[/dim]> "
    ).strip()

    if not url:
        print_null_input()
        return

    if not confirm(f"Open on device? [bold cyan]{url}[/bold cyan]"):
        return

    with task_status(f"[info]Opening URL…[/info]"):
        adb(["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url])
    print_success(f"Opened: {url}")
