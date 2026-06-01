# ///////////////////////////////////////////////////////////////
# LOADER - File reading functions (Excel and CSV)
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
File loading utilities for flash-excel.

Provides functions to read Excel files (via the fastexcel/calamine
Rust backend) and CSV files (via Polars' native reader). A lightweight
`read_headers` function loads only column names without materializing
the full DataFrame, enabling fast schema inspection in the UI.
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


def read_excel(path: Path, sheet: int = 0) -> pl.DataFrame:
    """Read an Excel file into a Polars DataFrame.

    Uses the ``fastexcel`` backend (Rust/calamine) for performance.
    The file is fully materialized in memory.

    Args:
        path: Absolute or relative path to the ``.xlsx`` / ``.xls``
            file.
        sheet: Zero-based sheet index to read. Defaults to ``0``
            (first sheet).

    Returns:
        pl.DataFrame: DataFrame containing all rows and columns from
            the specified sheet.

    Raises:
        FileNotFoundError: If ``path`` does not point to an existing
            file.
        Exception: Propagates any error raised by the ``fastexcel``
            backend (e.g., corrupt file, unsupported format).

    Example:
        >>> from pathlib import Path
        >>> df = read_excel(Path("data/report.xlsx"), sheet=0)
        >>> df.shape
        (1500, 12)
    """
    excel_data = pl.read_excel(path, sheet_id=sheet, engine="calamine")
    if isinstance(excel_data, pl.DataFrame):
        return excel_data
    if isinstance(excel_data, dict):
        if not excel_data:
            raise ValueError("Excel file contains no readable sheets.")
        first_sheet = next(iter(excel_data.values()))
        if isinstance(first_sheet, pl.DataFrame):
            return first_sheet
        raise TypeError("Unexpected sheet payload type from polars.read_excel().")
    raise TypeError("Unexpected return type from polars.read_excel().")


def read_csv(
    path: Path,
    separator: str = ";",
    encoding: str = "utf8-lossy",
) -> pl.DataFrame:
    """Read a CSV file into a Polars DataFrame.

    Defaults to French-style semicolon-separated files with
    ``utf8-lossy`` encoding to absorb ``cp1252`` / ``latin-1``
    characters common in Excel exports.

    Args:
        path: Absolute or relative path to the CSV file.
        separator: Column delimiter character. Defaults to ``";"``.
        encoding: File encoding. Defaults to ``"utf8-lossy"`` which
            replaces invalid UTF-8 bytes rather than raising an error.

    Returns:
        pl.DataFrame: DataFrame with all rows parsed from the CSV.

    Raises:
        FileNotFoundError: If ``path`` does not point to an existing
            file.
        polars.exceptions.ComputeError: If the file cannot be parsed
            with the given separator or encoding.

    Example:
        >>> from pathlib import Path
        >>> df = read_csv(Path("exports/data.csv"), separator=";")
        >>> df.shape
        (200, 5)
    """
    return pl.read_csv(path, separator=separator, encoding=encoding)


def read_headers(path: Path, separator: str = ";") -> list[str]:
    """Read only the column names from a file without loading all rows.

    Dispatches to the correct reader based on file extension:
    - ``.xlsx`` / ``.xls``: reads the first sheet via fastexcel.
    - All other extensions: treated as CSV with ``n_rows=0``.

    This provides fast schema inspection for the UI (e.g., to populate
    column dropdowns) without the cost of loading the full dataset.

    Args:
        path: Path to the source file.
        separator: CSV delimiter (ignored for Excel files).

    Returns:
        list[str]: Ordered list of column names.

    Raises:
        FileNotFoundError: If ``path`` does not exist.

    Example:
        >>> from pathlib import Path
        >>> headers = read_headers(Path("data/report.xlsx"))
        >>> headers
        ['nom', 'prenom', 'salaire', 'statut']
    """
    suffix = path.suffix.lower()

    if suffix in {".xlsx", ".xls", ".xlsm"}:
        # Read only first row via calamine to get the column names.
        excel_data = pl.read_excel(path, sheet_id=0, engine="calamine")
        if isinstance(excel_data, pl.DataFrame):
            return excel_data.columns
        if isinstance(excel_data, dict):
            if not excel_data:
                return []
            first_sheet = next(iter(excel_data.values()))
            if not isinstance(first_sheet, pl.DataFrame):
                raise TypeError(
                    "Unexpected sheet payload type from polars.read_excel()."
                )
            return first_sheet.columns
        raise TypeError("Unexpected return type from polars.read_excel().")

    # For CSV, n_rows=0 returns an empty DataFrame with the correct schema.
    df = pl.read_csv(
        path,
        separator=separator,
        encoding="utf8-lossy",
        n_rows=0,
    )
    return df.columns


def read_schema(path: Path, separator: str = ";") -> dict[str, str]:
    """Read inferred schema (column -> dtype name) for a source file.

    For Excel files, the first sheet schema is used. For CSV files,
    Polars infers schema from a small row sample.

    Args:
        path: Path to the source file.
        separator: CSV delimiter (ignored for Excel files).

    Returns:
        dict[str, str]: Mapping from column name to dtype name.
    """
    suffix = path.suffix.lower()

    if suffix in {".xlsx", ".xls", ".xlsm"}:
        excel_data = pl.read_excel(path, sheet_id=0, engine="calamine")
        if isinstance(excel_data, pl.DataFrame):
            return {name: str(dtype) for name, dtype in excel_data.schema.items()}
        if isinstance(excel_data, dict):
            if not excel_data:
                return {}
            first_sheet = next(iter(excel_data.values()))
            if not isinstance(first_sheet, pl.DataFrame):
                raise TypeError(
                    "Unexpected sheet payload type from polars.read_excel()."
                )
            return {name: str(dtype) for name, dtype in first_sheet.schema.items()}
        raise TypeError("Unexpected return type from polars.read_excel().")

    df = pl.read_csv(
        path,
        separator=separator,
        encoding="utf8-lossy",
        n_rows=300,
        infer_schema_length=500,
    )
    return {name: str(dtype) for name, dtype in df.schema.items()}


def read_unique_values(
    path: Path,
    column: str,
    separator: str = ";",
    limit: int = 300,
) -> list[str]:
    """Read distinct non-null values for one column (bounded for UI use).

    Args:
        path: Path to the source file.
        column: Source column name to inspect.
        separator: CSV delimiter (ignored for Excel files).
        limit: Maximum number of distinct values to return.

    Returns:
        list[str]: Distinct values converted to strings.
    """
    suffix = path.suffix.lower()

    if suffix in {".xlsx", ".xls", ".xlsm"}:
        df = read_excel(path)
    else:
        df = pl.read_csv(
            path,
            separator=separator,
            encoding="utf8-lossy",
            columns=[column],
        )

    if column not in df.columns:
        return []

    series = df.get_column(column).drop_nulls().unique().sort()
    bounded = series.head(max(1, limit)).to_list()
    return [str(value) for value in bounded]


def read_unique_values_many(
    path: Path,
    columns: list[str],
    separator: str = ";",
    limit: int = 300,
) -> dict[str, list[str]]:
    """Read distinct non-null values for multiple columns in one file pass.

    This avoids repeated full-file reads when the UI needs quick-filter values
    for many columns at once.

    Args:
        path: Path to the source file.
        columns: Source column names to inspect.
        separator: CSV delimiter (ignored for Excel files).
        limit: Maximum number of distinct values per column.

    Returns:
        dict[str, list[str]]: Mapping column -> distinct string values.
    """
    if not columns:
        return {}

    seen: set[str] = set()
    ordered_columns: list[str] = []
    for name in columns:
        if name in seen:
            continue
        seen.add(name)
        ordered_columns.append(name)

    suffix = path.suffix.lower()

    if suffix in {".xlsx", ".xls", ".xlsm"}:
        df = read_excel(path)
    else:
        df = pl.read_csv(
            path,
            separator=separator,
            encoding="utf8-lossy",
            columns=ordered_columns,
        )

    result: dict[str, list[str]] = {}
    bounded_limit = max(1, limit)
    for column in ordered_columns:
        if column not in df.columns:
            result[column] = []
            continue

        series = df.get_column(column).drop_nulls().unique().sort()
        values = series.head(bounded_limit).to_list()
        result[column] = [str(value) for value in values]

    return result


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "read_excel",
    "read_csv",
    "read_headers",
    "read_schema",
    "read_unique_values",
    "read_unique_values_many",
]
