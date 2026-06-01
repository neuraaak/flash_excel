# ///////////////////////////////////////////////////////////////
# STEPS/CAST - cast_types step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: cast_types.

Casts one or more DataFrame columns to specified target types
(string, int, float, bool, date, datetime).
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
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Mapping from logical type names (as used in presets) to Polars dtypes.
_TYPE_MAP: dict[str, type[pl.DataType]] = {
    "string": pl.String,
    "int": pl.Int64,
    "float": pl.Float64,
    "bool": pl.Boolean,
    "date": pl.Date,
    "datetime": pl.Datetime,
}

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


@action("cast_types")
def cast_types(df: pl.DataFrame, casts: dict[str, str]) -> pl.DataFrame:
    """Cast one or more columns to specified types.

    This is a pure function: no side effects, no I/O.

    Args:
        df: Input DataFrame.
        casts: Mapping from column name to target type name
            (one of: "string", "int", "float", "bool", "date", "datetime").

    Returns:
        pl.DataFrame: New DataFrame with the specified columns cast.

    Raises:
        polars.exceptions.ColumnNotFoundError: If any column in
            ``casts`` does not exist in ``df``.
        KeyError: If a type name is not recognized.
        polars.exceptions.ComputeError: If a column cannot be cast
            to the target type (e.g., non-numeric string → int).

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"amount": ["100", "200"], "active": ["true", "false"]})
        >>> cast_types(df, casts={"amount": "int", "active": "bool"})
        shape: (2, 2)
    """
    if not casts:
        return df

    exprs = [pl.col(col).cast(_TYPE_MAP[type_name]) for col, type_name in casts.items()]
    return df.with_columns(exprs)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["cast_types"]
