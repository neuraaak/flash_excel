# ///////////////////////////////////////////////////////////////
# PRESETS/__INIT__ - Public API for the presets layer
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Presets layer public API.

Exposes functions for loading, listing, saving, and deleting TOML
preset files. The parser validates each preset against Pydantic v2
models and raises a `ValueError` with a human-readable message on
any schema violation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .parser import load_preset
from .store import delete_preset, list_presets, save_preset

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "load_preset",
    "list_presets",
    "save_preset",
    "delete_preset",
]
