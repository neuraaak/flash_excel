# ///////////////////////////////////////////////////////////////
# STEPS/FILL - fill_nulls step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: fill_nulls.

Fills null/missing values in columns using one of three strategies:
- value: fill with a specific scalar value
- forward: propagate previous non-null value downward (forward fill)
- backward: propagate next non-null value upward (backward fill)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import Any

# Third-party imports
import polars as pl

# Local imports
from flash_excel.core.registry import action

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


@action("fill_nulls")
def fill_nulls(
    df: pl.DataFrame,
    columns: list[str],
    strategy: str = "value",
    value: Any = None,
) -> pl.DataFrame:
    """Fill null values in specified columns using a selected strategy.

    This is a pure function: no side effects, no I/O.

    Args:
        df: Input DataFrame.
        columns: List of column names to process.
        strategy: One of "value", "forward", or "backward".
            - "value": fill with the scalar ``value`` argument.
            - "forward": fill with the previous non-null value.
            - "backward": fill with the next non-null value.
        value: The scalar value to use when strategy is "value".
            Required and must be non-None when strategy is "value".

    Returns:
        pl.DataFrame: New DataFrame with nulls filled in the target columns.

    Raises:
        polars.exceptions.ColumnNotFoundError: If any column in
            ``columns`` does not exist in ``df``.
        ValueError: If strategy is "value" but ``value`` is None.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"country": ["France", None, None, "Spain"]})
        >>> fill_nulls(df, columns=["country"], strategy="value", value="Unknown")
        shape: (4, 1)
    """
    if not columns:
        return df

    if strategy == "value":
        if value is None:
            raise ValueError("fill_nulls strategy 'value' requires a non-null 'value'.")
        return df.with_columns([pl.col(c).fill_null(value) for c in columns])

    elif strategy == "forward":
        return df.with_columns([pl.col(c).forward_fill() for c in columns])

    elif strategy == "backward":
        return df.with_columns([pl.col(c).backward_fill() for c in columns])

    else:
        raise ValueError(
            f"Invalid fill_nulls strategy: '{strategy}'. "
            "Expected 'value', 'forward', or 'backward'."
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["fill_nulls"]
