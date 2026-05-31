# ///////////////////////////////////////////////////////////////
# PATHS - Project-level directory constants
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Resolved path constants for the flash-excel runtime layout.

All paths are derived from this file's location inside the source
tree so they remain valid whether the project is run in-place
(``python main.py``) or installed as a wheel.

Layout anchored here::

    flash_excel/                  ← PROJECT_ROOT
    ├── bin/
    │   ├── config/
    │   ├── presets/              ← PRESETS_DIR  (created at app startup)
    │   ├── themes/
    │   └── translations/
    └── src/
        └── flash_excel/
            └── paths.py          ← this file
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# RESOLUTION
# ///////////////////////////////////////////////////////////////

# src/flash_excel/paths.py  →  src/flash_excel/  →  src/  →  project root
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent

BIN_DIR: Path = PROJECT_ROOT / "bin"

PRESETS_DIR: Path = BIN_DIR / "presets"

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "PROJECT_ROOT",
    "BIN_DIR",
    "PRESETS_DIR",
]
