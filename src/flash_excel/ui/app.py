"""PyWebView application entry point for flash-excel."""

from __future__ import annotations

import sys
from pathlib import Path

import webview  # type: ignore[import-untyped]

from flash_excel.ui.api import FlashExcelAPI

_WEB_DIR = Path(__file__).parent / "web"


def run() -> None:
    """Launch the flash-excel desktop window via PyWebView."""
    api = FlashExcelAPI()

    webview.create_window(
        title="Flash-Excel",
        url=str(_WEB_DIR / "index.html"),
        js_api=api,
        width=1280,
        height=800,
        min_size=(900, 600),
        background_color="#21252b",
    )

    webview.start(debug="--debug" in sys.argv)
