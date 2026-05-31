# ///////////////////////////////////////////////////////////////
# STORE - Preset file management (list, save, delete)
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Preset store utilities for flash-excel.

Provides filesystem-level operations for managing TOML preset files:
listing available presets in a directory, persisting a `Preset`
instance to disk, and removing a preset file.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path

# Local imports
from flash_excel.core.models import Preset

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def list_presets(directory: Path) -> list[Path]:
    """Return a sorted list of ``.toml`` files in a directory.

    Only files with a ``.toml`` extension are included. The directory
    is not searched recursively. Paths are sorted alphabetically by
    filename.

    Args:
        directory: Path to the directory containing preset files.

    Returns:
        list[Path]: Sorted list of ``.toml`` file paths. Returns an
            empty list if the directory does not exist or contains no
            ``.toml`` files.

    Example:
        >>> from pathlib import Path
        >>> presets = list_presets(Path("presets/"))
        >>> [p.name for p in presets]
        ['nettoyage_rh.toml', 'rapport_mensuel.toml']
    """
    if not directory.exists():
        return []
    return sorted(directory.glob("*.toml"), key=lambda p: p.name)


def save_preset(preset: Preset, path: Path) -> None:
    """Serialize a Preset instance to a TOML file on disk.

    Creates any missing parent directories. Overwrites any existing
    file at ``path``. The TOML is generated from the Pydantic model's
    ``model_dump`` output and formatted to match the expected preset
    structure (``[meta]`` + ``[[steps]]``).

    Args:
        preset: Validated Preset instance to persist.
        path: Destination path for the ``.toml`` file.

    Raises:
        OSError: If the file cannot be written (e.g., permission
            denied, disk full).

    Example:
        >>> from pathlib import Path
        >>> from flash_excel.core.models import Preset, PresetMeta
        >>> p = Preset(meta=PresetMeta(name="Test"), steps=[])
        >>> save_preset(p, Path("presets/test.toml"))
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    toml_content = _preset_to_toml(preset)
    path.write_text(toml_content, encoding="utf-8")


def delete_preset(path: Path) -> None:
    """Delete a preset file from disk.

    If the file does not exist, this function is a no-op (no error
    is raised). Useful for idempotent cleanup operations.

    Args:
        path: Path to the ``.toml`` preset file to remove.

    Raises:
        OSError: If the path exists but cannot be removed (e.g.,
            permission denied).

    Example:
        >>> from pathlib import Path
        >>> delete_preset(Path("presets/obsolete.toml"))
    """
    if path.exists():
        path.unlink()


# ///////////////////////////////////////////////////////////////
# PRIVATE HELPERS
# ///////////////////////////////////////////////////////////////


def _preset_to_toml(preset: Preset) -> str:
    """Serialize a Preset to a TOML-formatted string.

    Produces a human-readable TOML document with a ``[meta]`` section
    followed by one ``[[steps]]`` block per step.

    Args:
        preset: The Preset instance to serialize.

    Returns:
        str: TOML-formatted string representing the preset.
    """
    lines: list[str] = []

    # [meta] section
    lines.append("[meta]")
    lines.append(f"name = {_toml_value(preset.meta.name)}")
    lines.append(f"description = {_toml_value(preset.meta.description)}")
    lines.append(f"csv_separator = {_toml_value(preset.meta.csv_separator)}")
    lines.append(f"csv_encoding = {_toml_value(preset.meta.csv_encoding)}")
    lines.append(f"source_columns = {_toml_value(preset.meta.source_columns)}")
    lines.append(f"source_types = {_toml_value(preset.meta.source_types)}")
    lines.append("")

    # [[steps]] sections
    for step in preset.steps:
        lines.append("[[steps]]")
        step_data = step.model_dump()
        for key, value in step_data.items():
            lines.append(f"{key} = {_toml_value(value)}")
        lines.append("")

    return "\n".join(lines)


def _toml_value(value: object) -> str:
    """Convert a Python value to its TOML literal representation.

    Handles strings, booleans, integers, floats, lists, and dicts.
    Nested structures (e.g., ``conditions`` list of dicts) are
    serialized as inline TOML tables.

    Args:
        value: Python value to convert.

    Returns:
        str: TOML-compatible string representation.
    """
    if isinstance(value, bool):
        # Must be checked before int, since bool is a subclass of int.
        return "true" if value else "false"
    if isinstance(value, str):
        escaped = (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )
        return f'"{escaped}"'
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, list):
        items = ", ".join(_toml_value(item) for item in value)
        return f"[{items}]"
    if isinstance(value, dict):
        # Inline table: { key = value, ... }
        pairs = ", ".join(
            f"{_toml_key(str(k))} = {_toml_value(v)}" for k, v in value.items()
        )
        return "{" + pairs + "}"
    return str(value)


def _toml_key(key: str) -> str:
    """Return a TOML-safe inline-table key (always quoted)."""
    escaped = key.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "list_presets",
    "save_preset",
    "delete_preset",
]
