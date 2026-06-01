# ///////////////////////////////////////////////////////////////
# PATHS - Project-level directory constants
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

from __future__ import annotations

from pathlib import Path

# src/flash_excel/paths.py  →  src/flash_excel/  →  src/  →  project root
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent

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
