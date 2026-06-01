# ///////////////////////////////////////////////////////////////
# STEPS/CLEAN - clean_text step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: clean_text.

Applies a configurable set of text cleaning operations to string columns.
Supported ops: trim, collapse, accents, special.
Supported case conversions: lower, upper, title.
"""

from __future__ import annotations

import unicodedata

import polars as pl

from flash_excel.core.registry import action


def _strip_accents(s: str | None) -> str | None:
    if s is None:
        return None
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii")


@action("clean_text")
def clean_text(
    df: pl.DataFrame,
    columns: list[str],
    ops: list[str] | None = None,
    case: str = "none",
) -> pl.DataFrame:
    """Apply text cleaning operations to string columns.

    Args:
        df: Input DataFrame.
        columns: String columns to process.
        ops: List of operations to apply. Supported values:
            - "trim": strip leading/trailing whitespace
            - "collapse": collapse multiple spaces into one
            - "accents": remove accent marks (normalize to ASCII)
            - "special": remove non-alphanumeric/non-space characters
        case: Case conversion to apply after ops. One of:
            "none", "lower", "upper", "title".

    Returns:
        pl.DataFrame: New DataFrame with cleaned columns.
    """
    if not columns:
        return df

    _ops = set(ops or [])

    for c in columns:
        col = df[c]
        if "trim" in _ops:
            col = col.str.strip_chars()
        if "collapse" in _ops:
            col = col.str.replace_all(r"\s+", " ")
        if "accents" in _ops:
            col = col.map_elements(_strip_accents, return_dtype=pl.Utf8)
        if "special" in _ops:
            col = col.str.replace_all(r"[^\w\s]", "")
        if case == "lower":
            col = col.str.to_lowercase()
        elif case == "upper":
            col = col.str.to_uppercase()
        elif case == "title":
            col = col.str.to_titlecase()
        df = df.with_columns(col.alias(c))

    return df


__all__ = ["clean_text"]
