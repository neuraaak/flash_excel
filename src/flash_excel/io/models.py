# ///////////////////////////////////////////////////////////////
# IO MODELS - I/O metadata models
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""Typed models for I/O layer metadata.

This module contains Pydantic models used to validate and transport
filesystem metadata across the application boundaries.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import Literal

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_SUPPORTED_SUFFIXES = {".xlsx", ".xls", ".xlsm", ".csv"}


# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class FileLoaderResult(BaseModel):
    """Validated metadata for a file selected in the UI loader.

    Attributes:
        path: Resolved absolute file path.
        file_name: Basename of the selected file.
        directory: Parent directory containing the file.
        suffix: Lowercase extension including leading dot.
        size_bytes: File size in bytes.
        file_type: Normalized category derived from extension.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: Path
    file_name: str = Field(min_length=1)
    directory: Path
    suffix: str
    size_bytes: int = Field(ge=0)
    file_type: Literal["excel", "csv"]

    @field_validator("path")
    @classmethod
    def _validate_path(cls, value: Path) -> Path:
        resolved = value.expanduser().resolve()
        if not resolved.exists() or not resolved.is_file():
            raise ValueError("Selected path must be an existing file")
        return resolved

    @field_validator("suffix")
    @classmethod
    def _validate_suffix(cls, value: str) -> str:
        suffix = value.lower()
        if suffix not in _SUPPORTED_SUFFIXES:
            raise ValueError(
                "Unsupported file format. Allowed: .xlsx, .xls, .xlsm, .csv"
            )
        return suffix

    @computed_field(return_type=bool)
    @property
    def is_excel(self) -> bool:
        """Return True when selected file belongs to Excel formats."""
        return self.file_type == "excel"

    @computed_field(return_type=bool)
    @property
    def is_csv(self) -> bool:
        """Return True when selected file is CSV."""
        return self.file_type == "csv"

    @classmethod
    def from_path(cls, file_path: Path) -> FileLoaderResult:
        """Build and validate metadata from a file path."""
        resolved = file_path.expanduser().resolve()
        suffix = resolved.suffix.lower()
        file_type: Literal["excel", "csv"] = (
            "excel" if suffix in {".xlsx", ".xls", ".xlsm"} else "csv"
        )
        return cls(
            path=resolved,
            file_name=resolved.name,
            directory=resolved.parent,
            suffix=suffix,
            size_bytes=resolved.stat().st_size,
            file_type=file_type,
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["FileLoaderResult"]
