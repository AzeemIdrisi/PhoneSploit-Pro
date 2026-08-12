"""Screen resolution, density (display size) and related settings (menu 63)."""

from __future__ import annotations

from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    task_status,
    submenu_row,
    adb,
    ask,
    confirm,
)

RESOLUTION_PRESETS = {
    "1": {"720p": ("720x1280", "1280x720")},
    "2": {"1080p": ("1080x1920", "1920x1080")},
    "3": {"2K/QHD": ("1440x2560", "2560x1440")},
    "4": {"4K UHD": ("2160x3840", "3840x2160")},
}

DENSITY_PRESETS = [
    ("160 (mdpi)", "160"),
    ("240 (hdpi)", "240"),
    ("320 (xhdpi)", "320"),
    ("420 (Pixel family)", "420"),
    ("480 (xxhdpi)", "480"),
    ("560 (xxxhdpi)", "560"),
]


def _wm(*args: str):
    """Run `adb shell wm <args>` and return the CompletedProcess."""
    return adb(["shell", "wm", *args])


def _run_wm_command(label: str, *args: str) -> None:
    with task_status(f"[info]{label}…[/info]"):
        r = _wm(*args)
    out = (r.stdout + r.stderr).strip()
    lowered = out.lower()
    if r.returncode == 0 and not any(
        token in lowered for token in ("unknown command", "exception", "error", "failed", "usage:", "invalid")
    ):
        print_success(out or "Done.")
    else:
        print_error(out or "command failed")


def _wm_read(*args: str) -> str | None:
    """Run a read-style `wm` query; return output, or None when unsupported."""
    r = _wm(*args)
    out = (r.stdout + r.stderr).strip()
    if not out or r.returncode != 0:
        return None
    lowered = out.lower()
    if "unknown command" in lowered or "exception" in lowered:
        return None
    return out


def show_current_settings(config: AppConfig) -> None:
    with task_status("[info]Reading display settings…[/info]"):
        rows = [
            ("Screen Size", _wm_read("size") or "No override set"),
            ("Density", _wm_read("density") or "No override set"),
        ]
    table = Table(title="Display Settings", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="yellow")
    table.add_column("Value", style="white")
    for prop, val in rows:
        table.add_row(prop, val)
    console.print(table)
    console.print("[dim]Note: display scaling can only be set, not read.[/dim]")


def set_resolution(config: AppConfig) -> None:
    submenu_row("720p", "1080p", "2K/QHD", "4K UHD", "Custom", "Reset")
    level = ask("[prompt]> [/prompt]").strip()
    if level == "5":
        size = ask("[cyan]Resolution[/cyan] [dim](WxH, e.g. 1080x1920)[/dim]> ").strip()
        if not size:
            return
    elif level == "6":
        _run_wm_command("Resetting resolution", "size", "reset")
        return
    elif level in RESOLUTION_PRESETS:
        preset = RESOLUTION_PRESETS[level]
        label, (portrait, landscape) = next(iter(preset.items()))
        submenu_row(f"{label} Portrait ({portrait})", f"{label} Landscape ({landscape})")
        orient = ask("[prompt]> [/prompt]").strip()
        if orient == "1":
            size = portrait
        elif orient == "2":
            size = landscape
        else:
            print_error("Invalid selection\n[green] Going back to Display Menu[/green]")
            return
    else:
        print_error("Invalid selection\n[green] Going back to Display Menu[/green]")
        return
    if not confirm(f"Set resolution to [cyan]{size}[/cyan]?"):
        return
    _run_wm_command(f"Setting resolution to {size}", "size", size)


def set_density(config: AppConfig) -> None:
    submenu_row(*(f"{d} DPI" for _, d in DENSITY_PRESETS), "Custom", "Reset")
    choice = ask("[prompt]> [/prompt]").strip()
    if choice == "7":
        density = ask("[cyan]Density[/cyan] [dim](DPI, e.g. 420)[/dim]> ").strip()
        if not density:
            return
        if not density.isdigit():
            print_error("Density must be a number\n[green] Going back to Display Menu[/green]")
            return
    elif choice == "8":
        _run_wm_command("Resetting density", "density", "reset")
        return
    elif choice.isdigit() and 1 <= int(choice) <= len(DENSITY_PRESETS):
        density = DENSITY_PRESETS[int(choice) - 1][1]
    else:
        print_error("Invalid selection\n[green] Going back to Display Menu[/green]")
        return
    if not confirm(f"Set density to [cyan]{density} DPI[/cyan]?"):
        return
    _run_wm_command(f"Setting density to {density} DPI", "density", density)


def toggle_scaling(config: AppConfig) -> None:
    submenu_row("Disable scaling", "Enable scaling (auto-fit)")
    choice = ask("[prompt]> [/prompt]").strip()
    if choice == "1":
        _run_wm_command("Disabling display scaling", "scaling", "0")
    elif choice == "2":
        _run_wm_command("Enabling display scaling", "scaling", "1")
    else:
        print_error("Invalid selection\n[green] Going back to Display Menu[/green]")


def reset_all(config: AppConfig) -> None:
    if not confirm("Reset resolution and density to device defaults?"):
        return
    _run_wm_command("Resetting resolution", "size", "reset")
    _run_wm_command("Resetting density", "density", "reset")


def display_menu(config: AppConfig) -> None:
    while True:
        console.print(
            "\n[bold cyan]Display Menu[/bold cyan]\n"
            "  [dim]1.[/dim] View Current Display Settings\n"
            "  [dim]2.[/dim] Set Resolution\n"
            "  [dim]3.[/dim] Set Display Size / Density\n"
            "  [dim]4.[/dim] Toggle Display Scaling\n"
            "  [dim]5.[/dim] Reset Resolution & Density\n"
            "  [dim]0.[/dim] Back to Main Menu\n"
        )
        choice = ask("[red]\\[Display Menu][/red] > ").strip().lower()
        if choice == "0":
            console.print("\n[white]Going back to Main Menu…[/white]\n")
            return
        elif choice == "1":
            show_current_settings(config)
        elif choice == "2":
            set_resolution(config)
        elif choice == "3":
            set_density(config)
        elif choice == "4":
            toggle_scaling(config)
        elif choice == "5":
            reset_all(config)
        else:
            print_error("Invalid selection\n[green] Going back to Display Menu[/green]")
