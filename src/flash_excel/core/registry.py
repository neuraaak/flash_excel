# ///////////////////////////////////////////////////////////////
# REGISTRY - Action registry and decorator for pipeline steps
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Action registry for flash-excel pipeline steps.

Provides the `REGISTRY` dict and the `@action` decorator used to
register pure step functions by their string action name. The
pipeline dispatches to registered callables at runtime.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from collections.abc import Callable
from typing import Any

# Third-party imports
import polars as pl

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Maps action name (str) to the registered step function.
# Functions are registered via the @action("name") decorator.
REGISTRY: dict[str, Callable[..., pl.DataFrame]] = {}

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def action(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that registers a step function in the REGISTRY.

    The decorated function must accept a `pl.DataFrame` as its first
    positional argument and return a `pl.DataFrame`. Any additional
    keyword arguments correspond to step model fields (e.g., `columns`,
    `conditions`).

    Args:
        name: The action identifier string used in TOML presets and
            Pydantic step models (e.g., ``"drop_columns"``).

    Returns:
        Callable: The original function, unchanged, with a side-effect
            of registering it under ``name`` in `REGISTRY`.

    Raises:
        ValueError: If ``name`` is already registered, preventing
            accidental overwrites from duplicate definitions.

    Example:
        >>> @action("my_step")
        ... def my_step(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
        ...     return df.drop(columns)
        >>> "my_step" in REGISTRY
        True
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if name in REGISTRY:
            raise ValueError(
                f"Action '{name}' is already registered. "
                "Each action name must be unique across all step modules."
            )
        REGISTRY[name] = fn
        return fn

    return decorator


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "REGISTRY",
    "action",
]
