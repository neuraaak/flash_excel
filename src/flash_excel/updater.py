# ///////////////////////////////////////////////////////////////
# UPDATER - Tufup client integration for flash-excel
# ///////////////////////////////////////////////////////////////

"""Auto-update check and apply via tufup + GitHub Releases.

This module exposes a single public function, `check_and_apply_update()`,
intended to be called once at startup (in a background thread) so it never
blocks the UI.

GitHub Release layout expected by tufup:
    https://github.com/<owner>/<repo>/releases/download/<tag>/<file>

The metadata and target base URLs point to the latest release tag so that
tufup can discover new versions independently.
"""

from __future__ import annotations

import threading

from flash_excel._version import __version__
from flash_excel.paths import BIN_DIR, PROJECT_ROOT

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

APP_NAME = "flash-excel"

# GitHub base URL for tufup files hosted on Releases
_GH_BASE = "https://github.com/neuraaak/flash-excel/releases/download"

# tufup uses a flat layout: all files are at the root of each release tag.
# Both metadata and targets are uploaded to the same release, so we use
# the same base URL pattern.  tufup appends the filename automatically.
METADATA_BASE_URL = f"{_GH_BASE}/latest/"
TARGET_BASE_URL = f"{_GH_BASE}/latest/"

# Local dirs (created automatically if absent)
_TUFUP_DIR = BIN_DIR / "tufup"
METADATA_DIR = _TUFUP_DIR / "metadata"
TARGET_DIR = _TUFUP_DIR / "targets"

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def check_and_apply_update(*, silent: bool = True) -> None:
    """Check for updates and apply them if available.

    Runs synchronously — call in a background thread to avoid blocking UI.

    Args:
        silent: If True, swallow non-critical errors (network unavailable, etc.).
                Set to False during development/testing for full tracebacks.
    """
    try:
        from tufup.client import Client

        METADATA_DIR.mkdir(parents=True, exist_ok=True)
        TARGET_DIR.mkdir(parents=True, exist_ok=True)

        client = Client(
            app_name=APP_NAME,
            app_install_dir=PROJECT_ROOT,
            current_version=__version__,
            metadata_dir=METADATA_DIR,
            metadata_base_url=METADATA_BASE_URL,
            target_dir=TARGET_DIR,
            target_base_url=TARGET_BASE_URL,
        )

        update = client.check_for_updates()
        if update is None:
            return

        print(f"[updater] update available: {update.version}")
        client.download_and_apply_update(skip_confirmation=True)

    except Exception as exc:  # noqa: BLE001
        if not silent:
            raise
        print(f"[updater] update check failed (non-critical): {exc}")


def start_update_check() -> None:
    """Launch the update check in a daemon background thread."""
    thread = threading.Thread(target=check_and_apply_update, daemon=True)
    thread.start()
