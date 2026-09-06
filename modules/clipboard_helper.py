"""Clipboard helper based on polygraphene/adb-clip (MIT).

Raw ``adb shell cmd clipboard ...`` / ``service call clipboard ...`` commands
are not implemented / not stable on modern Android, so clipboard read/write
goes through a tiny ``app_process`` helper that talks to ClipboardManager as
``com.android.shell`` (see https://github.com/polygraphene/adb-clip).

Distribution: download-on-first-use. The prebuilt ``clip.jar`` is fetched from
the pinned GitHub release, SHA-256 verified, cached under the user's home
directory, then pushed to ``/data/local/tmp`` on the device.
"""

from __future__ import annotations

import hashlib
import tempfile
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Pinned upstream release (bump deliberately, update hash + size together).
# ---------------------------------------------------------------------------
CLIP_JAR_URL = (
    "https://github.com/polygraphene/adb-clip/releases/download/v0.0.3/clip.jar"
)
CLIP_JAR_SHA256 = "59cb16fabeddcb7a0b5835ce4b8223d4520057334acd2e19b06994342db65fd1"
CLIP_JAR_SIZE = 1933

REMOTE_JAR = "/data/local/tmp/clip.jar"
REMOTE_BIN = "/data/local/tmp/clip"

# Inlined equivalent of upstream `clip` wrapper script. Kept inline so only
# clip.jar itself is downloaded (no executable shell script fetched remotely).
WRAPPER_SCRIPT = (
    "#!/system/bin/sh\n"
    "ANDROID_ROOT=/system ANDROID_DATA=/data "
    "CLASSPATH=/data/local/tmp/clip.jar exec app_process /system/bin Clip \"$@\"\n"
)

# Shown when Android refuses background clipboard access (device locked etc.).
LOCKED_HINT = (
    "Clipboard unavailable: unlock the device and keep the screen on, "
    "then try again."
)


def cache_dir() -> Path:
    """Local cache for the downloaded helper jar."""
    return Path.home() / ".phonesploit-pro" / "helpers" / "adb-clip"


def cached_jar() -> Path:
    return cache_dir() / "clip.jar"


def sh_single_quote(text: str) -> str:
    """Quote text for the on-device shell: ' -> '\\''."""
    return "'" + text.replace("'", "'\\''") + "'"


def remote_set_command(text: str) -> str:
    """Full remote shell string for a set, e.g. ``/data/.../clip 'a b'``.

    Passed as ONE argv element after ``adb shell`` so the device shell keeps
    spaces/quotes together (upstream issue #1: unquoted multi-word text was
    truncated). Upstream joins argv with spaces, this quoting keeps it exact.
    """
    return f"{REMOTE_BIN} {sh_single_quote(text)}"


def _adb():
    from modules.console import adb  # deferred to avoid import cycles

    return adb


def _download_jar(dest: Path) -> tuple[bool, str | None]:
    from modules.console import task_status

    try:
        cache_dir().mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return False, f"Cannot create helper cache: {e}"

    tmp = dest.with_suffix(".tmp")
    try:
        with task_status("[info]Downloading clipboard helper…[/info]"):
            with urllib.request.urlopen(CLIP_JAR_URL, timeout=30) as resp, open(
                tmp, "wb"
            ) as fh:
                digest = hashlib.sha256()
                total = 0
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    total += len(chunk)
                    digest.update(chunk)
                    fh.write(chunk)
    except Exception as e:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return False, (
            "Could not download clipboard helper (internet required on first "
            f"use): {e}"
        )

    if digest.hexdigest() != CLIP_JAR_SHA256:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return False, (
            "Clipboard helper checksum mismatch — refusing to push "
            "(release may have changed; aborting for safety)."
        )
    if CLIP_JAR_SIZE and total != CLIP_JAR_SIZE:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return False, "Clipboard helper size mismatch — refusing to push."
    try:
        tmp.replace(dest)
    except OSError as e:
        return False, f"Cannot cache clipboard helper: {e}"
    return True, None


def _remote_ready() -> bool:
    adb = _adb()
    r = adb(["shell", f"test -x {REMOTE_BIN} && test -f {REMOTE_JAR} && echo OK"])
    return r.returncode == 0 and r.stdout.strip() == "OK"


def ensure_clip_helper() -> tuple[bool, str | None]:
    """Make sure the helper is cached locally and deployed on the device."""
    from modules.console import task_status

    jar = cached_jar()
    if not jar.is_file():
        ok, err = _download_jar(jar)
        if not ok:
            return False, err
    else:
        # Re-verify a stale/corrupt cache entry without re-downloading blindly.
        try:
            if jar.stat().st_size != CLIP_JAR_SIZE or (
                hashlib.sha256(jar.read_bytes()).hexdigest() != CLIP_JAR_SHA256
            ):
                ok, err = _download_jar(jar)
                if not ok:
                    return False, err
        except OSError as e:
            return False, f"Cannot read cached clipboard helper: {e}"

    if _remote_ready():
        return True, None

    adb = _adb()
    with task_status("[info]Installing clipboard helper on device…[/info]"):
        push_jar = adb(["push", str(jar), REMOTE_JAR])
    out = (push_jar.stdout + push_jar.stderr).strip()
    if push_jar.returncode != 0:
        return False, f"Could not push clipboard helper: {out or 'adb push failed'}"

    # Push the tiny wrapper script via a temp file (avoids remote quoting).
    local_wrap: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix="_clip", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(WRAPPER_SCRIPT)
            local_wrap = Path(fh.name)
        push_bin = adb(["push", str(local_wrap), REMOTE_BIN])
        pout = (push_bin.stdout + push_bin.stderr).strip()
        if push_bin.returncode != 0:
            return False, f"Could not push clipboard wrapper: {pout or 'adb push failed'}"
        chmod = adb(["shell", "chmod", "755", REMOTE_BIN])
        cout = (chmod.stdout + chmod.stderr).strip()
        if chmod.returncode != 0:
            return False, f"Could not chmod clipboard helper: {cout or 'chmod failed'}"
    finally:
        if local_wrap is not None:
            try:
                local_wrap.unlink(missing_ok=True)
            except OSError:
                pass

    if not _remote_ready():
        return False, "Clipboard helper install verification failed."
    return True, None


def _helper_failed(out: str, returncode: int) -> str | None:
    """Return a friendly error, or None when the helper invocation looks fine."""
    lowered = (out or "").lower()
    if returncode == 0 and "exception" not in lowered and "traceback" not in lowered:
        return None
    if any(
        k in lowered
        for k in ("device locked", "screen", "cannot access clipboard", "locked")
    ):
        return LOCKED_HINT
    if "not found" in lowered or "no such file" in lowered:
        return "Clipboard helper missing on device — reinstall failed."
    if "unauthorized" in lowered or "no devices" in lowered or "device offline" in lowered:
        return out.strip() or "Device not connected."
    if returncode != 0 or "exception" in lowered or "traceback" in lowered:
        detail = out.strip().splitlines()
        short = detail[-1] if detail else f"helper exited with code {returncode}"
        return f"Clipboard helper failed: {short} ({LOCKED_HINT})"
    return None


def clip_get() -> tuple[str | None, str | None]:
    """Read clipboard. Returns (content, error); ('', None) means empty."""
    from modules.console import task_status

    ok, err = ensure_clip_helper()
    if not ok:
        return None, err
    adb = _adb()
    with task_status("[info]Reading clipboard…[/info]"):
        r = adb(["shell", REMOTE_BIN])
    out = (r.stdout or "").rstrip("\r\n")
    err_text = _helper_failed((r.stdout or "") + (r.stderr or ""), r.returncode)
    if err_text:
        # Empty clipboard prints nothing with rc 0; anything else is an error.
        if r.returncode == 0 and not out and not (r.stderr or "").strip():
            return "", None
        return None, err_text
    return out, None


def clip_set(text: str) -> tuple[bool, str | None]:
    """Write clipboard. Returns (success, error)."""
    from modules.console import task_status

    ok, err = ensure_clip_helper()
    if not ok:
        return False, err
    adb = _adb()
    with task_status("[info]Setting clipboard…[/info]"):
        r = adb(["shell", remote_set_command(text)])
    out = (r.stdout or "") + (r.stderr or "")
    err_text = _helper_failed(out, r.returncode)
    if err_text:
        return False, err_text
    return True, None
