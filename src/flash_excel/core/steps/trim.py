# ///////////////////////////////////////////////////////////////
# STEPS/TRIM - trim_whitespace step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: trim_whitespace.

Removes leading and trailing whitespace from string columns.
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


@action("trim_whitespace")
def trim_whitespace(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    """Trim leading and trailing whitespace from string columns.

    This is a pure function: no side effects, no I/O.

    Args:
        df: Input DataFrame.
        columns: List of column names (typically string columns) to trim.

    Returns:
        pl.DataFrame: New DataFrame with trimmed string columns.

    Raises:
        polars.exceptions.ColumnNotFoundError: If any column in
            ``columns`` does not exist in ``df``.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"name": ["  Alice  ", "  Bob  "]})
        >>> trim_whitespace(df, columns=["name"])
        shape: (2, 1)
        # name: ["Alice", "Bob"]
    """
    if not columns:
        return df

    return df.with_columns([pl.col(c).str.strip_chars() for c in columns])


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["trim_whitespace"]
