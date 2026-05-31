"""Build service context from AppConfig and active device."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from modules.config import AppConfig
from modules.services.adb import ADBService, DeviceSession


@dataclass
class ServiceContext:
    config: AppConfig
    session: DeviceSession
    adb: ADBService

    @property
    def output_dir(self) -> Path:
        return self.session.output_dir

    def ensure_output_dir(self) -> Path:
        self.session.output_dir.mkdir(parents=True, exist_ok=True)
        return self.session.output_dir


def build_context(
    config: AppConfig,
    serial: str | None = None,
    output_dir: Path | str | None = None,
) -> ServiceContext:
    out = Path(output_dir) if output_dir else Path("Downloaded-Files")
    out.mkdir(parents=True, exist_ok=True)
    session = DeviceSession(serial=serial, output_dir=out)
    adb = ADBService(config.adb_path, serial)
    return ServiceContext(config=config, session=session, adb=adb)
