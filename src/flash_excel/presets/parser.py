# ///////////////////////////////////////////////////////////////
# PARSER - TOML preset loading and Pydantic v2 validation
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
TOML preset parser for flash-excel.

Reads a ``.toml`` preset file and validates its content against the
`Preset` Pydantic v2 model. On validation failure, Pydantic's
technical error is translated into a plain-language `ValueError`
suitable for display to non-technical end users.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import tomllib
from pathlib import Path

# Third-party imports
from pydantic import ValidationError

# Local imports
from flash_excel.core.models import Preset

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def load_preset(path: Path) -> Preset:
    """Load and validate a TOML preset file.

    Reads the file at ``path`` with the stdlib ``tomllib`` parser,
    then validates the resulting dictionary against the `Preset` Pydantic
    model. Any validation error is caught and re-raised as a plain
    `ValueError` with a human-readable message.

    Args:
        path: Path to the ``.toml`` preset file.

    Returns:
        Preset: Validated preset instance ready for use with
            `run_pipeline`.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        ValueError: If the TOML cannot be parsed, or if the preset
            structure does not match the expected schema. The message
            is human-readable and safe to display to non-technical users.

    Example:
        >>> from pathlib import Path
        >>> preset = load_preset(Path("presets/rapport_rh.toml"))
        >>> preset.meta.name
        'Rapport mensuel RH'
    """
    # Read raw bytes — tomllib requires binary mode.
    try:
        raw_bytes = path.read_bytes()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Preset file not found: '{path}'. "
            "Please check that the file exists and the path is correct."
        ) from None

    # Parse TOML.
    try:
        data = tomllib.loads(raw_bytes.decode("utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(
            f"The preset file '{path.name}' contains invalid TOML syntax.\n"
            f"Details: {exc}"
        ) from exc

    # Validate against Pydantic model.
    try:
        return Preset.model_validate(data)
    except ValidationError as exc:
        # Convert Pydantic's technical errors into plain-language messages.
        messages = _format_validation_errors(exc)
        raise ValueError(
            f"The preset '{path.name}' contains configuration errors:\n{messages}"
        ) from exc


# ///////////////////////////////////////////////////////////////
# PRIVATE HELPERS
# ///////////////////////////////////////////////////////////////


def _format_validation_errors(exc: ValidationError) -> str:
    """Format Pydantic ValidationError into a readable multi-line string.

    Args:
        exc: The ValidationError raised during model validation.

    Returns:
        str: Newline-separated list of human-readable error descriptions.
    """
    lines: list[str] = []
    for error in exc.errors():
        location = " > ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        lines.append(f"  - {location}: {message}")
    return "\n".join(lines)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["load_preset"]
