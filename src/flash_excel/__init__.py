# ///////////////////////////////////////////////////////////////
# FLASH_EXCEL - Main Module
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""flash-excel - Desktop utility to transform Excel/CSV files via TOML presets."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys

# Local imports
from ._version import __version__

# ///////////////////////////////////////////////////////////////
# METADATA INFORMATION
# ///////////////////////////////////////////////////////////////

__author__ = "Neuraaak"
__maintainer__ = "Neuraaak"
__description__ = (
    "flash-excel - Desktop utility to transform Excel/CSV files via TOML presets"
)
__python_requires__ = ">=3.11"
__keywords__ = [
    "excel",
    "csv",
    "data",
    "transformation",
    "pipeline",
    "toml",
    "polars",
    "desktop",
]
__url__ = "https://github.com/neuraaak/flash-excel"
__repository__ = "https://github.com/neuraaak/flash-excel"

# ///////////////////////////////////////////////////////////////
# PYTHON VERSION CHECK
# ///////////////////////////////////////////////////////////////

if sys.version_info < (3, 11):  # noqa: UP036
    raise RuntimeError(
        f"flash-excel {__version__} requires Python 3.11 or higher. "
        f"Current version: {sys.version}"
    )

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = []
