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
    ask,
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

    duration_raw = ask("[bold cyan]Duration (seconds)[/bold cyan]> ").strip()
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

    duration_raw = ask("[bold cyan]Duration (seconds)[/bold cyan]> ").strip()
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
    location = ask(f"[bold yellow]{label} path on computer[/bold yellow]> ").strip()

    if not location:
        print_null_input()
        return

    location = location.rstrip().strip("'\"")
    file_path = Path(location)

    if not file_path.is_file():
        print_error("This file does not exist.")
        return

    if not confirm(
        f"Copy [bold cyan]{file_path.name}[/bold cyan] to /sdcard/? "
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


def _select_camera_facing() -> str | None:
    submenu_row("Front camera", "Back camera")
    choice = ask("[prompt]> [/prompt]").strip()
    if choice in ("", "1"):
        return "front"
    if choice == "2":
        return "back"
    print_error("Invalid camera choice.")
    return None


def record_audio(config: AppConfig, mode: str) -> None:
    console.print(
        "[bold red]\\[Notice][/bold red] [bold cyan]Requires Android 11+[/bold cyan]"
    )
    with task_status("[info]Detecting Android version…[/info]"):
        android_ver = _check_android_version()

    if android_ver is None:
        print_error("No connected device found.\n[bold green] Going back to Main Menu[/bold green]")
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
    choice = ask("[prompt]> [/prompt]")

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
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return

    if mode == "device":
        open_file_prompt(config.opener, save_path)


def mirror(config: AppConfig) -> None:
    submenu_row("Default (best quality)", "Fast (low bitrate)", "Custom")
    mode = ask("[prompt]> [/prompt]")

    if mode == "1":
        subprocess.run(scrcpy_argv(config, []))
    elif mode == "2":
        subprocess.run(scrcpy_argv(config, ["-m", "1024", "-b", "1M"]))
    elif mode == "3":
        size_in = ask("[bold cyan]Size limit[/bold cyan] [dim](e.g. 1024)[/dim]> ").strip()
        bitrate_in = ask("[bold cyan]Bitrate (Mbps)[/bold cyan] [dim](e.g. 2)[/dim]> ").strip()
        fps_in = ask("[bold cyan]Max FPS[/bold cyan] [dim](e.g. 15)[/dim]> ").strip()

        extra: list[str] = []
        if size_in:
            extra += ["-m", size_in]
        if bitrate_in:
            extra += ["-b", f"{bitrate_in}M"]
        if fps_in:
            extra += [f"--max-fps={fps_in}"]
        subprocess.run(scrcpy_argv(config, extra))
    else:
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return


def camera_live(config: AppConfig) -> None:
    console.print("[bold red]\\[Notice][/bold red] [bold cyan]Requires Android 12+ and scrcpy camera support[/bold cyan]")
    with task_status("[info]Detecting Android version…[/info]"):
        android_ver = _check_android_version()

    if android_ver is None:
        print_error("No connected device found.\n[bold green] Going back to Main Menu[/bold green]")
        return

    if android_ver < 12:
        print_error("Android version too old. Camera Live requires Android 12+.")
        return

    facing = _select_camera_facing()
    if facing is None:
        return

    submenu_row("Normal", "Rotate 90", "Rotate 180", "Rotate 270")
    rotation_choice = ask("[prompt]> [/prompt]").strip()
    rotation_map = {
        "": "0",
        "1": "0",
        "2": "90",
        "3": "180",
        "4": "270",
    }
    orientation = rotation_map.get(rotation_choice)
    if orientation is None:
        print_error("Invalid rotation\n[bold green] Going back to Main Menu[/bold green]")
        return

    submenu_row("Default", "Fast (720p / 15 FPS)", "Custom")
    mode = ask("[prompt]> [/prompt]").strip()

    args = [
        "--video-source=camera",
        f"--camera-facing={facing}",
        f"--capture-orientation={orientation}",
        "--no-audio",
        "--no-control",
        f"--window-title=PhoneSploit Camera Live ({facing})",
    ]

    if mode in ("", "1"):
        pass
    elif mode == "2":
        args += ["--camera-size=1280x720", "--camera-fps=15", "-b", "4M"]
    elif mode == "3":
        size_in = ask("[bold cyan]Camera size[/bold cyan] [dim](e.g. 1280x720, Enter=default)[/dim]> ").strip()
        fps_in = ask("[bold cyan]Camera FPS[/bold cyan] [dim](e.g. 30, Enter=default)[/dim]> ").strip()
        bitrate_in = ask("[bold cyan]Bitrate (Mbps)[/bold cyan] [dim](e.g. 4, Enter=default)[/dim]> ").strip()

        if size_in:
            args.append(f"--camera-size={size_in}")
        if fps_in:
            args.append(f"--camera-fps={fps_in}")
        if bitrate_in:
            args += ["-b", f"{bitrate_in}M"]
    else:
        print_error("Invalid selection\n[bold green] Going back to Main Menu[/bold green]")
        return

    console.print("\n[dim]Opening Camera Live window. Close the scrcpy window or press Ctrl+C to stop.[/dim]\n")
    subprocess.run(scrcpy_argv(config, args))


def stream_audio(config: AppConfig, mode: str) -> None:
    console.print("[bold red]\\[Notice][/bold red] [bold cyan]Requires Android 11+[/bold cyan]")
    with task_status("[info]Detecting Android version…[/info]"):
        android_ver = _check_android_version()

    if android_ver is None:
        print_error("No connected device found.\n[bold green] Going back to Main Menu[/bold green]")
        return

    if android_ver < 11:
        print_error("Android version too old. Going back to Main Menu.")
        return

    console.print(f"[dim]Android {android_ver} · Ctrl+C to stop[/dim]")
    if mode == "mic":
        subprocess.run(scrcpy_argv(config, ["--no-video", "--audio-source=mic"]))
    else:
        subprocess.run(scrcpy_argv(config, ["--no-video"]))


def set_wallpaper(config: AppConfig) -> None:
    location = ask("[bold cyan]Image path on computer[/bold cyan]> ").strip().strip("'\"")
    if not location:
        print_null_input()
        return
    src = Path(location)
    if not src.is_file():
        print_error("This file does not exist.")
        return
    if not confirm("Push this image to the device and open the wallpaper picker?"):
        return
    remote = f"/sdcard/wallpaper-{datetime.now().strftime('%Y%m%d%H%M%S')}{src.suffix.lower()}"
    with task_status("[info]Pushing image…[/info]"):
        push = adb(["push", str(src), remote])
    if push.returncode != 0:
        print_error((push.stdout + push.stderr).strip() or "adb push failed.")
        return
    with task_status("[info]Opening wallpaper picker…[/info]"):
        adb(
            [
                "shell",
                "am",
                "start",
                "-a",
                "android.intent.action.ATTACH_DATA",
                "-d",
                f"file://{remote}",
                "-t",
                "image/*",
            ]
        )
    print_success("Wallpaper picker opened. Choose the app (e.g. Wallpapers) to apply it.")
