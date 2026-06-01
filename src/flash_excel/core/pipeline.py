# ///////////////////////////////////////////////////////////////
# PIPELINE - Orchestrates execution of preset steps
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pipeline orchestrator for flash-excel.

Provides `run_pipeline` to execute all steps of a Preset against a
DataFrame, and `compute_schema_at_step` to derive the list of
available columns at any point in the pipeline (used by the UI to
populate dynamic column dropdowns).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
import polars as pl

# Local imports — steps import must come before REGISTRY usage
# to ensure all @action decorators have been executed.
from flash_excel.core import steps as _steps_module  # noqa: F401
from flash_excel.core.models import (
    AddComputedColumnStep,  # noqa: F401
    DropColumnsStep,
    Preset,
    RenameColumnsStep,  # noqa: F401
    ReorderColumnsStep,
    SelectColumnsStep,  # noqa: F401
    Step,
)
from flash_excel.core.registry import REGISTRY

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def run_pipeline(df: pl.DataFrame, preset: Preset) -> pl.DataFrame:
    """Execute all steps of a preset against a DataFrame.

    Each step is dispatched to its registered function via the
    REGISTRY, passing all model fields (except ``action``) as
    keyword arguments.

    Args:
        df: Input DataFrame produced by the io/loader layer.
        preset: Validated Preset instance (from ``presets/parser``).

    Returns:
        pl.DataFrame: Transformed DataFrame after all steps have run.

    Raises:
        KeyError: If a step's ``action`` has no registered handler.
            This should not occur if all step modules are imported.
        polars.exceptions.ColumnNotFoundError: If a step references a
            column that was already removed by a preceding step.

    Example:
        >>> import polars as pl
        >>> from flash_excel.core.models import Preset, PresetMeta, DropColumnsStep
        >>> df = pl.DataFrame({"a": [1], "b": [2], "tmp": [3]})
        >>> preset = Preset(
        ...     meta=PresetMeta(name="test"),
        ...     steps=[DropColumnsStep(action="drop_columns", columns=["tmp"])],
        ... )
        >>> run_pipeline(df, preset)
        shape: (1, 2)
    """
    result = df
    for step in preset.steps:
        handler = REGISTRY.get(step.action)
        if handler is None:
            raise KeyError(
                f"No registered handler for action '{step.action}'. "
                "Ensure all step modules are imported before running the pipeline."
            )
        # Pass all step fields except 'action' as keyword arguments.
        kwargs = step.model_dump(exclude={"action"})
        result = handler(result, **kwargs)
    return result


def compute_schema_at_step(
    steps: list[Step],
    headers: list[str],
    index: int,
) -> list[str]:
    """Compute the available column names just before a given step index.

    Simulates the effect of all preceding steps on ``headers`` without
    loading actual data. Used by the UI to build context-aware column
    dropdowns: if step 0 drops ``["tmp"]``, step 1's dropdown must not
    offer ``"tmp"``.

    Only steps that structurally change the column set are simulated:
    - ``drop_columns`` removes named columns.
    - ``reorder_columns`` reorders columns (and potentially subsets if
      unlisted columns are relevant, but all remain present).
    - ``filter_rows`` and ``sort_rows`` do not alter the column set.

    Args:
        steps: The full ordered list of steps in the preset.
        headers: The original column names as read from the source file.
        index: The step index for which to compute the available schema.
            Pass ``0`` to get the original headers. Pass ``len(steps)``
            to get the schema after all steps.

    Returns:
        list[str]: Column names available at the given step position.

    Example:
        >>> from flash_excel.core.models import DropColumnsStep
        >>> steps = [DropColumnsStep(action="drop_columns", columns=["tmp"])]
        >>> compute_schema_at_step(steps, ["a", "b", "tmp"], index=1)
        ['a', 'b']
    """
    current_headers = list(headers)

    for step in steps[:index]:
        if isinstance(step, DropColumnsStep):
            # Remove dropped columns from the simulated schema.
            dropped = set(step.columns)
            current_headers = [h for h in current_headers if h not in dropped]

        elif isinstance(step, SelectColumnsStep):
            # Keep only the selected columns in the given order.
            selected = [c for c in step.columns if c in set(current_headers)]
            current_headers = selected

        elif isinstance(step, RenameColumnsStep):
            # Apply the rename mapping to all column names.
            current_headers = [step.mapping.get(h, h) for h in current_headers]

        elif isinstance(step, ReorderColumnsStep):
            # Leading columns come first; remaining follow in original order.
            leading = [c for c in step.columns if c in current_headers]
            remaining = [c for c in current_headers if c not in set(step.columns)]
            current_headers = leading + remaining

        elif isinstance(step, AddComputedColumnStep):
            # Append the computed column if not already present.
            if step.target not in current_headers:
                current_headers = current_headers + [step.target]

        # filter_rows, sort_rows, and other steps leave the column set unchanged.

    return current_headers


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "run_pipeline",
    "compute_schema_at_step",
]
