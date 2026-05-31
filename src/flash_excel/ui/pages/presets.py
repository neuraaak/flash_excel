# ///////////////////////////////////////////////////////////////
# PRESETS - Preset management page
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

"""
PresetsPage — preset creation and management page.

Layout structure::

    ┌─ title row ───────────────────────────────┐
    │  Presets                        [+ icon]   │
    ├─ separator ───────────────────────────────┤
    ├─ content frame (expanding) ───────────────┤
    │ ┌─ left (240px) ─┐ ┌─ right (stretch) ──┐ │
    │ │ preset list     │ │ config area        │ │
    │ │                 │ │ (setup / edit)     │ │
    │ └─────────────────┘ └────────────────────┘ │
    └────────────────────────────────────────────┘

This module intentionally contains no business logic.  All
callbacks are stubs that will delegate to the ``presets`` layer
when implemented.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from pathlib import Path
from typing import Any  # pyright: ignore[reportUnusedImport]

# Third-party imports (stdlib-side)
from ezplog import get_logger

# Third-party imports
from ezqt_app import EzApplication
from ezqt_app.services.settings import get_settings_service
from ezqt_app.shared.resources import Icons
from ezqt_widgets import IconButton
from pydantic import TypeAdapter
from PySide6.QtCore import QCoreApplication, QEvent, QSize, Qt
from PySide6.QtGui import QEnterEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# Local imports
from flash_excel.core.models import Preset, PresetMeta, Step
from flash_excel.io.loader import read_headers, read_schema
from flash_excel.paths import PRESETS_DIR
from flash_excel.presets.parser import load_preset
from flash_excel.presets.store import delete_preset, list_presets, save_preset
from flash_excel.ui.widgets import ActionStepsWidget, FileLoader, PresetListItem

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

_LOG = get_logger(__name__)

_LEFT_PANEL_WIDTH = 240
_RIGHT_PLACEHOLDER = 0
_RIGHT_FORM = 1

# ///////////////////////////////////////////////////////////////
# PRIVATE HELPERS
# ///////////////////////////////////////////////////////////////


class _TintedIconButton(IconButton):
    """IconButton with optional icon tint and text-reveal on hover.

    Args:
        hover_color: CSS hex color applied to the icon on hover.
            ``None`` disables icon tinting.
        reveal_text_on_hover: When ``True`` the text label is hidden at
            rest and shown only while the cursor is over the button,
            producing an expanding-width effect.  The horizontal size
            policy is set to ``Preferred`` automatically so the layout
            accommodates the width change.
        *args / **kwargs: Forwarded to :class:`IconButton`.
    """

    def __init__(
        self,
        *args: Any,
        hover_color: str | None = None,
        reveal_text_on_hover: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self._hover_color = hover_color
        self._reveal_text = reveal_text_on_hover
        if reveal_text_on_hover:
            self.text_visible = False
            # Icon-only width: icon px + left/right layout margins (8+8)
            self._icon_only_width: int = self._icon_size.width() + 16
            self.setFixedWidth(self._icon_only_width)

    def enterEvent(self, event: QEnterEvent) -> None:
        super().enterEvent(event)
        if self._hover_color and self._current_icon:
            self.setIconColor(self._hover_color, opacity=1.0)
        if self._reveal_text:
            full_width = (
                self._icon_only_width
                + self._spacing
                + self._text_label.sizeHint().width()
                + 10
            )
            self.setFixedWidth(full_width)
            self.text_visible = True

    def leaveEvent(self, event: QEvent) -> None:  # type: ignore[override]
        super().leaveEvent(event)
        if self._hover_color and self._current_icon:
            self._icon_label.setPixmap(self._current_icon.pixmap(self._icon_size))
        if self._reveal_text:
            self.text_visible = False
            self.setFixedWidth(self._icon_only_width)


def _name_to_slug(name: str) -> str:
    """Convert a preset name to a safe filesystem slug.

    Strips leading/trailing whitespace, lowercases, replaces any run
    of non-word characters with an underscore, and trims edge
    underscores.  Falls back to ``"preset"`` for empty results.

    Args:
        name: Human-readable preset name.

    Returns:
        str: Lowercase, underscore-separated filename stem.

    Example:
        >>> _name_to_slug("Rapport RH — 2024")
        'rapport_rh_2024'
    """
    slug = re.sub(r"[^\w]+", "_", name.strip().lower()).strip("_")
    return slug or "preset"


def _resolve_theme_variant() -> str:
    """Return active theme variant expected by ThemeIcon-aware widgets."""
    try:
        raw_theme = str(get_settings_service().gui.THEME).strip().lower()
    except Exception:
        return "dark"
    if raw_theme == "light" or raw_theme.endswith(":light"):
        return "light"
    return "dark"


# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class PresetsPage(QWidget):
    """Page for browsing, creating, editing, and deleting presets.

    Two-zone layout:

    - **Left panel** (fixed 240 px) — :class:`QListWidget` listing
      preset names as :class:`~flash_excel.ui.widgets.PresetListItem`
      rich widgets.
    - **Right panel** (expanding) — configuration area that will host
      the setup form for new presets or the editor for existing ones.

    All interactive callbacks are stubs; business logic connecting to
    ``presets.store`` and ``presets.parser`` will be wired in a
    subsequent implementation step.
    """

    # ///////////////////////////////////////////////////////////////
    # INIT
    # ///////////////////////////////////////////////////////////////

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._new_preset_counter = 0
        self._theme_signal_connected = False
        self._setup_ui()
        self.retranslate_ui()
        self._connect_signals()
        self._connect_theme_signal()
        self.apply_theme()
        self._load_presets()

    def _tr(self, text: str) -> str:
        """Translate *text* using the project-wide Qt context."""
        return QCoreApplication.translate("EzQt_App", text)

    # ///////////////////////////////////////////////////////////////
    # SETUP
    # ///////////////////////////////////////////////////////////////

    def _setup_ui(self) -> None:
        """Build the two-row, two-column page layout.

        Structure::

            ┌─ left col (240 px) ──┐  ┌─ right col (stretch) ──────────────┐
            │  Presets      [+]    │  │  [name field]  [Sauvegarder][Suppr] │ ← header row
            ├──────────────────────┴──┴────────────────────────────────────┤ ← separator
            │  [preset list]       │  │  [section A]  [section B]  [section C] │ ← content row
            └──────────────────────┴──┴────────────────────────────────────┘

        The left column is ``_LEFT_PANEL_WIDTH`` wide in both rows so that
        the two zones stay vertically aligned.  The right column expands.
        """
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 12, 18, 12)
        root.setSpacing(0)

        # ------------------------------------------------
        # HEADER ROW — left: title+add  /  right: preset meta (stacked)
        # ------------------------------------------------
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 8)
        header_row.setSpacing(12)

        header_row.addWidget(self._build_left_header())
        header_row.addWidget(self._build_right_header(), stretch=1)

        root.addLayout(header_row)

        # ------------------------------------------------
        # SEPARATOR (full width)
        # ------------------------------------------------
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("presets_separator")
        root.addWidget(separator)
        root.addSpacing(12)

        # ------------------------------------------------
        # CONTENT ROW — left: list  /  right: options (stacked)
        # ------------------------------------------------
        content_row = QHBoxLayout()
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setSpacing(12)

        self._left_panel = self._build_left_panel()
        content_row.addWidget(self._left_panel)

        self._right_panel = self._build_right_panel()
        content_row.addWidget(self._right_panel, stretch=1)

        root.addLayout(content_row, stretch=1)

    # ----------------------------------------------------------------
    # Header — left column (title + add button)
    # ----------------------------------------------------------------

    def _build_left_header(self) -> QWidget:
        """Create the left header column: page title and add button.

        Returns:
            QWidget: Fixed ``_LEFT_PANEL_WIDTH`` px wide.
        """
        container = QWidget()
        container.setObjectName("presets_left_header")
        container.setFixedWidth(_LEFT_PANEL_WIDTH)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._page_title = QLabel(self._tr("Presets"))
        self._page_title.setObjectName("presets_page_title")
        layout.addWidget(self._page_title, stretch=1)

        self._add_button = IconButton(
            icon=Icons.cil_plus,
            text_visible=False,
            spacing=0,
            icon_size=QSize(12, 12),
        )
        self._add_button.setObjectName("presets_add_btn")
        self._add_button.setFixedSize(28, 24)
        self._add_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self._add_button)

        return container

    # ----------------------------------------------------------------
    # Header — right column (preset meta, stacked)
    # ----------------------------------------------------------------

    def _build_right_header(self) -> QStackedWidget:
        """Create the right header column as a stacked widget.

        - **Index 0** (``_RIGHT_PLACEHOLDER``) — empty widget; shown when no
          preset is selected so the header row height stays consistent.
        - **Index 1** (``_RIGHT_FORM``) — name field + save/delete buttons.

        Returns:
            QStackedWidget: Stored as ``_right_header_stack``.
        """
        self._right_header_stack = QStackedWidget()
        self._right_header_stack.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        # Page 0: empty placeholder — keeps header row height stable
        self._right_header_stack.addWidget(QWidget())

        # Page 1: meta row
        meta_widget = QWidget()
        meta_layout = QHBoxLayout(meta_widget)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(8)

        self._name_field = QLineEdit()
        self._name_field.setObjectName("presets_name_field")
        self._name_field.setPlaceholderText(self._tr("Preset name"))
        meta_layout.addWidget(self._name_field, stretch=1)

        action_group = QHBoxLayout()
        action_group.setContentsMargins(0, 0, 0, 0)
        action_group.setSpacing(6)

        self._save_button = _TintedIconButton(
            icon=Icons.cil_save,
            text="Save",
            spacing=6,
            icon_size=QSize(14, 14),
        )
        self._save_button.setObjectName("presets_save_btn")
        self._save_button.setFixedHeight(28)
        self._save_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        action_separator = QFrame()
        action_separator.setFrameShape(QFrame.Shape.VLine)
        action_separator.setObjectName("presets_action_separator")

        self._delete_button = _TintedIconButton(
            icon=Icons.cil_trash,
            text="Delete",
            spacing=6,
            icon_size=QSize(14, 14),
            hover_color="#ffffff",
        )
        self._delete_button.setObjectName("presets_delete_btn")
        self._delete_button.setFixedHeight(28)
        self._delete_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        self._export_button = _TintedIconButton(
            icon=Icons.cil_cloud_upload,
            text="Export",
            spacing=6,
            icon_size=QSize(14, 14),
        )
        self._export_button.setObjectName("presets_export_btn")
        self._export_button.setFixedHeight(28)
        self._export_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        action_group.addWidget(self._save_button)
        action_group.addWidget(action_separator)
        action_group.addWidget(self._delete_button)
        action_group.addWidget(self._export_button)
        meta_layout.addLayout(action_group)

        self._right_header_stack.addWidget(meta_widget)

        self._right_header_stack.setCurrentIndex(_RIGHT_PLACEHOLDER)
        return self._right_header_stack

    # ----------------------------------------------------------------
    # Left panel — preset browser
    # ----------------------------------------------------------------

    def _build_left_panel(self) -> QFrame:
        """Create the left sidebar listing available presets."""
        panel = QFrame()
        panel.setFixedWidth(_LEFT_PANEL_WIDTH)
        panel.setObjectName("presets_left_panel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        self._preset_list = QListWidget()
        self._preset_list.setObjectName("presets_list")
        self._preset_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._preset_list.setSpacing(4)
        layout.addWidget(self._preset_list)

        return panel

    # ----------------------------------------------------------------
    # Right panel — config / editor area
    # ----------------------------------------------------------------

    def _build_right_panel(self) -> QFrame:
        """Create the right content panel (stacked: placeholder | 3 sections).

        Structure::

            ┌─ right panel (QFrame) ─────────────────────────────────┐
            │  QStackedWidget (_right_stack)                          │
            │  ├── [0] placeholder — centred hint label               │
            │  └── [1] sections  — [section A] [section B] [section C]│
            └────────────────────────────────────────────────────────┘

        Starts on the placeholder page.  Switch via
        :meth:`_show_form` / :meth:`_show_placeholder`.
        """
        panel = QFrame()
        panel.setObjectName("presets_right_panel")
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._right_stack = QStackedWidget()
        outer.addWidget(self._right_stack)

        # ---- PAGE 0 : placeholder ----
        placeholder_page = QWidget()
        ph_layout = QVBoxLayout(placeholder_page)
        ph_layout.setContentsMargins(12, 12, 12, 12)

        self._placeholder_label = QLabel(
            self._tr("Select a preset or create a new one")
        )
        self._placeholder_label.setObjectName("presets_right_placeholder")
        self._placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ph_layout.addWidget(self._placeholder_label)

        self._right_stack.addWidget(placeholder_page)  # index _RIGHT_PLACEHOLDER

        # ---- PAGE 1 : Config Area ----
        sections_page = QWidget()
        sections_page_layout = QVBoxLayout(sections_page)
        sections_page_layout.setContentsMargins(12, 12, 12, 0)
        sections_page_layout.setSpacing(16)

        # 1. Row Header
        self._settings_header_title = QLabel(self._tr("Settings"))
        self._settings_header_title.setObjectName("presets_right_header_title")
        sections_page_layout.addWidget(self._settings_header_title)

        step_separator_1 = QFrame()
        step_separator_1.setObjectName("presets_step_separator_1")
        step_separator_1.setFrameShape(QFrame.Shape.HLine)
        sections_page_layout.addWidget(step_separator_1)

        # 2. Step header row (badge + H2 + supported formats tip)
        file_step_row = QHBoxLayout()
        file_step_row.setSpacing(8)

        self._file_step_badge = QLabel("1")
        self._file_step_badge.setObjectName("presets_step_badge")
        self._file_step_badge.setFixedSize(22, 22)
        self._file_step_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._file_step_title = QLabel(self._tr("Load the Excel template"))
        self._file_step_title.setObjectName("presets_file_step_title")

        self._file_hint = QLabel(self._tr("Accepted formats: .xlsx, .xls, .xlsm, .csv"))
        self._file_hint.setObjectName("presets_file_hint")

        file_step_row.addWidget(self._file_step_badge)
        file_step_row.addWidget(self._file_step_title)
        file_step_row.addStretch(1)
        file_step_row.addWidget(self._file_hint)
        sections_page_layout.addLayout(file_step_row)

        # 3. Row File Loading
        file_row = QHBoxLayout()
        file_row.setSpacing(12)

        self._file_loader = FileLoader()
        self._file_loader.setObjectName("presets_file_loader")
        self._file_loader.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        file_row.addWidget(self._file_loader)
        sections_page_layout.addLayout(file_row)

        step_separator_2 = QFrame()
        step_separator_2.setObjectName("presets_step_separator_2")
        step_separator_2.setFrameShape(QFrame.Shape.HLine)
        sections_page_layout.addWidget(step_separator_2)

        # 4. Step 2 title row (badge + title + hint)
        actions_step_row = QHBoxLayout()
        actions_step_row.setSpacing(8)

        self._actions_step_badge = QLabel("2")
        self._actions_step_badge.setObjectName("presets_step_badge")
        self._actions_step_badge.setFixedSize(22, 22)
        self._actions_step_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._actions_step_title = QLabel(self._tr("Action configuration"))
        self._actions_step_title.setObjectName("presets_actions_step_title")

        self._actions_step_hint = QLabel(self._tr("Select an action to configure it"))
        self._actions_step_hint.setObjectName("presets_actions_step_hint")

        actions_step_row.addWidget(self._actions_step_badge)
        actions_step_row.addWidget(self._actions_step_title)
        actions_step_row.addStretch(1)
        actions_step_row.addWidget(self._actions_step_hint)
        sections_page_layout.addLayout(actions_step_row)

        # 5. Step 2 content area (fills remaining width/height)
        self._actions_section_frame = ActionStepsWidget()
        sections_page_layout.addWidget(self._actions_section_frame, stretch=1)

        self._right_stack.addWidget(sections_page)  # index _RIGHT_FORM

        self._right_stack.setCurrentIndex(_RIGHT_PLACEHOLDER)
        return panel

    # ///////////////////////////////////////////////////////////////
    # RIGHT PANEL STATE
    # ///////////////////////////////////////////////////////////////

    def _show_form(self) -> None:
        """Reveal the preset form: meta in header, sections in content."""
        self._right_header_stack.setCurrentIndex(_RIGHT_FORM)
        self._right_stack.setCurrentIndex(_RIGHT_FORM)

    def _show_placeholder(self) -> None:
        """Hide the preset form and restore both placeholder states."""
        self._right_header_stack.setCurrentIndex(_RIGHT_PLACEHOLDER)
        self._right_stack.setCurrentIndex(_RIGHT_PLACEHOLDER)

    # ///////////////////////////////////////////////////////////////
    # SIGNALS
    # ///////////////////////////////////////////////////////////////

    def _connect_signals(self) -> None:
        """Connect Qt signals to their callback slots."""
        self._preset_list.currentItemChanged.connect(self._on_preset_selected)
        self._add_button.clicked.connect(self._on_new_preset)
        self._file_loader.load_requested.connect(self._on_file_load_requested)
        self._file_loader.remove_requested.connect(self._on_file_remove_requested)
        self._save_button.clicked.connect(self._on_save_preset)
        self._delete_button.clicked.connect(self._on_delete_preset)
        self._export_button.clicked.connect(self._on_export_preset)

    def _connect_theme_signal(self) -> None:
        """Subscribe this page to application-level theme updates."""
        if self._theme_signal_connected:
            return
        app_instance = QApplication.instance()
        if not isinstance(app_instance, EzApplication):
            return
        app_instance.themeChanged.connect(self._on_app_theme_changed)
        self._theme_signal_connected = True

    def _on_app_theme_changed(self) -> None:
        """Refresh all theme-aware widgets in this page."""
        self.apply_theme()

    def apply_theme(self, theme_variant: str | None = None) -> None:
        """Apply theme refresh hooks to buttons and nested action editors."""
        resolved_variant = theme_variant or _resolve_theme_variant()
        self._apply_theme_to_widget_tree(self, resolved_variant)
        self._actions_section_frame.apply_theme(resolved_variant)

    @staticmethod
    def _apply_theme_to_widget_tree(root: QWidget, theme_variant: str) -> None:
        """Apply theme icon refresh hooks on a widget and descendants."""
        for widget in [root, *root.findChildren(QWidget)]:
            setter = getattr(widget, "setTheme", None)
            if callable(setter):
                setter(theme_variant)
                continue
            updater = getattr(widget, "update_theme_icon", None)
            if callable(updater):
                updater()

    # ///////////////////////////////////////////////////////////////
    # PRIVATE HELPERS
    # ///////////////////////////////////////////////////////////////

    def _add_preset_to_list(
        self, preset: Preset, file_path: Path | None = None
    ) -> QListWidgetItem:
        """Insert a :class:`PresetListItem` row for *preset*.

        Creates a :class:`QListWidgetItem` with a matching size hint,
        then embeds the rich widget via ``setItemWidget``.

        Args:
            preset: Preset model to display.
            file_path: Path of the backing ``.toml`` file, or ``None``
                for an unsaved new preset.

        Returns:
            QListWidgetItem: The inserted item (for selection/reuse).
        """
        item_widget = PresetListItem(preset)
        item_widget.file_path = file_path

        list_item = QListWidgetItem()
        list_item.setSizeHint(item_widget.sizeHint())

        self._preset_list.addItem(list_item)
        self._preset_list.setItemWidget(list_item, item_widget)
        return list_item

    # ///////////////////////////////////////////////////////////////
    # PRIVATE CALLBACKS
    # ///////////////////////////////////////////////////////////////

    def _load_presets(self) -> None:
        """Scan ``PRESETS_DIR`` and populate the list on startup.

        Iterates over every ``.toml`` file returned by
        :func:`~flash_excel.presets.store.list_presets`, parses each one
        with :func:`~flash_excel.presets.parser.load_preset`, and inserts a
        :class:`PresetListItem` row.  Files that fail to parse are skipped
        with a warning so a single corrupt preset never blocks the UI.
        """
        paths = list_presets(PRESETS_DIR)
        _LOG.debug("Found %d preset(s) in %s", len(paths), PRESETS_DIR)
        for path in paths:
            try:
                preset = load_preset(path)
            except (ValueError, FileNotFoundError) as exc:
                _LOG.warning("Skipping '%s': %s", path.name, exc)
                continue
            self._add_preset_to_list(preset, file_path=path)

    def _on_preset_selected(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        """Load the selected preset into the config area.

        Args:
            current: The newly selected list item (may be None).
            _previous: The previously selected item (unused).
        """
        if current is None:
            return
        item_widget = self._preset_list.itemWidget(current)
        if not isinstance(item_widget, PresetListItem):
            return
        preset = item_widget.preset
        _LOG.debug("Preset selected: %s", preset.meta.name)
        self._name_field.setText(preset.meta.name)
        self._actions_section_frame.set_available_columns(
            preset.meta.source_columns,
            base_types=preset.meta.source_types,
        )
        self._actions_section_frame.set_filter_values({})
        self._actions_section_frame.load_step_payloads(
            [step.model_dump() for step in preset.steps]
        )
        self._show_form()

    def _on_new_preset(self) -> None:
        """Add an unsaved placeholder preset and select it."""
        self._new_preset_counter += 1
        stub = Preset(
            meta=PresetMeta(
                name=f"New Preset {self._new_preset_counter}",
                description="",
            )
        )
        list_item = self._add_preset_to_list(stub)
        self._preset_list.setCurrentItem(list_item)
        self._actions_section_frame.set_available_columns([], base_types={})
        self._actions_section_frame.set_filter_values({})
        self._show_form()
        self._name_field.setFocus()
        _LOG.debug("New preset placeholder created: %s", stub.meta.name)

    def _on_file_load_requested(self) -> None:
        """Handle click on file loader and open a real file dialog."""
        result = self._file_loader.load_from_dialog(self)
        if result is None:
            _LOG.debug("File load cancelled or invalid format")
            return

        try:
            headers = read_headers(result.path)
        except (OSError, ValueError) as exc:
            _LOG.warning("Unable to read source headers from %s: %s", result.path, exc)
            headers = []

        try:
            schema = read_schema(result.path)
        except (OSError, ValueError) as exc:
            _LOG.warning("Unable to read source schema from %s: %s", result.path, exc)
            schema = {}

        self._actions_section_frame.set_available_columns(headers, base_types=schema)

        # Keep loading responsive: do not scan unique values for every column
        # during initial file load. Values are now provided lazily.
        self._actions_section_frame.set_filter_values({})
        _LOG.debug(
            "Loaded source file: %s (%s bytes) with %d header(s) and %d typed column(s) (lazy unique values)",
            result.path,
            result.size_bytes,
            len(headers),
            len(schema),
        )

    def _on_file_remove_requested(self) -> None:
        """Handle click on the file loader delete button (stub)."""
        self._actions_section_frame.set_available_columns([], base_types={})
        self._actions_section_frame.set_filter_values({})
        _LOG.debug("Loaded file removed")

    def _on_save_preset(self) -> None:
        """Persist the current preset to ``bin/presets/`` as a TOML file.

        Reads the name from ``_name_field``, builds a :class:`Preset`
        carrying only the meta (steps added later), computes a slug-based
        filename, and calls :func:`~flash_excel.presets.store.save_preset`.

        If the name changed and the item already had a backing file,
        the old file is removed before writing the new one.
        """
        current = self._preset_list.currentItem()
        if current is None:
            return
        item_widget = self._preset_list.itemWidget(current)
        if not isinstance(item_widget, PresetListItem):
            return

        name = self._name_field.text().strip()
        if not name:
            return

        step_adapter = TypeAdapter(list[Step])
        typed_steps = step_adapter.validate_python(
            self._actions_section_frame.collect_step_payloads()
        )
        source_columns = self._actions_section_frame.get_available_columns()
        source_types = self._actions_section_frame.get_available_types()

        preset = Preset(
            meta=PresetMeta(
                name=name,
                description=item_widget.preset.meta.description,
                csv_separator=item_widget.preset.meta.csv_separator,
                csv_encoding=item_widget.preset.meta.csv_encoding,
                source_columns=source_columns,
                source_types=source_types,
            ),
            steps=typed_steps,
        )

        new_path = PRESETS_DIR / f"{_name_to_slug(name)}.toml"
        old_path = item_widget.file_path

        # Remove the old file when the name (and therefore slug) changed.
        if old_path is not None and old_path != new_path and old_path.exists():
            old_path.unlink()
            _LOG.debug("Renamed preset file: %s → %s", old_path.name, new_path.name)

        save_preset(preset, new_path)
        item_widget.file_path = new_path
        item_widget.update_preset(preset)
        current.setSizeHint(item_widget.sizeHint())
        _LOG.debug("Preset saved: %s", new_path)

    def _on_export_preset(self) -> None:
        """Export the current preset to a user-chosen location (stub)."""
        _LOG.debug("Export preset requested (stub)")
        # TODO: open a file dialog, write the preset TOML to the chosen path.

    def _on_delete_preset(self) -> None:
        """Delete the selected preset from the list and from disk.

        Removes the backing ``.toml`` file via
        :func:`~flash_excel.presets.store.delete_preset` (no-op when
        the preset was never saved), then takes the row out of the
        :class:`QListWidget` and clears the name field.
        """
        current = self._preset_list.currentItem()
        if current is None:
            return
        item_widget = self._preset_list.itemWidget(current)
        if (
            isinstance(item_widget, PresetListItem)
            and item_widget.file_path is not None
        ):
            delete_preset(item_widget.file_path)
            _LOG.debug("Preset file deleted: %s", item_widget.file_path)

        row = self._preset_list.row(current)
        self._preset_list.takeItem(row)
        self._name_field.clear()
        self._show_placeholder()

    def retranslate_ui(self) -> None:
        """Apply current language to all user-visible labels in this page."""
        self._page_title.setText(self._tr("Presets"))
        self._name_field.setPlaceholderText(self._tr("Preset name"))
        self._save_button.text = self._tr("Save")
        self._delete_button.text = self._tr("Delete")
        self._export_button.text = self._tr("Export")
        self._placeholder_label.setText(self._tr("Select a preset or create a new one"))
        self._settings_header_title.setText(self._tr("Settings"))
        self._file_step_title.setText(self._tr("Load the Excel template"))
        self._file_hint.setText(self._tr("Accepted formats: .xlsx, .xls, .xlsm, .csv"))
        self._actions_step_title.setText(self._tr("Action configuration"))
        self._actions_step_hint.setText(self._tr("Select an action to configure it"))

    def changeEvent(self, event: QEvent) -> None:
        """React to language changes by re-applying all translated labels."""
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

__all__ = ["PresetsPage"]
