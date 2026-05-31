"""Python API exposed to JS via webview.expose(api).

Every public method becomes ``await pywebview.api.<method>()`` in JS.
Methods must be synchronous from Python's perspective; pywebview wraps
them in promises on the JS side automatically.

Return convention: always return a dict with:
  {"ok": true, "data": <payload>}       on success
  {"ok": false, "error": "<message>"}   on failure
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import webview  # type: ignore[import-untyped]
from pydantic import TypeAdapter

from flash_excel.core.models import Preset, PresetMeta, Step
from flash_excel.io.loader import read_csv, read_excel
from flash_excel.io.models import FileLoaderResult
from flash_excel.paths import PRESETS_DIR
from flash_excel.presets import delete_preset, list_presets, load_preset, save_preset

_step_adapter: TypeAdapter[Step] = TypeAdapter(Step)


def _ok(data: Any = None) -> dict:
    return {"ok": True, "data": data}


def _err(message: str) -> dict:
    return {"ok": False, "error": message}


class FlashExcelAPI:
    """Stateful API instance — one per application lifetime."""

    def __init__(self) -> None:
        self._loaded_file: FileLoaderResult | None = None
        self._source_columns: list[str] = []
        self._current_preset_path: Path | None = None
        self._step_payloads: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------

    def get_presets(self) -> dict:
        """Return list of preset metadata dicts."""
        try:
            paths = list_presets(PRESETS_DIR)
            result = []
            for p in paths:
                try:
                    preset = load_preset(p)
                    result.append(
                        {
                            "name": preset.meta.name,
                            "description": preset.meta.description or "",
                            "step_count": len(preset.steps),
                            "path": str(p),
                        }
                    )
                except Exception:  # noqa: S110
                    pass
            return _ok(result)
        except Exception as exc:
            return _err(str(exc))

    def load_preset(self, preset_path: str) -> dict:
        """Load a preset by absolute path and return its full data."""
        try:
            path = Path(preset_path)
            preset = load_preset(path)
            self._current_preset_path = path
            self._step_payloads = {}
            for step in preset.steps:
                step_dict = step.model_dump()
                action = step_dict.pop("action")
                self._step_payloads[action] = {"action": action, **step_dict}
            return _ok(self._preset_to_dict(preset))
        except Exception as exc:
            return _err(str(exc))

    def new_preset(self, name: str) -> dict:
        """Create a fresh empty preset in memory and return its data."""
        try:
            name = name.strip()
            if not name:
                return _err("Preset name cannot be empty")
            preset = Preset(meta=PresetMeta(name=name), steps=[])
            path = PRESETS_DIR / f"{name.lower().replace(' ', '_')}.toml"
            self._current_preset_path = path
            self._step_payloads = {}
            return _ok(self._preset_to_dict(preset))
        except Exception as exc:
            return _err(str(exc))

    def save_preset(self, name: str, steps_payload: list) -> dict:
        """Persist current preset to disk."""
        try:
            if self._current_preset_path is None:
                name = name.strip()
                self._current_preset_path = (
                    PRESETS_DIR / f"{name.lower().replace(' ', '_')}.toml"
                )

            steps: list[Step] = []
            for raw in steps_payload:
                if raw:
                    try:  # noqa: SIM105
                        steps.append(_step_adapter.validate_python(raw))
                    except Exception:  # noqa: S110
                        pass

            preset = Preset(
                meta=PresetMeta(
                    name=name,
                    source_columns=self._source_columns,
                ),
                steps=steps,
            )
            save_preset(preset, self._current_preset_path)
            return _ok({"path": str(self._current_preset_path)})
        except Exception as exc:
            return _err(str(exc))

    def delete_preset(self, preset_path: str) -> dict:
        """Delete a preset file."""
        try:
            path = Path(preset_path)
            delete_preset(path)
            if self._current_preset_path == path:
                self._current_preset_path = None
                self._step_payloads = {}
            return _ok()
        except Exception as exc:
            return _err(str(exc))

    def export_preset(self, preset_path: str) -> dict:
        """Open a save dialog and copy the preset TOML to the chosen location."""
        try:
            src = Path(preset_path)
            if not src.exists():
                return _err("Preset file not found")
            window = webview.active_window()
            if window is None:
                return _err("No active window")
            result = window.create_file_dialog(  # type: ignore[union-attr]
                int(webview.SAVE_DIALOG),
                directory=str(Path.home()),
                save_filename=src.name,
                file_types=("TOML files (*.toml)",),
            )
            if not result:
                return _ok({"cancelled": True})
            dest = Path(
                str(result[0]) if isinstance(result, (list, tuple)) else str(result)
            )
            dest.write_bytes(src.read_bytes())
            return _ok({"dest": str(dest)})
        except Exception as exc:
            return _err(str(exc))

    # ------------------------------------------------------------------
    # File loading
    # ------------------------------------------------------------------

    def open_file_dialog(self) -> dict:
        """Open native file picker and load the selected file."""
        try:
            window = webview.active_window()
            if window is None:
                return _err("No active window")
            result = window.create_file_dialog(  # type: ignore[union-attr]
                int(webview.OPEN_DIALOG),
                allow_multiple=False,
                file_types=("Supported files (*.xlsx *.xls *.xlsm *.csv)",),
            )
            if not result:
                return _ok({"cancelled": True})
            return self._load_file_path(result[0])
        except Exception as exc:
            return _err(str(exc))

    def clear_file(self) -> dict:
        """Unload the current file."""
        self._loaded_file = None
        self._source_columns = []
        return _ok()

    # ------------------------------------------------------------------
    # Step payloads
    # ------------------------------------------------------------------

    def get_step_payload(self, action: str) -> dict:
        """Return the current in-memory payload for a given action."""
        return _ok(self._step_payloads.get(action, {}))

    def set_step_payload(self, action: str, payload: dict) -> dict:
        """Store an edited step payload in memory."""
        if payload:
            self._step_payloads[action] = payload
        else:
            self._step_payloads.pop(action, None)
        return _ok()

    def get_source_columns(self) -> dict:
        """Return the column list of the currently loaded file."""
        return _ok(self._source_columns)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_file_path(self, path_str: str) -> dict:
        try:
            path = Path(path_str)
            result = FileLoaderResult.from_path(path)
            self._loaded_file = result
            df = read_csv(path) if result.file_type == "csv" else read_excel(path)
            self._source_columns = df.columns
            return _ok(
                {
                    "file_name": result.file_name,
                    "size_bytes": result.size_bytes,
                    "file_type": result.file_type,
                    "columns": self._source_columns,
                }
            )
        except Exception as exc:
            return _err(str(exc))

    @staticmethod
    def _preset_to_dict(preset: Preset) -> dict:
        return {
            "name": preset.meta.name,
            "description": preset.meta.description or "",
            "source_columns": preset.meta.source_columns or [],
            "steps": [s.model_dump() for s in preset.steps],
        }
