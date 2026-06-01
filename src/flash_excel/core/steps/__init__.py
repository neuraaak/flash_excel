# ///////////////////////////////////////////////////////////////
# STEPS/__INIT__ - Auto-import all step modules to trigger registration
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pipeline step functions.

Importing this package ensures all step modules are loaded, which
triggers their `@action` decorators and populates the REGISTRY.
Import order does not matter — each module is self-contained.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports — side-effect imports that populate the REGISTRY
from .cast import cast_types
from .clean import clean_text
from .computed import add_computed_column
from .deduplicate import deduplicate_rows
from .drop import drop_columns
from .fill import fill_nulls
from .filter import filter_rows
from .rename import rename_columns
from .reorder import reorder_columns
from .replace import replace_values
from .select import select_columns
from .sort import sort_rows

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "add_computed_column",
    "cast_types",
    "clean_text",
    "deduplicate_rows",
    "drop_columns",
    "fill_nulls",
    "filter_rows",
    "rename_columns",
    "replace_values",
    "reorder_columns",
    "select_columns",
    "sort_rows",
]
