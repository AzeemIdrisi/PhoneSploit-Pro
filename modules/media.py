import subprocess
from pathlib import Path
from datetime import datetime

from modules.config import AppConfig
from modules.console import (
    console,
    print_error,
    print_success,
    print_null_input,
    open_file_prompt,
    confirm,
    adb,
    adb_output,
)


def _timestamp() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}"


def _ensure_location(config: AppConfig, label: str) -> str:
    """Prompt for save location if not set, returns the resolved path."""
    if not config.pull_location:
        console.print(f"\n[yellow]Enter location to save {label}, Press 'Enter' for default[/yellow]")
        config.pull_location = console.input("[prompt]> [/prompt]")
    if not config.pull_location:
        config.pull_location = "Downloaded-Files"
        console.print(f"\n[purple]Saving {label} to PhoneSploit-Pro/{config.pull_location}[/purple]\n")
    else:
        console.print(f"\n[purple]Saving {label} to {config.pull_location}[/purple]\n")
    Path(config.pull_location).mkdir(parents=True, exist_ok=True)
    return config.pull_location


def get_screenshot(config: AppConfig) -> None:
    file_name = f"screenshot-{_timestamp()}.png"
    remote = f"/sdcard/{file_name}"

    with console.status("[info]Capturing screenshot...[/info]"):
        adb(["shell", "screencap", "-p", remote])

    if not config.screenshot_location:
        console.print("\n[yellow]Enter location to save all screenshots, Press 'Enter' for default[/yellow]")
        config.screenshot_location = console.input("[prompt]> [/prompt]")
    if not config.screenshot_location:
        config.screenshot_location = "Downloaded-Files"
        console.print(f"\n[purple]Saving screenshot to PhoneSploit-Pro/{config.screenshot_location}[/purple]\n")
    else:
        console.print(f"\n[purple]Saving screenshot to {config.screenshot_location}[/purple]\n")
    Path(config.screenshot_location).mkdir(parents=True, exist_ok=True)

    with console.status("[info]Pulling screenshot...[/info]"):
        result = adb(["pull", remote, config.screenshot_location])

    local_path = str(Path(config.screenshot_location) / file_name)
    if result.returncode == 0:
        print_success(f"Saved to: {local_path}")
    else:
        print_error((result.stdout + result.stderr).strip())
        return

    open_file_prompt(config.opener, local_path)
    console.print()


def anonymous_screenshot(config: AppConfig) -> None:
    if not confirm(
        "Capture a screenshot, copy it to this computer, then "
        "[bold red]DELETE[/bold red] the file from the device storage?"
    ):
        return

    file_name = f"screenshot-{_timestamp()}.png"
    remote = f"/sdcard/{file_name}"

    with console.status("[info]Capturing screenshot...[/info]"):
        adb(["shell", "screencap", "-p", remote])

    if not config.screenshot_location:
        console.print("\n[yellow]Enter location to save all screenshots, Press 'Enter' for default[/yellow]")
        config.screenshot_location = console.input("[prompt]> [/prompt]")
    if not config.screenshot_location:
        config.screenshot_location = "Downloaded-Files"
        console.print(f"\n[purple]Saving screenshot to PhoneSploit-Pro/{config.screenshot_location}[/purple]\n")
    else:
        console.print(f"\n[purple]Saving screenshot to {config.screenshot_location}[/purple]\n")
    Path(config.screenshot_location).mkdir(parents=True, exist_ok=True)

    with console.status("[info]Pulling screenshot...[/info]"):
        result = adb(["pull", remote, config.screenshot_location])

    console.print("[yellow]Deleting screenshot from target device...[/yellow]")
    with console.status("[info]Removing remote file...[/info]"):
        adb(["shell", "rm", remote])

    local_path = str(Path(config.screenshot_location) / file_name)
    if result.returncode == 0:
        print_success(f"Saved to: {local_path}")
    else:
        print_error((result.stdout + result.stderr).strip())
        return

    open_file_prompt(config.opener, local_path)
    console.print()


def screenrecord(config: AppConfig) -> None:
    file_name = f"vid-{_timestamp()}.mp4"
    remote = f"/sdcard/{file_name}"

    duration = console.input(f"\n[cyan]Enter the recording duration (in seconds) > [/cyan]")
    console.print(f"\n[yellow]Starting Screen Recording...[/yellow]\n")

    subprocess.run(
        ["adb", "shell", "screenrecord", "--verbose", "--time-limit", duration, remote]
    )

    if not config.screenrecord_location:
        console.print("\n[yellow]Enter location to save all videos, Press 'Enter' for default[/yellow]")
        config.screenrecord_location = console.input("[prompt]> [/prompt]")
    if not config.screenrecord_location:
        config.screenrecord_location = "Downloaded-Files"
        console.print(f"\n[purple]Saving video to PhoneSploit-Pro/{config.screenrecord_location}[/purple]\n")
    else:
        console.print(f"\n[purple]Saving video to {config.screenrecord_location}[/purple]\n")
    Path(config.screenrecord_location).mkdir(parents=True, exist_ok=True)

    with console.status("[info]Pulling video...[/info]"):
        result = adb(["pull", remote, config.screenrecord_location])

    local_path = str(Path(config.screenrecord_location) / file_name)
    if result.returncode == 0:
        print_success(f"Saved to: {local_path}")
    else:
        print_error((result.stdout + result.stderr).strip())
        return

    open_file_prompt(config.opener, local_path)
    console.print()


def anonymous_screenrecord(config: AppConfig) -> None:
    if not confirm(
        "Record the screen, copy the video to this computer, then "
        "[bold red]DELETE[/bold red] the file from the device storage?"
    ):
        return

    file_name = f"vid-{_timestamp()}.mp4"
    remote = f"/sdcard/{file_name}"

    duration = console.input(f"\n[cyan]Enter the recording duration (in seconds) > [/cyan]")
    console.print(f"\n[yellow]Starting Screen Recording...[/yellow]\n")

    subprocess.run(
        ["adb", "shell", "screenrecord", "--verbose", "--time-limit", duration, remote]
    )

    if not config.screenrecord_location:
        console.print("\n[yellow]Enter location to save all videos, Press 'Enter' for default[/yellow]")
        config.screenrecord_location = console.input("[prompt]> [/prompt]")
    if not config.screenrecord_location:
        config.screenrecord_location = "Downloaded-Files"
        console.print(f"\n[purple]Saving video to PhoneSploit-Pro/{config.screenrecord_location}[/purple]\n")
    else:
        console.print(f"\n[purple]Saving video to {config.screenrecord_location}[/purple]\n")
    Path(config.screenrecord_location).mkdir(parents=True, exist_ok=True)

    with console.status("[info]Pulling video...[/info]"):
        result = adb(["pull", remote, config.screenrecord_location])

    console.print("[yellow]Deleting video from target device...[/yellow]")
    with console.status("[info]Removing remote file...[/info]"):
        adb(["shell", "rm", remote])

    local_path = str(Path(config.screenrecord_location) / file_name)
    if result.returncode == 0:
        print_success(f"Saved to: {local_path}")
    else:
        print_error((result.stdout + result.stderr).strip())
        return

    open_file_prompt(config.opener, local_path)
    console.print()


def _push_and_open_media(config: AppConfig, label: str, mime: str) -> str | None:
    """Push a local media file to /sdcard/ and return the remote filename."""
    location = console.input(f"\n[yellow]Enter {label} location in computer[/yellow] > ").strip()

    if not location:
        print_null_input()
        return None

    location = location.rstrip().strip("'\"")
    file_path = Path(location)

    if not file_path.is_file():
        print_error("This file does not exist.")
        return None

    if not confirm(
        f"Copy [cyan]{file_path.name}[/cyan] to the device at /sdcard/? "
        "An existing file with the same name may be overwritten."
    ):
        return None

    with console.status(f"[info]Pushing {file_path.name} to device...[/info]"):
        adb(["push", str(file_path), "/sdcard/"])

    return file_path.name


def open_photo(config: AppConfig) -> None:
    file_name = _push_and_open_media(config, "Photo", "image/jpeg")
    if not file_name:
        return
    console.print(f"\n[yellow]Opening photo on device...[/yellow]\n")
    adb([
        "shell", "am", "start", "-a", "android.intent.action.VIEW",
        "-d", f"file:///sdcard/{file_name}", "-t", "image/jpeg",
    ])
    console.print()


def open_audio(config: AppConfig) -> None:
    file_name = _push_and_open_media(config, "Audio", "audio/mp3")
    if not file_name:
        return
    console.print(f"\n[yellow]Playing audio on device...[/yellow]\n")
    adb([
        "shell", "am", "start", "-a", "android.intent.action.VIEW",
        "-d", f"file:///sdcard/{file_name}", "-t", "audio/mp3",
    ])
    console.print()


def open_video(config: AppConfig) -> None:
    file_name = _push_and_open_media(config, "Video", "video/mp4")
    if not file_name:
        return
    console.print(f"\n[yellow]Playing video on device...[/yellow]\n")
    adb([
        "shell", "am", "start", "-a", "android.intent.action.VIEW",
        "-d", f"file:///sdcard/{file_name}", "-t", "video/mp4",
    ])
    console.print()


def _check_android_version() -> int | None:
    """Return Android major version integer, or None if undetectable."""
    raw = adb_output(["shell", "getprop", "ro.build.version.release"])
    try:
        return int(raw.split(".")[0])
    except (ValueError, IndexError):
        return None


def record_audio(config: AppConfig, mode: str) -> None:
    console.print(
        "\n[red]\\[Notice][/red] [cyan]This feature requires Android 11 or higher.[/cyan]"
    )
    with console.status("[info]Detecting Android version...[/info]"):
        android_ver = _check_android_version()

    if android_ver is None:
        print_error("No connected device found.\n[green] Going back to Main Menu[/green]")
        return

    console.print(f"\n[green]Detected Android Version: {android_ver}[/green]")

    if android_ver < 11:
        print_error("Android version too old. Going back to Main Menu.")
        return

    save_dir = _ensure_location(config, "Recordings")

    if mode == "mic":
        file_name = f"mic-audio-{_timestamp()}.opus"
        audio_flag = "--audio-source=mic"
        label = "Microphone Audio"
    else:
        file_name = f"device-audio-{_timestamp()}.opus"
        audio_flag = ""
        label = "Device Audio"

    console.print(
        f"\n    [white]1. [green]Stream & Record\n"
        f"    [white]2. [green]Record Only     [yellow](Fast)[/yellow][/green]\n"
    )
    choice = console.input("[prompt]> [/prompt]")

    save_path = str(Path(save_dir) / file_name)

    if choice == "1":
        console.print(f"\n[green]Recording {label}\n\n[red]Press Ctrl+C to Stop.[/red][/green]\n")
        cmd = ["scrcpy", "--no-video", f"--record={save_path}"]
        if audio_flag:
            cmd.append(audio_flag)
        subprocess.run(cmd)
    elif choice == "2":
        console.print(f"\n[green]Recording {label}\n\n[red]Press Ctrl+C to Stop.[/red][/green]\n")
        cmd = ["scrcpy", "--no-video", "--no-playback", f"--record={save_path}"]
        if audio_flag:
            cmd.append(audio_flag)
        subprocess.run(cmd)
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return

    if mode == "device":
        open_file_prompt(config.opener, save_path)
    console.print()


def mirror(config: AppConfig) -> None:
    console.print(
        "\n    [white]1. [green]Default Mode   [yellow](Best quality)[/yellow]\n"
        "    [white]2. [green]Fast Mode      [yellow](Low quality but high performance)[/yellow]\n"
        "    [white]3. [green]Custom Mode    [yellow](Tweak settings to increase performance)[/yellow][/green]\n"
    )
    mode = console.input("[prompt]> [/prompt]")

    if mode == "1":
        subprocess.run(["scrcpy"])
    elif mode == "2":
        subprocess.run(["scrcpy", "-m", "1024", "-b", "1M"])
    elif mode == "3":
        size_in = console.input(f"\n[cyan]Enter size limit [yellow](e.g. 1024)[/yellow][/cyan] > ")
        bitrate_in = console.input(f"\n[cyan]Enter bit-rate [yellow](e.g. 2)[/yellow]   (Default : 8 Mbps)[/cyan] > ")
        fps_in = console.input(f"\n[cyan]Enter frame-rate [yellow](e.g. 15)[/yellow][/cyan] > ")

        cmd = ["scrcpy"]
        if size_in:
            cmd += ["-m", size_in]
        if bitrate_in:
            cmd += ["-b", f"{bitrate_in}M"]
        if fps_in:
            cmd += [f"--max-fps={fps_in}"]
        subprocess.run(cmd)
    else:
        print_error("Invalid selection\n[green] Going back to Main Menu[/green]")
        return
    console.print()


def stream_audio(config: AppConfig, mode: str) -> None:
    console.print(
        "\n[red]\\[Notice][/red] [cyan]This feature requires Android 11 or higher.[/cyan]"
    )
    with console.status("[info]Detecting Android version...[/info]"):
        android_ver = _check_android_version()

    if android_ver is None:
        print_error("No connected device found.\n[green] Going back to Main Menu[/green]")
        return

    console.print(f"\n[green]Detected Android Version: {android_ver}[/green]")

    if android_ver < 11:
        print_error("Android version too old. Going back to Main Menu.")
        return

    if mode == "mic":
        console.print("\n[green]Streaming Microphone Audio\n\n[red]Press Ctrl+C to Stop.[/red][/green]\n")
        subprocess.run(["scrcpy", "--no-video", "--audio-source=mic"])
    else:
        console.print("\n[green]Streaming Device Audio\n\n[red]Press Ctrl+C to Stop.[/red][/green]\n")
        subprocess.run(["scrcpy", "--no-video"])

    console.print()
