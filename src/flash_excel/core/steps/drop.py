# ///////////////////////////////////////////////////////////////
# STEPS/DROP - drop_columns step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: drop_columns.

Removes a list of named columns from the DataFrame. If a column
does not exist, Polars raises an error — the pipeline handles this
at the orchestration level.
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


@action("drop_columns")
def drop_columns(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    """Remove named columns from a DataFrame.

    This is a pure function: no side effects, no I/O.

    Args:
        df: Input DataFrame.
        columns: List of column names to remove.

    Returns:
        pl.DataFrame: New DataFrame with the specified columns absent.

    Raises:
        polars.exceptions.ColumnNotFoundError: If any column in
            ``columns`` does not exist in ``df``.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"a": [1], "b": [2], "tmp": [3]})
        >>> drop_columns(df, columns=["tmp"])
        shape: (1, 2)
    """
    return df.drop(columns)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["drop_columns"]
