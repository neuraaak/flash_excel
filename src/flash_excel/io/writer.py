# ///////////////////////////////////////////////////////////////
# WRITER - File writing functions (Excel and CSV)
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
File writing utilities for flash-excel.

Provides functions to persist a transformed Polars DataFrame to
Excel (.xlsx) or CSV format. Output paths are created including
any missing parent directories.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Third-party imports
import polars as pl

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


_EXCEL_DTYPE_FORMATS: dict = {
    pl.Date: "DD/MM/YYYY",
    pl.Datetime: "DD/MM/YYYY HH:MM:SS",
}


def _coerce_booleans(df: pl.DataFrame) -> pl.DataFrame:
    """Convert Boolean columns to VRAI/FAUX strings (Excel-friendly)."""
    bool_cols = [name for name, dtype in df.schema.items() if dtype == pl.Boolean]
    if not bool_cols:
        return df
    return df.with_columns(
        [
            pl.when(pl.col(c)).then(pl.lit("VRAI")).otherwise(pl.lit("FAUX")).alias(c)
            for c in bool_cols
        ]
    )


def write_excel(df: pl.DataFrame, path: Path) -> None:
    """Write a DataFrame to an Excel file (.xlsx).

    Boolean columns are converted to VRAI/FAUX. Date and Datetime columns
    receive locale-appropriate format strings. All other types are written
    natively via xlsxwriter.

    Args:
        df: DataFrame to write.
        path: Destination path for the ``.xlsx`` file.

    Raises:
        OSError: If the parent directory cannot be created or the file
            cannot be written (e.g., permission denied).

    Example:
        >>> import polars as pl
        >>> from pathlib import Path
        >>> df = pl.DataFrame({"nom": ["Alice"], "salaire": [50000]})
        >>> write_excel(df, Path("output/rapport.xlsx"))
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df = _coerce_booleans(df)
    df.write_excel(path, dtype_formats=_EXCEL_DTYPE_FORMATS)


def write_csv(
    df: pl.DataFrame,
    path: Path,
    separator: str = ";",
) -> None:
    """Write a DataFrame to a CSV file.

    Creates any missing parent directories before writing. Overwrites
    the file if it already exists at ``path``. Uses semicolon as the
    default delimiter to match the French Excel convention.

    Args:
        df: DataFrame to write.
        path: Destination path for the CSV file.
        separator: Column delimiter character. Defaults to ``";"``.

    Raises:
        OSError: If the parent directory cannot be created or the file
            cannot be written (e.g., permission denied).

    Example:
        >>> import polars as pl
        >>> from pathlib import Path
        >>> df = pl.DataFrame({"nom": ["Alice"], "salaire": [50000]})
        >>> write_csv(df, Path("output/rapport.csv"), separator=";")
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_csv(path, separator=separator)


def write_parquet(df: pl.DataFrame, path: Path) -> None:
    """Write a DataFrame to a Parquet file.

    Creates any missing parent directories before writing.

    Args:
        df: DataFrame to write.
        path: Destination path for the ``.parquet`` file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path)


def write_dataframe(df: pl.DataFrame, path: Path, fmt: str) -> None:
    """Dispatch DataFrame writing based on format.

    Args:
        df: DataFrame to write.
        path: Destination path (extension must match fmt).
        fmt: One of ``'xlsx'``, ``'csv'``, ``'parquet'``. Never ``'keep'`` — resolve first.

    Raises:
        ValueError: If fmt is not a supported format.
    """
    if fmt == "xlsx":
        write_excel(df, path)
    elif fmt == "csv":
        write_csv(df, path)
    elif fmt == "parquet":
        write_parquet(df, path)
    else:
        raise ValueError(
            f"Unsupported format: {fmt!r}. Expected 'xlsx', 'csv', or 'parquet'."
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "write_excel",
    "write_csv",
    "write_parquet",
    "write_dataframe",
]
