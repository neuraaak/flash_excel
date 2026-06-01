"""PyWebView application entry point for flash-excel."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Doit être positionné avant l'import de webview pour prendre effet.
os.environ.setdefault("PYWEBVIEW_LOG", "WARNING")

import webview  # type: ignore[import-untyped]  # noqa: E402

from flash_excel.paths import BIN_DIR
from flash_excel.ui.api import FlashExcelAPI
from flash_excel.updater import start_update_check

_WEB_DIR = Path(__file__).parent / "web"
_ICON = BIN_DIR / "assets" / "images" / "logo.ico"


def _log(msg: str) -> None:
    print(f"[flash-excel] {msg}")


def run() -> None:
    """Launch the flash-excel desktop window via PyWebView."""
    _log("starting")
    start_update_check()
    api = FlashExcelAPI()

    webview.create_window(
        title="Flash-Excel",
        url=(_WEB_DIR / "index.html").as_uri(),
        js_api=api,
        width=1280,
        height=800,
        min_size=(900, 600),
        background_color="#161a20",
    )

    webview.start(debug="--debug" in sys.argv, icon=str(_ICON))
