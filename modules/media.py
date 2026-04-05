import subprocess
from pathlib import Path
from datetime import datetime

from modules.config import AppConfig
from modules.tools import scrcpy_argv
from modules.console import (
    console,
    print_error,
    print_success,
    print_null_input,
    open_file_prompt,
    confirm,
    task_status,
    submenu_row,
    ensure_config_dir,
    adb,
    adb_output,
    get_adb_executable,
)


def _timestamp() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}"


def _parse_positive_duration_seconds(raw: str) -> int | None:
    s = raw.strip()
    if not s:
        print_error("Duration is required (positive integer seconds).")
        return None
    try:
        n = int(s, 10)
    except ValueError:
        print_error("Duration must be a positive integer (seconds).")
        return None
    if n < 1:
        print_error("Duration must be at least 1 second.")
        return None
    return n


def get_screenshot(config: AppConfig) -> None:
    file_name = f"screenshot-{_timestamp()}.png"
    remote = f"/sdcard/{file_name}"
    out_dir = ensure_config_dir(config, "screenshot_location")

    with task_status("[info]Capturing screenshot…[/info]"):
        adb(["shell", "screencap", "-p", remote])

    with task_status("[info]Pulling screenshot…[/info]"):
        result = adb(["pull", remote, str(out_dir)])

    local_path = str(out_dir / file_name)
    if result.returncode == 0:
        print_success(f"Saved to: {local_path}")
    else:
        print_error((result.stdout + result.stderr).strip())
        return

    open_file_prompt(config.opener, local_path)


def anonymous_screenshot(config: AppConfig) -> None:
    if not confirm(
        "Capture a screenshot, copy it to this computer, then "
        "[bold red]DELETE[/bold red] the file from the device storage?"
    ):
        return

    file_name = f"screenshot-{_timestamp()}.png"
    remote = f"/sdcard/{file_name}"
    out_dir = ensure_config_dir(config, "screenshot_location")

    with task_status("[info]Capturing screenshot…[/info]"):
        adb(["shell", "screencap", "-p", remote])

    with task_status("[info]Pulling screenshot…[/info]"):
        result = adb(["pull", remote, str(out_dir)])

    with task_status("[info]Removing file from device…[/info]"):
        adb(["shell", "rm", remote])

    local_path = str(out_dir / file_name)
    if result.returncode == 0:
        print_success(f"Saved to: {local_path}")
    else:
        print_error((result.stdout + result.stderr).strip())
        return

    open_file_prompt(config.opener, local_path)


def screenrecord(config: AppConfig) -> None:
    file_name = f"vid-{_timestamp()}.mp4"
    remote = f"/sdcard/{file_name}"

    duration_raw = console.input("[cyan]Duration (seconds)[/cyan]> ").strip()
    duration_sec = _parse_positive_duration_seconds(duration_raw)
    if duration_sec is None:
        return
    out_dir = ensure_config_dir(config, "screenrecord_location")

    adb_exe = get_adb_executable()
    if not adb_exe:
        print_error("ADB not available.")
        return

    with task_status(f"[info]Recording {duration_sec}s…[/info]"):
        rec = subprocess.run(
            [
                adb_exe,
                "shell",
                "screenrecord",
                "--time-limit",
                str(duration_sec),
                remote,
            ],
            capture_output=True,
            text=True,
        )
    if rec.returncode != 0:
        detail = (rec.stdout + rec.stderr).strip() or f"exit code {rec.returncode}"
        print_error(f"screenrecord failed: {detail}")
        return

    with task_status("[info]Pulling video…[/info]"):
        result = adb(["pull", remote, str(out_dir)])

    local_path = str(out_dir / file_name)
    if result.returncode == 0:
        print_success(f"Saved to: {local_path}")
    else:
        print_error((result.stdout + result.stderr).strip())
        return

    open_file_prompt(config.opener, local_path)


def anonymous_screenrecord(config: AppConfig) -> None:
    if not confirm(
        "Record the screen, copy the video to this computer, then "
        "[bold red]DELETE[/bold red] the file from the device storage?"
    ):
        return

    file_name = f"vid-{_timestamp()}.mp4"
    remote = f"/sdcard/{file_name}"

    duration_raw = console.input("[cyan]Duration (seconds)[/cyan]> ").strip()
    duration_sec = _parse_positive_duration_seconds(duration_raw)
    if duration_sec is None:
        return
    out_dir = ensure_config_dir(config, "screenrecord_location")

    adb_exe = get_adb_executable()
    if not adb_exe:
        print_error("ADB not available.")
        return

    with task_status(f"[info]Recording {duration_sec}s…[/info]"):
        rec = subprocess.run(
            [
                adb_exe,
                "shell",
                "screenrecord",
                "--time-limit",
                str(duration_sec),
                remote,
            ],
            capture_output=True,
            text=True,
        )
    if rec.returncode != 0:
        detail = (rec.stdout + rec.stderr).strip() or f"exit code {rec.returncode}"
        print_error(f"screenrecord failed: {detail}")
        return

    with task_status("[info]Pulling video…[/info]"):
        result = adb(["pull", remote, str(out_dir)])

    with task_status("[info]Removing file from device…[/info]"):
        adb(["shell", "rm", remote])

    local_path = str(out_dir / file_name)
    if result.returncode == 0:
        print_success(f"Saved to: {local_path}")
    else:
        print_error((result.stdout + result.stderr).strip())
        return

    open_file_prompt(config.opener, local_path)


def _push_and_open_media(config: AppConfig, label: str, intent_type: str) -> None:
    location = console.input(f"[yellow]{label} path on computer[/yellow]> ").strip()

    if not location:
        print_null_input()
        return

    location = location.rstrip().strip("'\"")
    file_path = Path(location)

    if not file_path.is_file():
        print_error("This file does not exist.")
        return

    if not confirm(
        f"Copy [cyan]{file_path.name}[/cyan] to /sdcard/? "
        "An existing file with the same name may be overwritten."
    ):
        return

    with task_status(f"[info]Pushing {file_path.name}…[/info]"):
        adb(["push", str(file_path), "/sdcard/"])

    fn = file_path.name
    with task_status(f"[info]Opening on device…[/info]"):
        adb(
            [
                "shell",
                "am",
                "start",
                "-a",
                "android.intent.action.VIEW",
                "-d",
                f"file:///sdcard/{fn}",
                "-t",
                intent_type,
            ]
        )
    print_success(f"Opened: {fn}")


def open_photo(config: AppConfig) -> None:
    _push_and_open_media(config, "Photo", "image/jpeg")


def open_audio(config: AppConfig) -> None:
    _push_and_open_media(config, "Audio", "audio/mp3")


def open_video(config: AppConfig) -> None:
    _push_and_open_media(config, "Video", "video/mp4")


def _check_android_version() -> int | None:
    raw = adb_output(["shell", "getprop", "ro.build.version.release"])
    try:
        return int(raw.split(".")[0])
    except (ValueError, IndexError):
        return None


def record_audio(config: AppConfig, mode: str) -> None:
    console.print(
        "[red]\\[Notice][/red] [cyan]Requires Android 11+[/cyan]"
    )
    with task_status("[info]Detecting Android version…[/info]"):
        android_ver = _check_android_version()

    if android_ver is None:
        print_error("No connected device found.\n[green] Going back to Main Menu[/green]")
        return

    if android_ver < 11:
        print_error("Android version too old. Going back to Main Menu.")
        return

    console.print(f"[dim]Android {android_ver}[/dim]")
    save_dir = ensure_config_dir(config, "pull_location")

    if mode == "mic":
        file_name = f"mic-audio-{_timestamp()}.opus"
        audio_flag = "--audio-source=mic"
        label = "Microphone Audio"
    else:
        file_name = f"device-audio-{_timestamp()}.opus"
        audio_flag = ""
        label = "Device Audio"

    submenu_row("Stream & record", "Record only (fast)")
    choice = console.input("[prompt]> [/prompt]")

    save_path = str(Path(save_dir) / file_name)

    if choice == "1":
        console.print("[dim]Ctrl+C to stop.[/dim]")
        cmd = scrcpy_argv(config, ["--no-video", f"--record={save_path}"])
        if audio_flag:
            cmd.append(audio_flag)
        subprocess.run(cmd)
    elif choice == "2":
        console.print("[dim]Ctrl+C to stop.[/dim]")
        cmd = scrcpy_argv(config, ["--no-video", "--no-playback", f"--record={save_path}"])
        if audio_flag:
            cmd.append(audio_flag)
        subprocess.run(cmd)
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return

    if mode == "device":
        open_file_prompt(config.opener, save_path)


def mirror(config: AppConfig) -> None:
    submenu_row("Default (best quality)", "Fast (low bitrate)", "Custom")
    mode = console.input("[prompt]> [/prompt]")

    if mode == "1":
        subprocess.run(scrcpy_argv(config, []))
    elif mode == "2":
        subprocess.run(scrcpy_argv(config, ["-m", "1024", "-b", "1M"]))
    elif mode == "3":
        size_in = console.input("[cyan]Size limit[/cyan] [dim](e.g. 1024)[/dim]> ").strip()
        bitrate_in = console.input("[cyan]Bitrate (Mbps)[/cyan] [dim](e.g. 2)[/dim]> ").strip()
        fps_in = console.input("[cyan]Max FPS[/cyan] [dim](e.g. 15)[/dim]> ").strip()

        extra: list[str] = []
        if size_in:
            extra += ["-m", size_in]
        if bitrate_in:
            extra += ["-b", f"{bitrate_in}M"]
        if fps_in:
            extra += [f"--max-fps={fps_in}"]
        subprocess.run(scrcpy_argv(config, extra))
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return


def stream_audio(config: AppConfig, mode: str) -> None:
    console.print("[red]\\[Notice][/red] [cyan]Requires Android 11+[/cyan]")
    with task_status("[info]Detecting Android version…[/info]"):
        android_ver = _check_android_version()

    if android_ver is None:
        print_error("No connected device found.\n[green] Going back to Main Menu[/green]")
        return

    if android_ver < 11:
        print_error("Android version too old. Going back to Main Menu.")
        return

    console.print(f"[dim]Android {android_ver} · Ctrl+C to stop[/dim]")
    if mode == "mic":
        subprocess.run(scrcpy_argv(config, ["--no-video", "--audio-source=mic"]))
    else:
        subprocess.run(scrcpy_argv(config, ["--no-video"]))
