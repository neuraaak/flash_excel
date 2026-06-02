# ///////////////////////////////////////////////////////////////
# PATHS - Project-level directory constants
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

from __future__ import annotations

import sys
from pathlib import Path


def _get_base_dir() -> Path:
    # En mode compilé PyInstaller, les fichiers sont extraits dans sys._MEIPASS
    # En mode développement, on remonte depuis src/flash_excel/ vers la racine
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).parent.parent.parent


PROJECT_ROOT: Path = _get_base_dir()

BIN_DIR: Path = PROJECT_ROOT / "bin"

PRESETS_DIR: Path = BIN_DIR / "presets"
ASSETS_DIR: Path = BIN_DIR / "assets"
THEMES_CONFIG: Path = BIN_DIR / "config" / "theme.config.yaml"
APP_CONFIG: Path = BIN_DIR / "config" / "app.config.yaml"

__all__ = [
    "PROJECT_ROOT",
    "BIN_DIR",
    "PRESETS_DIR",
    "ASSETS_DIR",
    "THEMES_CONFIG",
    "APP_CONFIG",
]
