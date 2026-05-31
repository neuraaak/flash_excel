# ///////////////////////////////////////////////////////////////
# STEPS/SORT - sort_rows step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: sort_rows.

Sorts DataFrame rows by one or more columns, either ascending or
descending. Sort stability follows Polars' default (stable sort).
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


@action("sort_rows")
def sort_rows(
    df: pl.DataFrame,
    by: list[str],
    descending: bool | list[bool] = False,
) -> pl.DataFrame:
    """Sort DataFrame rows by one or more columns.

    This is a pure function: no side effects, no I/O.

    Args:
        df: Input DataFrame.
        by: One or more column names to sort by. The first name
            has the highest sort priority.
        descending: Either a global bool direction for all columns,
            or one bool per column aligned with ``by``.

    Returns:
        pl.DataFrame: New DataFrame with rows sorted as specified.

    Raises:
        polars.exceptions.ColumnNotFoundError: If any column in ``by``
            does not exist in ``df``.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"salaire": [50000, 30000, 40000], "nom": ["C", "A", "B"]})
        >>> sort_rows(df, by=["salaire"], descending=True)
        shape: (3, 2)
        # rows ordered: 50000, 40000, 30000
    """
    return df.sort(by=by, descending=descending)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["sort_rows"]
