from __future__ import annotations

from modules.config import AppConfig
from modules.console import ask
from modules.ext_runner import pick_package, preflight_serial, report_dir
from modules.lockknife._common import open_category, run_lk


def _scan(config: AppConfig) -> None:
    out = report_dir("lockknife") / "security-scan.json"
    run_lk(config, ["security", "scan", "--output", str(out)])


def _selinux(config: AppConfig) -> None:
    out = report_dir("lockknife") / "selinux.json"
    run_lk(config, ["security", "selinux", "--output", str(out)])


def _bootloader(config: AppConfig) -> None:
    out = report_dir("lockknife") / "bootloader.json"
    run_lk(config, ["security", "bootloader", "--output", str(out)])


def _hardware(config: AppConfig) -> None:
    out = report_dir("lockknife") / "hardware.json"
    run_lk(config, ["security", "hardware", "--output", str(out)])


def _network_scan(config: AppConfig) -> None:
    out = report_dir("lockknife") / "network-scan.json"
    run_lk(config, ["security", "network-scan", "--output", str(out)])


def _attack_surface(config: AppConfig) -> None:
    pkg = pick_package(config)
    if not pkg:
        return
    serial = preflight_serial()
    if not serial:
        return
    out = report_dir("lockknife") / "attack-surface.json"
    run_lk(
        config,
        ["security", "attack-surface", "--package", pkg, "--serial", serial, "--output", str(out)],
    )


def _owasp(config: AppConfig) -> None:
    artifacts = ask("Artifacts JSON path: ").strip()
    run_lk(config, ["security", "owasp", "--artifacts", artifacts], need_device=False)


def _pcap_capture(config: AppConfig) -> None:
    duration = ask("Capture duration seconds [30]: ").strip() or "30"
    out = report_dir("lockknife") / "capture.pcap"
    run_lk(
        config,
        ["network", "capture", "--duration", duration, "--output", str(out)],
        timeout=float(duration) + 60,
    )


def _pcap_analyze(config: AppConfig) -> None:
    pcap = ask("PCAP path: ").strip()
    run_lk(config, ["network", "analyze", pcap], need_device=False)


def _wallet_scan_device(config: AppConfig) -> None:
    serial = preflight_serial()
    if not serial:
        return
    case = ask("Case directory (optional): ").strip()
    args = ["crypto-wallet", "scan-device", "-s", serial]
    if case:
        args.extend(["--case-dir", case])
    run_lk(config, args)


def _api_discovery(config: AppConfig) -> None:
    pcap = ask("PCAP file path: ").strip()
    if not pcap:
        return
    out = report_dir("lockknife") / "api-discovery.json"
    run_lk(config, ["network", "api-discovery", pcap, "--output", str(out)], need_device=False)


def _wallet(config: AppConfig) -> None:
    db = ask("Wallet SQLite DB path: ").strip()
    out = report_dir("lockknife") / "wallet.json"
    lookup = ask("Lookup addresses online? (y/N): ").strip().lower() in ("y", "yes")
    args = ["crypto-wallet", "wallet", db, "--output", str(out)]
    if lookup:
        args.append("--lookup")
    run_lk(config, args, need_device=False)


def open_menu(config: AppConfig) -> None:
    open_category(
        config,
        "lockknife-security",
        "Security & network",
        [
            ("Posture scan", _scan),
            ("SELinux status", _selinux),
            ("Bootloader", _bootloader),
            ("Hardware security", _hardware),
            ("Network scan", _network_scan),
            ("App attack surface", _attack_surface),
            ("OWASP helper (from JSON)", _owasp),
            ("PCAP capture (root/tcpdump)", _pcap_capture),
            ("Analyze PCAP", _pcap_analyze),
            ("API discovery from PCAP", _api_discovery),
            ("Crypto wallet scan (device)", _wallet_scan_device),
            ("Crypto wallet artifacts (SQLite)", _wallet),
        ],
    )
