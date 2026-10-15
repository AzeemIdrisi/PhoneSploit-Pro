"""Cross-platform PTY spawn for the in-browser terminal."""

from __future__ import annotations

import sys
from typing import Any


def spawn(argv: list[str]) -> Any:
    if sys.platform == "win32":
        from winpty import PtyProcess  # type: ignore

        return PtyProcess.spawn(argv)
    import ptyprocess

    return ptyprocess.PtyProcess.spawn(argv)
