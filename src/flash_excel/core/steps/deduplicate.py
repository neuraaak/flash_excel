# ///////////////////////////////////////////////////////////////
# STEPS/DEDUPLICATE - deduplicate_rows step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: deduplicate_rows.

Removes duplicate rows from the DataFrame based on all or a subset
of columns, keeping only the first, last, or no occurrences of duplicates.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library
from typing import Literal, cast

# Third-party imports
import polars as pl

# Local imports
from flash_excel.core.registry import action

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


@action("deduplicate_rows")
def deduplicate_rows(
    df: pl.DataFrame,
    subset: list[str] | None = None,
    keep: str = "first",
) -> pl.DataFrame:
    """Remove duplicate rows from the DataFrame.

    Deduplication can be based on all columns or a subset.
    By default, the first occurrence of a duplicate is kept.

    This is a pure function: no side effects, no I/O.

    Args:
        df: Input DataFrame.
        subset: List of column names to consider for duplicate detection.
            If empty or None, all columns are considered.
        keep: Which occurrence to keep. One of:
            - "first": keep the first occurrence.
            - "last": keep the last occurrence.
            - "none": remove all duplicates (keep no rows with duplicates).

    Returns:
        pl.DataFrame: New DataFrame with duplicate rows removed.

    Raises:
        polars.exceptions.ColumnNotFoundError: If any column in
            ``subset`` does not exist in ``df``.
        ValueError: If ``keep`` is not one of "first", "last", or "none".

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"id": [1, 1, 2], "name": ["A", "A", "B"]})
        >>> deduplicate_rows(df, subset=["id"], keep="first")
        shape: (2, 2)
    """
    # None or empty list means deduplicate on all columns.
    subset_arg = subset if (subset and len(subset) > 0) else None

    # Validate and normalize the keep argument.
    keep_normalized = keep.lower()
    if keep_normalized not in ("first", "last", "none"):
        raise ValueError(
            f"Invalid keep value: '{keep}'. Expected 'first', 'last', or 'none'."
        )

    # Cast to the Polars-expected Literal type so the type checker accepts it.
    keep_arg = cast(Literal["first", "last", "any", "none"], keep_normalized)
    return df.unique(subset=subset_arg, keep=keep_arg)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["deduplicate_rows"]
