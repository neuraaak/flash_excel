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


def write_excel(df: pl.DataFrame, path: Path) -> None:
    """Write a DataFrame to an Excel file (.xlsx).

    Creates any missing parent directories before writing. Overwrites
    the file if it already exists at ``path``.

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
    df.write_excel(path)


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


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "write_excel",
    "write_csv",
]
