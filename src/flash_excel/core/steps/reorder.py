# ///////////////////////////////////////////////////////////////
# STEPS/REORDER - reorder_columns step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: reorder_columns.

Reorders DataFrame columns so that the listed columns appear first,
in the given order. Any columns not listed are appended afterward,
preserving their relative order from the original DataFrame.
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


@action("reorder_columns")
def reorder_columns(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    """Reorder DataFrame columns, placing listed columns first.

    Columns not present in ``columns`` are appended at the end in
    their original relative order. This is a pure function.

    Args:
        df: Input DataFrame.
        columns: Desired leading column order. Every name must exist
            in ``df``; extra names in ``df`` are placed after.

    Returns:
        pl.DataFrame: New DataFrame with reordered columns.

    Raises:
        polars.exceptions.ColumnNotFoundError: If any name in
            ``columns`` does not exist in ``df``.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"b": [2], "a": [1], "c": [3]})
        >>> reorder_columns(df, columns=["a", "b"])
        shape: (1, 3)
        # columns order: a, b, c
    """
    # Columns listed explicitly come first; remaining columns follow.
    remaining = [col for col in df.columns if col not in columns]
    return df.select(columns + remaining)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["reorder_columns"]
