# ///////////////////////////////////////////////////////////////
# ACTION STEPS - Step list + stacked editor panel
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""Action steps widget used in Presets step-2 section.

Layout:
- Left: vertical list of steps.
- Right: stacked pages, one page per selected step.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
from ezqt_app.services.settings import get_settings_service
from ezqt_app.shared.resources import Icons
from ezqt_widgets import IconButton, ThemeIcon
from PySide6.QtCore import QCoreApplication, QEvent, QSize, Qt
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# Local imports
from flash_excel.ui.widgets.action_table import (
    AddComputedColumnActionWidget,
    CastTypesActionWidget,
    CleanTextActionWidget,
    DeduplicateRowsActionWidget,
    FilterRowsActionWidget,
    RenameColumnsActionWidget,
    ReorderColumnsActionWidget,
    ReplaceValuesActionWidget,
    SelectColumnsActionWidget,
    SortRowsActionWidget,
)


def _resolve_theme_variant() -> str:
    """Return active theme variant expected by ThemeIcon (dark/light)."""
    try:
        raw_theme = str(get_settings_service().gui.THEME).strip().lower()
    except Exception:
        return "dark"
    if raw_theme == "light" or raw_theme.endswith(":light"):
        return "light"
    return "dark"


class _ActionStepListItem(QWidget):
    """List row: title (left) + info icon with tooltip (right)."""

    def __init__(
        self, title: str, description: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setObjectName("presets_actions_step_list_item")
        self.setProperty("active", False)
        self.setMinimumHeight(38)
        self._is_configured = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(8)

        self._status_icon = QLabel()
        self._status_icon.setObjectName("presets_actions_step_status_icon")
        self._status_icon.setFixedSize(14, 14)
        self._status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        variant = _resolve_theme_variant()
        self._dot_on_icon = ThemeIcon.from_source(
            ":/icons/icons/dot_on.svg", theme=variant
        )
        self._dot_off_icon = ThemeIcon.from_source(
            ":/icons/icons/dot_off.svg", theme=variant
        )
        self._apply_dot(configured=False)

        self._title = QLabel(title)
        self._title.setObjectName("presets_actions_step_list_item_title")
        self._title.setProperty("active", False)
        self._title.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        self._count_badge = QLabel()
        self._count_badge.setObjectName("presets_action_count_badge")
        self._count_badge.setVisible(False)
        self._count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._info_btn = IconButton(
            icon=Icons.cil_lightbulb,
            text_visible=False,
            spacing=0,
            icon_size=(14, 14),
        )
        self._info_btn.setObjectName("presets_actions_step_info_btn")
        self._info_btn.setFixedSize(20, 20)
        self._info_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._info_btn.setToolTip(description)
        self._info_btn.setCursor(Qt.CursorShape.WhatsThisCursor)

        layout.addWidget(self._status_icon)
        layout.addWidget(self._title, stretch=1)
        layout.addWidget(self._count_badge)
        layout.addWidget(self._info_btn)

    def _apply_dot(self, configured: bool) -> None:
        """Swap dot pixmap between filled (configured) and ring (empty)."""
        icon = self._dot_on_icon if configured else self._dot_off_icon
        if icon is not None:
            self._status_icon.setPixmap(icon.pixmap(QSize(8, 8)))

    def set_active(self, is_active: bool) -> None:
        """Set visual active state for row title styling."""
        self.setProperty("active", is_active)
        self._title.setProperty("active", is_active)
        self._title.style().unpolish(self._title)
        self._title.style().polish(self._title)

    def set_content(self, title: str, description: str) -> None:
        """Update row content (title + info tooltip)."""
        self._title.setText(title)
        self._info_btn.setToolTip(description)

    def set_count(self, count: int) -> None:
        """Update dot indicator and count badge from configured row count."""
        self._is_configured = count > 0
        self._apply_dot(configured=self._is_configured)
        if count > 0:
            self._count_badge.setText(str(count))
            self._count_badge.setVisible(True)
        else:
            self._count_badge.setVisible(False)

    def apply_theme(self, theme_variant: str | None = None) -> None:
        """Refresh dot icons and info button for the active theme variant."""
        resolved_variant = theme_variant or _resolve_theme_variant()

        if self._dot_on_icon is not None:
            self._dot_on_icon.setTheme(resolved_variant)
        if self._dot_off_icon is not None:
            self._dot_off_icon.setTheme(resolved_variant)
        self._apply_dot(configured=self._is_configured)

        info_setter = getattr(self._info_btn, "setTheme", None)
        if callable(info_setter):
            info_setter(resolved_variant)
        info_updater = getattr(self._info_btn, "update_theme_icon", None)
        if callable(info_updater):
            info_updater()


class ActionStepsWidget(QFrame):
    """Step navigation panel with left list and right stacked pages."""

    _DEFAULT_STEP_SOURCES: tuple[tuple[str, str], ...] = (
        (
            "Rename columns",
            "Configure source-to-target column rename mapping (placeholder).",
        ),
        (
            "Select columns",
            "Configure which columns to keep and in which order (placeholder).",
        ),
        (
            "Cast types",
            "Configure target data types for selected columns (placeholder).",
        ),
        (
            "Replace values",
            "Configure exact value replacement rules per column (placeholder).",
        ),
        (
            "Clean text",
            "Configure text cleanup in one pass (trim spaces + fill nulls with empty string).",
        ),
        (
            "Add computed column",
            "Configure derived column name and expression (placeholder).",
        ),
        (
            "Filter rows",
            "Configure row filtering conditions and logical combine mode (placeholder).",
        ),
        (
            "Deduplicate rows",
            "Configure duplicate detection subset and keep policy (placeholder).",
        ),
        ("Sort rows", "Configure sort keys and direction (placeholder)."),
        ("Reorder columns", "Configure final output column ordering (placeholder)."),
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("presets_actions_section_frame")
        self._base_columns: list[str] = []
        self._base_types: dict[str, str] = {}
        self._rename_editor: RenameColumnsActionWidget | None = None
        self._replace_editor: ReplaceValuesActionWidget | None = None
        self._select_editor: SelectColumnsActionWidget | None = None
        self._cast_editor: CastTypesActionWidget | None = None
        self._clean_editor: CleanTextActionWidget | None = None
        self._computed_editor: AddComputedColumnActionWidget | None = None
        self._filter_editor: FilterRowsActionWidget | None = None
        self._deduplicate_editor: DeduplicateRowsActionWidget | None = None
        self._sort_editor: SortRowsActionWidget | None = None
        self._reorder_editor: ReorderColumnsActionWidget | None = None
        self._filter_values_by_column: dict[str, list[str]] = {}
        self._is_loading_preset_state = False
        self._step_sources: list[tuple[str, str]] = []
        self._step_rows: list[_ActionStepListItem] = []
        self._setup_ui()
        self._add_default_steps()
        self.retranslate_ui()
        self._connect_signals()

    def _tr(self, text: str) -> str:
        """Translate *text* using the shared application context."""
        return QCoreApplication.translate("EzQt_App", text)

    # ------------------------------------------------
    # Setup
    # ------------------------------------------------

    def _setup_ui(self) -> None:
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._left_panel = QFrame()
        self._left_panel.setObjectName("presets_actions_steps_left_panel")
        self._left_panel.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        self._left_panel.setFixedWidth(230)

        left_layout = QVBoxLayout(self._left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self._steps_list = QListWidget()
        self._steps_list.setObjectName("presets_actions_steps_list")
        self._steps_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._steps_list.setSpacing(0)
        self._steps_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._steps_list.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self._steps_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Maximum,
        )

        left_layout.addWidget(self._steps_list)
        left_layout.addStretch(1)

        self._pages_stack = QStackedWidget()
        self._pages_stack.setObjectName("presets_actions_pages_stack")
        self._pages_stack.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self._splitter = QFrame()
        self._splitter.setObjectName("presets_actions_steps_splitter")
        self._splitter.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        self._splitter.setFixedWidth(1)

        root.addWidget(self._left_panel)
        root.addWidget(self._splitter)
        root.addWidget(self._pages_stack, stretch=1)

    def _add_default_steps(self) -> None:
        for title_source, description_source in self._DEFAULT_STEP_SOURCES:
            self.add_step(title_source, description_source)

        if self._steps_list.count() > 0:
            self._steps_list.setCurrentRow(0)
            self._refresh_active_step(0)

    def _connect_signals(self) -> None:
        self._steps_list.currentRowChanged.connect(self._on_step_changed)

    # ------------------------------------------------
    # Public API
    # ------------------------------------------------

    def add_step(self, title: str, description: str) -> None:
        """Add a navigable step with a basic placeholder page."""
        item = QListWidgetItem()
        row_widget = _ActionStepListItem(self._tr(title), self._tr(description))
        item.setSizeHint(QSize(0, 42))
        self._steps_list.addItem(item)
        self._steps_list.setItemWidget(item, row_widget)
        self._step_sources.append((title, description))
        self._step_rows.append(row_widget)

        page = QWidget()
        page.setObjectName("presets_actions_step_page")
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(10, 10, 10, 10)
        page_layout.setSpacing(6)

        editor = self._build_editor_for_step(title)
        if editor is not None:
            page_layout.addWidget(self._wrap_editor_widget(title, editor), stretch=1)

        self._pages_stack.addWidget(page)

    def _wrap_editor_widget(self, title_source: str, editor: QWidget) -> QWidget:
        """Wrap large editors when needed to keep the step page usable."""
        if title_source not in {"Add computed column", "Filter rows"}:
            return editor

        scroll = QScrollArea()
        scroll.setObjectName("presets_actions_step_scroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(editor)
        return scroll

    # ------------------------------------------------
    # Slots
    # ------------------------------------------------

    def _on_step_changed(self, row: int) -> None:
        if row < 0 or row >= self._pages_stack.count():
            return
        self._refresh_active_step(row)
        self._pages_stack.setCurrentIndex(row)

    def _refresh_active_step(self, active_row: int) -> None:
        """Sync active state so QSS can style row title color."""
        count = self._steps_list.count()
        for idx in range(count):
            item = self._steps_list.item(idx)
            widget = self._steps_list.itemWidget(item)
            if widget is None or not isinstance(widget, _ActionStepListItem):
                continue
            widget.set_active(idx == active_row)

    def _build_editor_for_step(self, title_source: str) -> QWidget | None:
        """Build the concrete action editor bound to a given step title."""
        if title_source == "Rename columns":
            self._rename_editor = RenameColumnsActionWidget()
            self._rename_editor.result_changed.connect(self._on_rename_result_changed)
            self._rename_editor.set_source_columns(self._base_columns)
            return self._rename_editor

        if title_source == "Select columns":
            self._select_editor = SelectColumnsActionWidget()
            self._select_editor.result_changed.connect(self._on_select_result_changed)
            self._select_editor.set_source_columns(self._base_columns)
            return self._select_editor

        if title_source == "Replace values":
            self._replace_editor = ReplaceValuesActionWidget()
            self._replace_editor.result_changed.connect(self._on_replace_result_changed)
            self._replace_editor.set_source_columns(self._base_columns)
            return self._replace_editor

        if title_source == "Cast types":
            self._cast_editor = CastTypesActionWidget()
            self._cast_editor.result_changed.connect(self._on_cast_result_changed)
            self._cast_editor.set_source_columns(
                columns=self._base_columns,
                current_to_base={name: name for name in self._base_columns},
                base_types=self._base_types,
            )
            return self._cast_editor

        if title_source == "Clean text":
            self._clean_editor = CleanTextActionWidget()
            self._clean_editor.result_changed.connect(self._on_clean_result_changed)
            self._clean_editor.set_source_columns([])
            return self._clean_editor

        if title_source == "Add computed column":
            self._computed_editor = AddComputedColumnActionWidget()
            self._computed_editor.result_changed.connect(
                self._on_computed_result_changed
            )
            self._computed_editor.set_source_columns([])
            return self._computed_editor

        if title_source == "Filter rows":
            self._filter_editor = FilterRowsActionWidget()
            self._filter_editor.result_changed.connect(self._on_filter_result_changed)
            self._filter_editor.set_source_columns([])
            return self._filter_editor

        if title_source == "Deduplicate rows":
            self._deduplicate_editor = DeduplicateRowsActionWidget()
            self._deduplicate_editor.result_changed.connect(
                self._on_deduplicate_result_changed
            )
            self._deduplicate_editor.set_source_columns([])
            return self._deduplicate_editor

        if title_source == "Sort rows":
            self._sort_editor = SortRowsActionWidget()
            self._sort_editor.result_changed.connect(self._on_sort_result_changed)
            self._sort_editor.set_source_columns([])
            return self._sort_editor

        if title_source == "Reorder columns":
            self._reorder_editor = ReorderColumnsActionWidget()
            self._reorder_editor.set_source_columns([])
            return self._reorder_editor

        return None

    def _on_rename_result_changed(self) -> None:
        """Propagate rename result columns to next-step select editor."""
        if self._is_loading_preset_state:
            return
        if self._rename_editor is None or self._select_editor is None:
            return

        rename_result = self._rename_editor.get_result_model()
        self._select_editor.set_source_columns(rename_result.resulting_columns)
        self._propagate_to_cast()
        self._refresh_step_badges()

    def _on_select_result_changed(self) -> None:
        """Propagate selected columns to cast editor."""
        if self._is_loading_preset_state:
            return
        self._propagate_to_cast()
        self._refresh_step_badges()

    def _on_cast_result_changed(self) -> None:
        """Propagate cast updates downstream."""
        if self._is_loading_preset_state:
            return
        self._propagate_to_replace()
        self._propagate_to_clean()
        self._refresh_step_badges()

    def _on_replace_result_changed(self) -> None:
        """Propagate replace-values output downstream."""
        if self._is_loading_preset_state:
            return
        self._propagate_to_clean()
        self._refresh_step_badges()

    def _on_clean_result_changed(self) -> None:
        """Propagate clean stage output to computed-column editor."""
        if self._is_loading_preset_state:
            return
        self._propagate_to_computed()
        self._refresh_step_badges()

    def _on_computed_result_changed(self) -> None:
        """Propagate computed stage output to filter editor."""
        if self._is_loading_preset_state:
            return
        self._propagate_to_filter()
        self._refresh_step_badges()

    def _on_filter_result_changed(self) -> None:
        """Propagate filter stage output to deduplicate editor."""
        if self._is_loading_preset_state:
            return
        self._propagate_to_deduplicate()
        self._refresh_step_badges()

    def _on_deduplicate_result_changed(self) -> None:
        """Propagate deduplicate stage output to sort editor."""
        if self._is_loading_preset_state:
            return
        self._propagate_to_sort()
        self._refresh_step_badges()

    def _on_sort_result_changed(self) -> None:
        """Propagate sort stage output to reorder editor."""
        if self._is_loading_preset_state:
            return
        self._propagate_to_reorder()
        self._refresh_step_badges()

    def _propagate_to_cast(self) -> None:
        """Build lineage and propagate available columns to cast action."""
        if self._cast_editor is None:
            return

        rename_mapping: dict[str, str] = {}
        renamed_columns = list(self._base_columns)
        if self._rename_editor is not None:
            rename_result = self._rename_editor.get_result_model()
            rename_mapping = dict(rename_result.mapping)
            renamed_columns = list(rename_result.resulting_columns)

        selected_columns = list(renamed_columns)
        if self._select_editor is not None:
            selected_columns = self._select_editor.get_result_model().selected_columns

        current_to_base: dict[str, str] = {
            rename_mapping.get(base_name, base_name): base_name
            for base_name in self._base_columns
        }

        self._cast_editor.set_source_columns(
            columns=selected_columns,
            current_to_base=current_to_base,
            base_types=self._base_types,
        )
        self._propagate_to_replace()
        self._propagate_to_clean()
        self._propagate_to_computed()
        self._propagate_to_filter()

    def _propagate_to_replace(self) -> None:
        """Propagate cast output columns to replace-values editor."""
        if self._replace_editor is None:
            return

        self._replace_editor.set_source_columns(self._selected_columns_after_select())

    def _propagate_to_clean(self) -> None:
        """Expose only string-compatible columns from replace output to clean."""
        if self._clean_editor is None:
            return

        rename_mapping: dict[str, str] = {}
        if self._rename_editor is not None:
            rename_result = self._rename_editor.get_result_model()
            rename_mapping = dict(rename_result.mapping)

        # n -> n+1 flow: Clean is sourced from Replace-values output.
        replace_output_columns = self._replace_output_columns()

        current_to_base: dict[str, str] = {
            rename_mapping.get(base_name, base_name): base_name
            for base_name in self._base_columns
        }

        cast_overrides: dict[str, str] = {}
        if self._cast_editor is not None:
            cast_overrides = dict(self._cast_editor.get_result_model().casts)

        compatible_columns: list[str] = []
        for current_name in replace_output_columns:
            if current_name in cast_overrides:
                if cast_overrides[current_name] == "string":
                    compatible_columns.append(current_name)
                # Explicit cast overrides always win over base type.
                continue

            base_name = current_to_base.get(current_name, current_name)
            base_dtype = self._base_types.get(base_name, "Unknown")
            logical_dtype = self._normalize_polars_dtype(base_dtype)
            if logical_dtype == "string":
                compatible_columns.append(current_name)

        existing_selected = set(self._clean_editor.get_selected_columns())
        retained_selection = [
            name for name in compatible_columns if name in existing_selected
        ]
        self._clean_editor.set_source_columns(
            compatible_columns,
            selected_columns=retained_selection or compatible_columns,
        )
        self._propagate_to_computed()

    def _propagate_to_computed(self) -> None:
        """Propagate available columns after clean stage to computed builder."""
        if self._computed_editor is None:
            return

        rename_mapping: dict[str, str] = {}
        if self._rename_editor is not None:
            rename_result = self._rename_editor.get_result_model()
            rename_mapping = dict(rename_result.mapping)

        current_to_base: dict[str, str] = {
            rename_mapping.get(base_name, base_name): base_name
            for base_name in self._base_columns
        }

        cast_overrides: dict[str, str] = {}
        if self._cast_editor is not None:
            cast_overrides = dict(self._cast_editor.get_result_model().casts)

        replace_output_columns = self._replace_output_columns()
        logical_types: dict[str, str] = {}
        for current_name in replace_output_columns:
            if current_name in cast_overrides:
                logical_types[current_name] = cast_overrides[current_name]
                continue

            base_name = current_to_base.get(current_name, current_name)
            base_dtype = self._base_types.get(base_name, "Unknown")
            logical_types[current_name] = self._normalize_polars_dtype(base_dtype)

        self._computed_editor.set_source_columns(
            replace_output_columns,
            logical_types=logical_types,
        )
        self._propagate_to_filter()

    def _propagate_to_filter(self) -> None:
        """Propagate columns after computed stage to filter builder."""
        if self._filter_editor is None:
            return

        filter_columns = self._computed_output_columns()
        self._filter_editor.set_source_columns(filter_columns)
        self._filter_editor.set_column_values(
            {
                name: list(self._filter_values_by_column.get(name, []))
                for name in filter_columns
            }
        )
        self._propagate_to_deduplicate()

    def _propagate_to_deduplicate(self) -> None:
        """Propagate columns after filter stage to deduplicate builder."""
        if self._deduplicate_editor is None:
            return

        self._deduplicate_editor.set_source_columns(self._filter_output_columns())
        self._propagate_to_sort()

    def _propagate_to_sort(self) -> None:
        """Propagate columns after deduplicate stage to sort builder."""
        if self._sort_editor is None:
            return

        self._sort_editor.set_source_columns(self._deduplicate_output_columns())
        self._propagate_to_reorder()

    def _propagate_to_reorder(self) -> None:
        """Propagate columns after sort stage to reorder builder."""
        if self._reorder_editor is None:
            return

        self._reorder_editor.set_source_columns(self._deduplicate_output_columns())

    def _computed_output_columns(self) -> list[str]:
        """Return ordered columns output by computed stage."""
        columns = list(self._replace_output_columns())
        if self._computed_editor is None:
            return columns

        result = self._computed_editor.get_result_model()
        target = result.target.strip()
        if target and target not in columns:
            columns.append(target)
        return columns

    def _filter_output_columns(self) -> list[str]:
        """Return ordered columns output by filter stage.

        Filter rows does not alter schema, only row set.
        """
        return self._computed_output_columns()

    def _deduplicate_output_columns(self) -> list[str]:
        """Return ordered columns output by deduplicate stage.

        Deduplicate rows does not alter schema, only row set.
        """
        return self._filter_output_columns()

    @staticmethod
    def _normalize_polars_dtype(dtype_name: str) -> str:
        """Map a Polars dtype name to a logical cast family."""
        lower_name = dtype_name.lower()

        if lower_name.startswith(("int", "uint")):
            return "int"
        if lower_name.startswith("float"):
            return "float"
        if lower_name in {"bool", "boolean"}:
            return "bool"
        if lower_name.startswith("date"):
            return "date"
        if lower_name.startswith(("datetime", "time")):
            return "datetime"
        if lower_name in {"str", "string", "utf8", "categorical"}:
            return "string"
        return "unknown"

    def _selected_columns_after_select(self) -> list[str]:
        """Return ordered columns after rename/select stages."""
        rename_resulting_columns = list(self._base_columns)
        if self._rename_editor is not None:
            rename_resulting_columns = list(
                self._rename_editor.get_result_model().resulting_columns
            )

        selected_columns = list(rename_resulting_columns)
        if self._select_editor is not None:
            selected_columns = self._select_editor.get_result_model().selected_columns
        return selected_columns

    def _replace_output_columns(self) -> list[str]:
        """Return ordered columns output by replace-values stage.

        Replace-values currently does not alter schema, so output columns
        equal input columns. We still keep this helper to enforce clear
        n->n+1 chaining semantics.
        """
        if self._replace_editor is None:
            return self._selected_columns_after_select()
        return list(self._replace_editor.get_values().keys())

    def _get_step_row_count(self, step_name: str) -> int:
        """Return the configured row count for a given step (by source title)."""
        if step_name == "Rename columns" and self._rename_editor is not None:
            payload = self._rename_editor.get_step_payload()
            mapping = payload.get("mapping", {})
            return len(mapping) if isinstance(mapping, dict) else 0

        if step_name == "Select columns" and self._select_editor is not None:
            payload = self._select_editor.get_step_payload()
            columns = payload.get("columns", [])
            return len(columns) if isinstance(columns, list) else 0

        if step_name == "Cast types" and self._cast_editor is not None:
            payload = self._cast_editor.get_step_payload()
            casts = payload.get("casts", {})
            return len(casts) if isinstance(casts, dict) else 0

        if step_name == "Replace values" and self._replace_editor is not None:
            return len(self._replace_editor.get_step_payloads())

        if step_name == "Clean text" and self._clean_editor is not None:
            return len(self._clean_editor.get_step_payloads())

        if step_name == "Add computed column" and self._computed_editor is not None:
            return 1 if self._computed_editor.get_step_payload() is not None else 0

        if step_name == "Filter rows" and self._filter_editor is not None:
            payload = self._filter_editor.get_step_payload()
            if payload is None:
                return 0
            conditions = payload.get("conditions", [])
            return len(conditions) if isinstance(conditions, list) else 1

        if step_name == "Deduplicate rows" and self._deduplicate_editor is not None:
            payload = self._deduplicate_editor.get_step_payload()
            subset = payload.get("subset", [])
            keep = payload.get("keep", "first")
            if isinstance(subset, list) and subset:
                return len(subset)
            return 1 if keep in {"last", "none"} else 0

        if step_name == "Sort rows" and self._sort_editor is not None:
            payload = self._sort_editor.get_step_payload()
            if payload is None:
                return 0
            by = payload.get("by", [])
            return len(by) if isinstance(by, list) else 0

        if step_name == "Reorder columns" and self._reorder_editor is not None:
            payload = self._reorder_editor.get_step_payload()
            if payload is None:
                return 0
            columns = payload.get("columns", [])
            return len(columns) if isinstance(columns, list) else 0

        return 0

    def _refresh_step_badges(self) -> None:
        """Update dot + count badge for every step row from live editor data."""
        for idx, (step_name, _) in enumerate(self._step_sources):
            if idx >= len(self._step_rows):
                break
            count = self._get_step_row_count(step_name)
            self._step_rows[idx].set_count(count)

    def set_available_columns(
        self,
        columns: list[str],
        base_types: dict[str, str] | None = None,
    ) -> None:
        """Set the base columns context used by action-table editors."""
        seen: set[str] = set()
        ordered_unique_columns: list[str] = []
        for name in columns:
            if name in seen:
                continue
            seen.add(name)
            ordered_unique_columns.append(name)

        self._base_columns = ordered_unique_columns
        self._base_types = dict(base_types or {})

        if self._rename_editor is not None:
            self._rename_editor.set_source_columns(self._base_columns)
        if self._select_editor is not None:
            if self._rename_editor is None:
                self._select_editor.set_source_columns(self._base_columns)
            else:
                self._on_rename_result_changed()
        elif self._cast_editor is not None:
            self._propagate_to_cast()
        if self._replace_editor is not None:
            self._propagate_to_replace()
        if self._cast_editor is not None:
            self._propagate_to_cast()
        if self._clean_editor is not None:
            self._propagate_to_clean()
        if self._computed_editor is not None:
            self._propagate_to_computed()
        if self._filter_editor is not None:
            self._propagate_to_filter()
        if self._deduplicate_editor is not None:
            self._propagate_to_deduplicate()
        if self._sort_editor is not None:
            self._propagate_to_sort()
        if self._reorder_editor is not None:
            self._propagate_to_reorder()

    def get_available_columns(self) -> list[str]:
        """Return cached source columns currently used by step editors."""
        return list(self._base_columns)

    def get_available_types(self) -> dict[str, str]:
        """Return cached source schema currently used by step editors."""
        return dict(self._base_types)

    def collect_step_payloads(self) -> list[dict[str, object]]:
        """Collect configured action payloads in pipeline execution order.

        Returns:
            list[dict[str, object]]: Payloads ready to instantiate
                ``Preset.steps`` via Pydantic discriminated union parsing.
        """
        payloads: list[dict[str, object]] = []

        if self._rename_editor is not None:
            rename_payload = self._rename_editor.get_step_payload()
            mapping = rename_payload.get("mapping")
            if isinstance(mapping, dict) and mapping:
                payloads.append(rename_payload)

        if self._select_editor is not None:
            select_payload = self._select_editor.get_step_payload()
            columns = select_payload.get("columns")
            if isinstance(columns, list) and columns:
                payloads.append(select_payload)

        if self._cast_editor is not None:
            cast_payload = self._cast_editor.get_step_payload()
            casts = cast_payload.get("casts")
            if isinstance(casts, dict) and casts:
                payloads.append(cast_payload)

        if self._replace_editor is not None:
            payloads.extend(self._replace_editor.get_step_payloads())

        if self._clean_editor is not None:
            payloads.extend(self._clean_editor.get_step_payloads())

        if self._computed_editor is not None:
            computed_payload = self._computed_editor.get_step_payload()
            if computed_payload is not None:
                payloads.append(computed_payload)

        if self._filter_editor is not None:
            filter_payload = self._filter_editor.get_step_payload()
            if filter_payload is not None:
                payloads.append(filter_payload)

        if self._deduplicate_editor is not None:
            dedup_payload = self._deduplicate_editor.get_step_payload()
            subset = dedup_payload.get("subset")
            keep = dedup_payload.get("keep")
            if (isinstance(subset, list) and subset) or keep in {"last", "none"}:
                payloads.append(dedup_payload)

        if self._sort_editor is not None:
            sort_payload = self._sort_editor.get_step_payload()
            if sort_payload is not None:
                payloads.append(sort_payload)

        if self._reorder_editor is not None:
            reorder_payload = self._reorder_editor.get_step_payload()
            if reorder_payload is not None:
                payloads.append(reorder_payload)

        return payloads

    def load_step_payloads(self, steps: list[dict[str, object]]) -> None:
        """Replay saved preset steps into all action editors."""
        self._is_loading_preset_state = True
        try:
            rename_mapping: dict[str, str] = {}
            select_columns: list[str] | None = None
            cast_overrides: dict[str, str] = {}
            replace_rules_by_column: dict[str, str] = {}
            clean_columns: list[str] | None = None
            computed_target = ""
            computed_expression = ""
            filter_combine = "AND"
            filter_conditions: list[dict[str, object]] = []
            dedup_subset: list[str] = []
            dedup_keep = "first"
            sort_by: list[str] = []
            sort_descending_map: dict[str, bool] = {}
            reorder_columns: list[str] | None = None

            for step in steps:
                action = step.get("action")
                if not isinstance(action, str):
                    continue

                if action == "rename_columns":
                    mapping = step.get("mapping")
                    if isinstance(mapping, dict):
                        rename_mapping = {
                            str(src): str(dst)
                            for src, dst in mapping.items()
                            if isinstance(src, str) and isinstance(dst, str)
                        }
                elif action == "select_columns":
                    columns = step.get("columns")
                    if isinstance(columns, list):
                        select_columns = [str(name) for name in columns]
                elif action == "cast_types":
                    casts = step.get("casts")
                    if isinstance(casts, dict):
                        cast_overrides = {
                            str(col): str(dtype)
                            for col, dtype in casts.items()
                            if isinstance(col, str) and isinstance(dtype, str)
                        }
                elif action == "replace_values":
                    column = step.get("column")
                    mapping = step.get("mapping")
                    if not isinstance(column, str) or not isinstance(mapping, dict):
                        continue
                    serialized_pairs = [
                        f"{old}=>{'' if new is None else new}"
                        for old, new in mapping.items()
                    ]
                    replace_rules_by_column[column] = "; ".join(serialized_pairs)
                elif action == "trim_whitespace":
                    columns = step.get("columns")
                    if isinstance(columns, list):
                        clean_columns = [str(name) for name in columns]
                elif action == "fill_nulls":
                    value = step.get("value")
                    strategy = step.get("strategy")
                    columns = step.get("columns")
                    if (
                        strategy == "value"
                        and value == ""
                        and isinstance(columns, list)
                    ):
                        clean_columns = [str(name) for name in columns]
                elif action == "add_computed_column":
                    target = step.get("target")
                    expression = step.get("expression")
                    if isinstance(target, str) and isinstance(expression, str):
                        computed_target = target
                        computed_expression = expression
                elif action == "filter_rows":
                    combine = step.get("combine")
                    conditions = step.get("conditions")
                    if isinstance(combine, str):
                        filter_combine = combine
                    if isinstance(conditions, list):
                        filter_conditions = []
                        for condition in conditions:
                            if not isinstance(condition, dict):
                                continue
                            normalized_condition: dict[str, object] = {
                                str(key): value for key, value in condition.items()
                            }
                            filter_conditions.append(normalized_condition)
                elif action == "deduplicate_rows":
                    subset = step.get("subset")
                    keep = step.get("keep")
                    if isinstance(subset, list):
                        dedup_subset = [str(name) for name in subset]
                    if isinstance(keep, str):
                        dedup_keep = keep
                elif action == "sort_rows":
                    by = step.get("by")
                    descending = step.get("descending")
                    if isinstance(by, list):
                        sort_by = [str(name) for name in by]
                    if isinstance(descending, list):
                        sort_descending_map = {
                            str(name): bool(desc)
                            for name, desc in zip(sort_by, descending, strict=False)
                        }
                    elif isinstance(descending, bool):
                        sort_descending_map = dict.fromkeys(sort_by, descending)
                elif action == "reorder_columns":
                    columns = step.get("columns")
                    if isinstance(columns, list):
                        reorder_columns = [str(name) for name in columns]

            if self._rename_editor is not None:
                self._rename_editor.set_source_columns(
                    self._base_columns,
                    value_overrides=rename_mapping,
                )

            renamed_columns = list(self._base_columns)
            if self._rename_editor is not None:
                renamed_columns = (
                    self._rename_editor.get_result_model().resulting_columns
                )

            if self._select_editor is not None:
                self._select_editor.set_source_columns(
                    renamed_columns,
                    selected_columns=select_columns,
                )

            self._propagate_to_cast()

            if self._cast_editor is not None:
                rename_mapping_for_cast: dict[str, str] = {}
                if self._rename_editor is not None:
                    rename_mapping_for_cast = dict(
                        self._rename_editor.get_result_model().mapping
                    )
                current_to_base = {
                    rename_mapping_for_cast.get(base_name, base_name): base_name
                    for base_name in self._base_columns
                }
                self._cast_editor.set_source_columns(
                    columns=self._selected_columns_after_select(),
                    current_to_base=current_to_base,
                    base_types=self._base_types,
                    cast_overrides=cast_overrides,
                )

            self._propagate_to_replace()
            if self._replace_editor is not None:
                self._replace_editor.set_source_columns(
                    self._selected_columns_after_select(),
                    value_overrides=replace_rules_by_column,
                )

            self._propagate_to_clean()
            if self._clean_editor is not None and clean_columns is not None:
                compatible_columns = self._clean_editor.get_source_columns()
                retained_selection = [
                    name for name in clean_columns if name in compatible_columns
                ]
                self._clean_editor.set_source_columns(
                    compatible_columns,
                    selected_columns=retained_selection,
                )

            self._propagate_to_computed()
            if (
                self._computed_editor is not None
                and computed_target
                and computed_expression
            ):
                self._computed_editor.set_state(computed_target, computed_expression)

            self._propagate_to_filter()
            if self._filter_editor is not None and filter_conditions:
                self._filter_editor.set_state(filter_combine, filter_conditions)

            self._propagate_to_deduplicate()
            if self._deduplicate_editor is not None:
                self._deduplicate_editor.set_state(dedup_subset, dedup_keep)

            self._propagate_to_sort()
            if self._sort_editor is not None:
                self._sort_editor.set_source_columns(self._deduplicate_output_columns())
                self._sort_editor.set_state(sort_by, sort_descending_map)

            self._propagate_to_reorder()
            if self._reorder_editor is not None and reorder_columns is not None:
                self._reorder_editor.set_source_columns(
                    self._deduplicate_output_columns(),
                    ordered_columns=reorder_columns,
                )
        finally:
            self._is_loading_preset_state = False

        self._refresh_step_badges()

    def set_filter_values(self, values_by_column: dict[str, list[str]]) -> None:
        """Set optional unique-values context used by filter quick mode."""
        self._filter_values_by_column = {
            column: list(values) for column, values in values_by_column.items()
        }
        if self._filter_editor is not None:
            self._propagate_to_filter()

    def retranslate_ui(self) -> None:
        """Apply current language to all step labels and page descriptions."""
        for idx, (title_source, description_source) in enumerate(self._step_sources):
            title = self._tr(title_source)
            description = self._tr(description_source)

            if idx < len(self._step_rows):
                self._step_rows[idx].set_content(title, description)

        # Force retranslation of instantiated editors so nested widgets
        # (headers/placeholders/combo labels) are refreshed reliably.
        editors: tuple[QWidget | None, ...] = (
            self._rename_editor,
            self._select_editor,
            self._cast_editor,
            self._replace_editor,
            self._clean_editor,
            self._computed_editor,
            self._filter_editor,
            self._deduplicate_editor,
            self._sort_editor,
            self._reorder_editor,
        )
        for editor in editors:
            if editor is None:
                continue
            retranslate = getattr(editor, "retranslate_ui", None)
            if callable(retranslate):
                retranslate()

    def apply_theme(self, theme_variant: str | None = None) -> None:
        """Refresh all theme-aware icons in list rows and action editors."""
        resolved_variant = theme_variant or _resolve_theme_variant()

        for row in self._step_rows:
            row.apply_theme(resolved_variant)

        editors: tuple[QWidget | None, ...] = (
            self._rename_editor,
            self._select_editor,
            self._cast_editor,
            self._replace_editor,
            self._clean_editor,
            self._computed_editor,
            self._filter_editor,
            self._deduplicate_editor,
            self._sort_editor,
            self._reorder_editor,
        )
        for editor in editors:
            if editor is None:
                continue
            apply_theme = getattr(editor, "apply_theme", None)
            if callable(apply_theme):
                apply_theme(resolved_variant)

        self._apply_theme_to_widget_tree(self, resolved_variant)

    @staticmethod
    def _apply_theme_to_widget_tree(root: QWidget, theme_variant: str) -> None:
        """Apply theme icon refresh hooks on a widget and its descendants."""
        for widget in [root, *root.findChildren(QWidget)]:
            setter = getattr(widget, "setTheme", None)
            if callable(setter):
                setter(theme_variant)
                continue
            updater = getattr(widget, "update_theme_icon", None)
            if callable(updater):
                updater()

    def changeEvent(self, event: QEvent) -> None:
        """Re-apply translations when Qt emits a language-change event."""
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate_ui()
        elif event.type() in {
            QEvent.Type.PaletteChange,
            QEvent.Type.StyleChange,
            QEvent.Type.ThemeChange,
            QEvent.Type.ApplicationPaletteChange,
        }:
            self.apply_theme()
        super().changeEvent(event)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ActionStepsWidget"]
