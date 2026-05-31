# ///////////////////////////////////////////////////////////////
# STEPS/RENAME - rename_columns step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: rename_columns.

Renames one or more DataFrame columns based on a mapping from
old column names to new column names.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
import polars as pl

# Local imports
from flash_excel.core.registry import action

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


@action("rename_columns")
def rename_columns(df: pl.DataFrame, mapping: dict[str, str]) -> pl.DataFrame:
    """Rename one or more DataFrame columns.

    This is a pure function: no side effects, no I/O.

    Args:
        df: Input DataFrame.
        mapping: Dictionary mapping old column names to new names.

    Returns:
        pl.DataFrame: New DataFrame with renamed columns.

    Raises:
        polars.exceptions.ColumnNotFoundError: If any key in ``mapping``
            does not exist in ``df``.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"old_name": [1], "other": [2]})
        >>> rename_columns(df, mapping={"old_name": "new_name"})
        shape: (1, 2)
    """
    return df.rename(mapping)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["rename_columns"]
