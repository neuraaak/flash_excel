# ///////////////////////////////////////////////////////////////
# STEPS/SELECT - select_columns step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: select_columns.

Selects a subset of columns from the DataFrame, keeping only
the specified columns in the given order.
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


@action("select_columns")
def select_columns(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    """Select and reorder DataFrame columns.

    Keeps only the specified columns in the given order. Columns not
    listed are removed. This is a pure function.

    Args:
        df: Input DataFrame.
        columns: List of column names to keep, in the desired order.

    Returns:
        pl.DataFrame: New DataFrame with only the selected columns.

    Raises:
        polars.exceptions.ColumnNotFoundError: If any column in
            ``columns`` does not exist in ``df``.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"a": [1], "b": [2], "c": [3]})
        >>> select_columns(df, columns=["c", "a"])
        shape: (1, 2)
    """
    return df.select(columns)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["select_columns"]
