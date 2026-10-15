from __future__ import annotations

from modules.config import AppConfig
from modules.console import ask
from modules.ext_runner import report_dir
from modules.lockknife._common import open_category, run_lk


def _offline_pin(config: AppConfig) -> None:
    h = ask("PIN hash (hex): ").strip()
    length = ask("Length (4/6/8) [4]: ").strip() or "4"
    algo = ask("Algorithm (sha1/sha256) [sha256]: ").strip() or "sha256"
    out = report_dir("lockknife") / "crack-pin.json"
    run_lk(
        config,
        ["crack", "pin", "--hash", h, "--algo", algo, "--length", length, "--output", str(out)],
        need_device=False,
    )


def _password_dict(config: AppConfig) -> None:
    h = ask("Password hash (hex): ").strip()
    algo = ask("Algorithm (sha256) [sha256]: ").strip() or "sha256"
    wordlist = ask("Wordlist path: ").strip()
    run_lk(
        config,
        ["crack", "password", "--hash", h, "--algo", algo, "--wordlist", wordlist],
        need_device=False,
    )


def _password_rules(config: AppConfig) -> None:
    h = ask("Password hash (hex): ").strip()
    algo = ask("Algorithm [sha256]: ").strip() or "sha256"
    wordlist = ask("Wordlist path: ").strip()
    run_lk(
        config,
        [
            "crack",
            "password-rules",
            "--hash",
            h,
            "--algo",
            algo,
            "--wordlist",
            wordlist,
            "--max-suffix",
            "100",
        ],
        need_device=False,
    )


def _pin_device(config: AppConfig) -> None:
    length = ask("PIN length (4/6/8) [6]: ").strip() or "6"
    run_lk(config, ["crack", "pin-device", "--length", length])


def _gesture(config: AppConfig) -> None:
    run_lk(config, ["crack", "gesture"])


def _wifi(config: AppConfig) -> None:
    run_lk(config, ["crack", "wifi"])


def _keystore(config: AppConfig) -> None:
    run_lk(config, ["crack", "keystore"])


def _passkeys(config: AppConfig) -> None:
    run_lk(config, ["crack", "passkeys", "--limit", "200"])


def open_menu(config: AppConfig) -> None:
    open_category(
        config,
        "lockknife-crack",
        "Crack",
        [
            ("Offline PIN bruteforce", _offline_pin),
            ("Dictionary password crack", _password_dict),
            ("Password rules crack", _password_rules),
            ("Device-side PIN (ADB)", _pin_device),
            ("Gesture / pattern recovery", _gesture),
            ("Wi‑Fi passwords (often needs root)", _wifi),
            ("Keystore list", _keystore),
            ("Passkeys (Android 14+)", _passkeys),
        ],
    )
