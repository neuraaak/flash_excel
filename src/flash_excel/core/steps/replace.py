# ///////////////////////////////////////////////////////////////
# STEPS/REPLACE - replace_values step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: replace_values.

Replaces exact values in a target column with mapped replacement values.
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


@action("replace_values")
def replace_values(
    df: pl.DataFrame,
    column: str,
    mapping: dict,
) -> pl.DataFrame:
    """Replace exact values in a column.

    Maps old values to new values (one-to-one). Unmapped values
    are left unchanged. This is a pure function.

    Args:
        df: Input DataFrame.
        column: Target column name.
        mapping: Dictionary mapping old values to new values.
            Values can be any scalar (str, int, float, bool) or None.

    Returns:
        pl.DataFrame: New DataFrame with values replaced in the target column.

    Raises:
        polars.exceptions.ColumnNotFoundError: If ``column`` does not
            exist in ``df``.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"status": ["YES", "NO", "YES"]})
        >>> replace_values(df, column="status", mapping={"YES": "Yes", "NO": "No"})
        shape: (3, 1)
    """
    old_values = list(mapping.keys())
    new_values = list(mapping.values())

    return df.with_columns(pl.col(column).replace(old_values, new_values))


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["replace_values"]
