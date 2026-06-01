#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PUBLISH - Package and publish flash-excel via tufup + GitHub Releases
# ///////////////////////////////////////////////////////////////

"""Publish script for flash-excel.

Creates a signed tufup update package from the compiled dist/ folder,
then uploads metadata and targets to GitHub Releases via the `gh` CLI.

Workflow:
    1. Initialize local tufup repository (once, or safe to re-run)
    2. Generate key pairs if they don't exist yet
    3. Create archive + patch from dist/
    4. Sign metadata (publish_changes)
    5. Upload targets + metadata to GitHub Release

Prerequisites:
    - `gh` CLI installed and authenticated (gh auth login)
    - dist/ populated by build.py

Usage:
    uv run .scripts/build/publish.py
    uv run .scripts/build/publish.py --skip-upload   # local only, no GitHub push
    uv run .scripts/build/publish.py --skip-patch    # full archive only, no diff
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import argparse
import builtins
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

# Third-party imports
from tufup.repo import Repository

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DIST_DIR = PROJECT_ROOT / "dist" / "Flash-Excel"
TUFUP_REPO_DIR = PROJECT_ROOT / ".tufup" / "repo"
TUFUP_KEYS_DIR = PROJECT_ROOT / ".tufup" / "keys"

# ///////////////////////////////////////////////////////////////
# HELPERS
# ///////////////////////////////////////////////////////////////


def _gh() -> str:
    """Return the absolute path to the gh CLI, or raise if not found."""
    exe = shutil.which("gh")
    if exe is None:
        raise FileNotFoundError(
            "gh CLI not found in PATH.\n"
            "Install it from https://cli.github.com/ and run `gh auth login`."
        )
    return exe


def _read_project_meta() -> tuple[str, str]:
    """Read app name and version from pyproject.toml."""
    with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    project = data["project"]
    return project["name"], project["version"]


def _gh_ensure_release(tag: str, version: str) -> None:
    """Create the GitHub Release if it does not already exist."""
    check = subprocess.run(  # noqa: S603
        [_gh(), "release", "view", tag],
        check=False,
        capture_output=True,
    )
    if check.returncode == 0:
        print(f"GitHub Release {tag} already exists.")
        return
    result = subprocess.run(  # noqa: S603
        [
            _gh(),
            "release",
            "create",
            tag,
            "--title",
            f"Flash-Excel {version}",
            "--notes",
            f"Release {version}",
        ],
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh release create failed (exit {result.returncode})")
    print(f"GitHub Release {tag} created.")


def _gh_upload(tag: str, files: list[Path]) -> None:
    """Upload files to a GitHub Release via the gh CLI."""
    paths = [str(p) for p in files if p.exists()]
    if not paths:
        print("No files to upload.")
        return
    cmd = [_gh(), "release", "upload", tag, *paths, "--clobber"]
    result = subprocess.run(cmd, check=False)  # noqa: S603
    if result.returncode != 0:
        raise RuntimeError(f"gh release upload failed (exit {result.returncode})")


def _collect_repo_files() -> list[Path]:
    """Collect all tufup repo files to upload (metadata + targets)."""
    files: list[Path] = []
    metadata_dir = TUFUP_REPO_DIR / "metadata"
    targets_dir = TUFUP_REPO_DIR / "targets"
    if metadata_dir.exists():
        files.extend(metadata_dir.iterdir())
    if targets_dir.exists():
        files.extend(targets_dir.iterdir())
    return files


# ///////////////////////////////////////////////////////////////
# MAIN
# ///////////////////////////////////////////////////////////////


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package and publish flash-excel.")
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Skip GitHub Release upload (local tufup repo only).",
    )
    parser.add_argument(
        "--skip-patch",
        action="store_true",
        help="Skip patch generation (full archive only).",
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Force regeneration of tufup key pairs even if they already exist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    app_name, version = _read_project_meta()
    print(f"Packaging {app_name} v{version}")

    # -- Step 1: Initialize local tufup repo (idempotent) --
    # Patch builtins.input to auto-answer the "Overwrite key pair?" prompt:
    # answer 'y' only when --regenerate is passed, otherwise always 'n'.
    _original_input = builtins.input
    builtins.input = lambda _prompt="": "y" if args.regenerate else "n"
    try:
        repo = Repository(
            app_name=app_name,
            repo_dir=TUFUP_REPO_DIR,
            keys_dir=TUFUP_KEYS_DIR,
        )
        repo.initialize()
    finally:
        builtins.input = _original_input
    print("Tufup repo initialized.")

    # -- Step 2: Add bundle (archive + optional patch) --
    if not DIST_DIR.exists():
        print(f"ERROR: dist/ not found at {DIST_DIR}. Run build.py first.")
        return 1

    repo.add_bundle(
        new_bundle_dir=DIST_DIR,
        new_version=version,
        skip_patch=args.skip_patch,
    )
    print("Bundle added.")

    # -- Step 3: Sign and publish metadata --
    repo.publish_changes(private_key_dirs=[TUFUP_KEYS_DIR])
    print("Metadata signed and published.")

    # -- Step 4: Upload to GitHub Release --
    if not args.skip_upload:
        tag = f"v{version}"
        _gh_ensure_release(tag=tag, version=version)
        print(f"Uploading to GitHub Release {tag}...")
        _gh_upload(tag=tag, files=_collect_repo_files())
        print("Upload complete.")
    else:
        print("Skipping GitHub upload (--skip-upload).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
