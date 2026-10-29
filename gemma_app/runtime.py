"""Shared process/runtime helpers used by the launcher and setup wizard."""
from __future__ import annotations

import shutil
import sys


def get_python_exe() -> str:
    if getattr(sys, "frozen", False):
        return (
            shutil.which("python")
            or shutil.which("python3")
            or shutil.which("py")
            or "python"
        )
    return sys.executable

