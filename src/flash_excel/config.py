# ///////////////////////////////////////////////////////////////
# CONFIG - App configuration and theme loading
# Project: flash-excel
# ///////////////////////////////////////////////////////////////

from __future__ import annotations

import yaml

from flash_excel.paths import APP_CONFIG, THEMES_CONFIG

_DEFAULTS: dict = {
    "appearance": {
        "palette": "blue-gray",
        "mode": "dark",
    }
}

# Template conservé à l'écriture pour garder les commentaires inline
_TEMPLATE = """\
# ///////////////////////////////////////////////////////////////
# Flash-Excel — Configuration utilisateur
# Ce fichier est géré automatiquement par l'application.
# Vous pouvez l'éditer manuellement ; les changements seront
# pris en compte au prochain démarrage.
# ///////////////////////////////////////////////////////////////

# //////
# Apparence
appearance:
  # Palette de couleurs active.
  # Valeurs disponibles : blue-gray | github-dark | warm-dark
  palette: {palette}

  # Mode d'affichage.
  # Valeurs disponibles : dark | light
  mode: {mode}
"""


def load_app_config() -> dict:
    """Charge la config, crée le fichier avec les défauts s'il n'existe pas."""
    if not APP_CONFIG.exists():
        _write(_DEFAULTS["appearance"]["palette"], _DEFAULTS["appearance"]["mode"])
        return {k: dict(v) for k, v in _DEFAULTS.items()}
    try:
        raw = yaml.safe_load(APP_CONFIG.read_text(encoding="utf-8")) or {}
        app = raw.get("appearance", {})
        return {
            "appearance": {
                "palette": app.get("palette", _DEFAULTS["appearance"]["palette"]),
                "mode": app.get("mode", _DEFAULTS["appearance"]["mode"]),
            }
        }
    except Exception:
        return {k: dict(v) for k, v in _DEFAULTS.items()}


def save_app_config(palette: str, mode: str) -> None:
    """Persiste les réglages d'apparence en conservant les commentaires."""
    _write(palette, mode)


def load_themes() -> dict:
    """Retourne le dict complet des palettes depuis theme.config.yaml."""
    try:
        data = yaml.safe_load(THEMES_CONFIG.read_text(encoding="utf-8")) or {}
        return data.get("palette", {})
    except Exception:
        return {}


def _write(palette: str, mode: str) -> None:
    APP_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    APP_CONFIG.write_text(
        _TEMPLATE.format(palette=palette, mode=mode),
        encoding="utf-8",
    )
