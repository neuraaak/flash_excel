# ///////////////////////////////////////////////////////////////
# STEPS/COMPUTED - add_computed_column step
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
Pure step function: add_computed_column.

Adds a new column to the DataFrame using an expression evaluated
in a restricted Polars namespace.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
import ast

import polars as pl

# Local imports
from flash_excel.core.registry import action

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


@action("add_computed_column")
def add_computed_column(
    df: pl.DataFrame,
    target: str,
    expression: str,
) -> pl.DataFrame:
    """Add a computed column to the DataFrame.

    Evaluates a Polars expression string in a restricted namespace
    containing ``pl``, ``col``, and ``lit``, plus all column names
    as direct references to ``pl.col(name)``.

    The expression is evaluated and aliased to the target column name.

    This is a pure function: no side effects, no I/O.

    Args:
        df: Input DataFrame.
        target: Name for the new computed column.
        expression: A Polars expression string (e.g.,
            ``"col('first') + col('second')"`` or
            ``"col('salary') * 1.1"``).

    Returns:
        pl.DataFrame: New DataFrame with the computed column added.

    Raises:
        SyntaxError: If the expression string is not valid Python.
        NameError: If the expression references undefined names
            (only ``pl``, ``col``, ``lit``, and column names are available).
        TypeError: If the expression evaluates to a non-Expression object.
        polars.exceptions.ColumnNotFoundError: If a referenced column
            does not exist in ``df``.

    Example:
        >>> import polars as pl
        >>> df = pl.DataFrame({"first": ["Alice"], "last": ["Smith"]})
        >>> add_computed_column(
        ...     df,
        ...     target="full_name",
        ...     expression="pl.concat_str([col('first'), col('last')], separator=' ')"
        ... )
        shape: (1, 3)
    """
    # Prepare a safe namespace for expression evaluation.  We expose only
    # the Polars helpers and a mapping of column names -> pl.col(name).
    namespace: dict = {
        "pl": pl,
        "col": pl.col,
        "lit": pl.lit,
    }

    # Add column references so users can write col('name') or just 'name'.
    for col_name in df.columns:
        namespace[col_name] = pl.col(col_name)

    # Validate the expression AST to prevent dangerous constructs and
    # restrict the set of allowed identifiers and attribute names.
    allowed_names: set[str] = set(namespace.keys())

    class _SafeExprVisitor(ast.NodeVisitor):
        """AST visitor that rejects unsafe nodes and identifiers."""

        _ALLOWED_NODE_TYPES = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.BoolOp,
            ast.Compare,
            ast.Call,
            ast.Name,
            ast.Constant,
            ast.Attribute,
            ast.Subscript,
            ast.List,
            ast.Tuple,
            ast.Dict,
            ast.Set,
            ast.Load,
            ast.keyword,
            ast.IfExp,
        )

        def __init__(self, allowed: set[str]) -> None:
            self.allowed = allowed

        def visit(self, node: ast.AST) -> None:  # type: ignore[override]
            if not isinstance(node, self._ALLOWED_NODE_TYPES):
                raise ValueError(
                    f"Disallowed expression element: {node.__class__.__name__}"
                )
            super().visit(node)

        def visit_Name(self, node: ast.Name) -> None:  # type: ignore[override]
            if node.id not in self.allowed:
                raise NameError(
                    f"Use of name '{node.id}' is not allowed in expressions"
                )

        def visit_Attribute(self, node: ast.Attribute) -> None:  # type: ignore[override]
            # Disallow access to private/dunder attributes (eg. __class__)
            if node.attr.startswith("_"):
                raise ValueError(f"Access to attribute '{node.attr}' is forbidden")
            # Recursively validate the value (base) of the attribute.
            self.visit(node.value)

        def visit_Call(self, node: ast.Call) -> None:  # type: ignore[override]
            # Only allow calls where the callee is a Name or an Attribute
            if not isinstance(node.func, (ast.Name, ast.Attribute)):
                raise ValueError("Calls to lambda/complex expressions are not allowed")
            # Keyword names must not be private/dunder
            for kw in node.keywords:
                if kw.arg and kw.arg.startswith("_"):
                    raise ValueError(f"Keyword '{kw.arg}' is forbidden in expressions")
            # Continue validation for nested nodes
            self.generic_visit(node)

    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression syntax: {exc}") from exc

    try:
        _SafeExprVisitor(allowed_names).visit(parsed)
    except Exception as exc:
        raise ValueError(f"Unsafe or unsupported expression: {exc}") from exc

    # Compile and evaluate the validated AST in the restricted namespace.
    try:
        code_obj = compile(parsed, "<add_computed_column>", "eval")
        expr = eval(code_obj, {"__builtins__": {}}, namespace)  # noqa: S307
    except Exception as exc:
        raise ValueError(
            f"Failed to evaluate add_computed_column expression: {exc}"
        ) from exc

    # Ensure the result is a Polars expression.
    if not isinstance(expr, pl.Expr):
        raise TypeError(
            f"Expression must evaluate to a Polars Expr, got {type(expr).__name__}"
        )

    # Add the computed column with the target alias.
    return df.with_columns(expr.alias(target))


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["add_computed_column"]
