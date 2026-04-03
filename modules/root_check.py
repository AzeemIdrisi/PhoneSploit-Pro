"""Root / debuggable build heuristics (menu 63)."""

from rich.panel import Panel
from rich.table import Table

from modules.config import AppConfig
from modules.console import (
    console,
    task_status,
    adb,
    adb_output,
)


def _getprop(key: str) -> str:
    return adb_output(["shell", "getprop", key]).strip()


def _shell_line(cmd: str) -> str:
    return adb_output(["shell", "sh", "-c", cmd]).strip()


def root_heuristics(config: AppConfig) -> None:
    with task_status("[info]Gathering root / build signals…[/info]"):
        props = {
            "ro.build.type": _getprop("ro.build.type"),
            "ro.build.tags": _getprop("ro.build.tags"),
            "ro.debuggable": _getprop("ro.debuggable"),
            "ro.secure": _getprop("ro.secure"),
            "service.adb.root": _getprop("service.adb.root"),
            "ro.boot.flash.locked": _getprop("ro.boot.flash.locked"),
            "ro.boot.verifiedbootstate": _getprop("ro.boot.verifiedbootstate"),
        }

        shell_uid = _shell_line("id 2>/dev/null | head -1")
        which_su = _shell_line("which su 2>/dev/null")
        su_bin = _shell_line("ls -l /system/xbin/su /system/bin/su 2>/dev/null | head -2")
        magisk_bins = _shell_line(
            "ls /data/adb/magisk/magisk 2>/dev/null; "
            "ls /sbin/magisk 2>/dev/null; "
            "which magisk 2>/dev/null"
        )
        r_pkg = adb(["shell", "pm", "path", "com.topjohnwu.magisk"])
        magisk_pkg = (r_pkg.stdout + r_pkg.stderr).strip()

    table = Table(title="Root / build heuristics", show_header=True, header_style="bold cyan")
    table.add_column("Check", style="yellow", no_wrap=True)
    table.add_column("Result", style="white")

    for k, v in props.items():
        table.add_row(k, v or "[dim]empty[/dim]")

    table.add_row("shell id", shell_uid or "[dim]n/a[/dim]")
    table.add_row("which su", which_su or "[dim]not found[/dim]")
    table.add_row("su binaries (ls)", su_bin[:220] + ("…" if len(su_bin) > 220 else "") if su_bin else "[dim]n/a[/dim]")
    table.add_row("Magisk paths / magisk", magisk_bins[:220] + ("…" if len(magisk_bins) > 220 else "") if magisk_bins else "[dim]n/a[/dim]")
    table.add_row(
        "Magisk app (pm path)",
        (magisk_pkg[:120] + "…") if len(magisk_pkg) > 120 else (magisk_pkg or "[dim]not installed[/dim]"),
    )

    console.print(table)

    verdict, detail = _verdict(props, which_su, su_bin, magisk_bins, magisk_pkg)
    console.print(
        Panel(
            f"[bold]{verdict}[/bold]\n[dim]{detail}[/dim]",
            title="[bold]Assessment[/bold]",
            border_style="cyan",
        )
    )


def _verdict(
    props: dict[str, str],
    which_su: str,
    su_bin: str,
    magisk_bins: str,
    magisk_pkg: str,
) -> tuple[str, str]:
    score = 0
    reasons: list[str] = []

    tags = (props.get("ro.build.tags") or "").lower()
    if "test-keys" in tags:
        score += 2
        reasons.append("ro.build.tags contains test-keys (common on eng/userdebug)")

    btype = (props.get("ro.build.type") or "").lower()
    if btype in ("eng", "userdebug"):
        score += 1
        reasons.append(f"ro.build.type is {btype}")

    if props.get("ro.debuggable") == "1":
        score += 1
        reasons.append("ro.debuggable=1")

    if props.get("service.adb.root") == "1":
        score += 1
        reasons.append("service.adb.root=1 (adb root may work)")

    if which_su and "su" in which_su and "not found" not in which_su.lower():
        score += 2
        reasons.append("`which su` found a path")

    if su_bin and ("-rwx" in su_bin or "su" in su_bin):
        score += 1
        reasons.append("classic /system/*/su paths exist")

    if magisk_bins and ("magisk" in magisk_bins.lower() or "/data/adb" in magisk_bins):
        score += 3
        reasons.append("Magisk binary or /data/adb path detected")

    if magisk_pkg and "package:" in magisk_pkg:
        score += 2
        reasons.append("Magisk manager package present")

    if score >= 4:
        return (
            "Several root / mod indicators detected",
            "; ".join(reasons) if reasons else "Multiple signals fired.",
        )
    if score >= 2:
        return (
            "Some indicators present (inconclusive)",
            "; ".join(reasons) if reasons else "Mixed signals.",
        )
    return (
        "No strong root indicators (typical stock user build)",
        "su/Magisk not obvious; build looks like a normal user image.",
    )
