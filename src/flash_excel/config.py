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
    },
    "locale": "en",
}

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

# //////
# Langue
# Valeurs disponibles : en | fr
locale: {locale}
"""


def load_app_config() -> dict:
    """Charge la config, crée le fichier avec les défauts s'il n'existe pas."""
    if not APP_CONFIG.exists():
        _write(
            _DEFAULTS["appearance"]["palette"],
            _DEFAULTS["appearance"]["mode"],
            _DEFAULTS["locale"],
        )
        return {
            "appearance": dict(_DEFAULTS["appearance"]),
            "locale": _DEFAULTS["locale"],
        }
    try:
        raw = yaml.safe_load(APP_CONFIG.read_text(encoding="utf-8")) or {}
        app = raw.get("appearance", {})
        return {
            "appearance": {
                "palette": app.get("palette", _DEFAULTS["appearance"]["palette"]),
                "mode": app.get("mode", _DEFAULTS["appearance"]["mode"]),
            },
            "locale": raw.get("locale", _DEFAULTS["locale"]),
        }
    except Exception:
        return {
            "appearance": dict(_DEFAULTS["appearance"]),
            "locale": _DEFAULTS["locale"],
        }


def save_app_config(palette: str, mode: str, locale: str = "en") -> None:
    """Persiste les réglages d'apparence et la locale en conservant les commentaires."""
    _write(palette, mode, locale)


def load_themes() -> dict:
    """Retourne le dict complet des palettes depuis theme.config.yaml."""
    try:
        data = yaml.safe_load(THEMES_CONFIG.read_text(encoding="utf-8")) or {}
        return data.get("palette", {})
    except Exception:
        return {}


def _write(palette: str, mode: str, locale: str) -> None:
    APP_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    APP_CONFIG.write_text(
        _TEMPLATE.format(palette=palette, mode=mode, locale=locale),
        encoding="utf-8",
    )
