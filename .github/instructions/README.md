# Project Instructions

## Project Overview

**Project Name**: flash-excel
**Tech Stack**: Python 3.11+, Polars, Pydantic v2, PySide6, uv
**Environment**: Corporate environment with proxy restrictions, Windows desktop

## Project Description

Utilitaire desktop destiné à des utilisateurs non-techniques pour traiter des fichiers Excel/CSV
sans manipuler de macros. L'utilisateur sélectionne un fichier source, choisit un **preset**
(fichier TOML décrivant un pipeline de transformations), et exécute le pipeline pour produire
un fichier de sortie transformé. Le traitement **batch** sur plusieurs fichiers avec le même
preset est également supporté.

## Tech Stack Details

| Composant             | Choix                         | Justification                                       |
| --------------------- | ----------------------------- | --------------------------------------------------- |
| Traitement données    | **Polars**                    | Rapide (Rust), API claire, lecture Excel/CSV native |
| Validation preset     | **Pydantic v2**               | Schéma typé, erreurs claires au chargement          |
| Format preset         | **TOML** (`tomllib` stdlib)   | Lisible humain, natif Python 3.11+                  |
| Interface utilisateur | **PySide6**                   | Contrôle total, UI soignée, desktop natif           |
| Gestion dépendances   | **uv**                        | Moderne, rapide, standard 2025                      |
| Distribution          | **PyInstaller** ou **Nuitka** | `.exe` standalone sans installation Python          |

## Architecture

### Principe : couches plates (pas d'hexagonale)

L'architecture hexagonale est **explicitement écartée**. Ce projet a une seule source (fichier
local) et une seule sortie (fichier local), sans base de données ni API externe. Ajouter des
ports/adaptateurs serait de la cérémonie sans bénéfice. On adopte une **architecture en couches
plates**.

### Flux de données

```text
ui/  →  io/loader  →  core/pipeline  →  io/writer  →  fichier de sortie
```

### Structure des répertoires (package source)

```text
src/flash_excel/
│
├── core/                   # Logique métier pure — 0 dépendance sur ui/ ou io/
│   ├── pipeline.py         # Orchestration des steps
│   ├── registry.py         # Registre des actions (décorateur @action)
│   ├── models.py           # Modèles Pydantic discriminés par action
│   └── steps/              # Une fonction pure par action
│       ├── drop.py
│       ├── reorder.py
│       ├── filter.py
│       └── sort.py
│
├── io/                     # Lecture / écriture fichiers
│   ├── loader.py           # read_excel (fastexcel), read_csv
│   └── writer.py           # write_excel, write_csv
│
├── presets/                # Gestion des presets TOML
│   ├── parser.py           # Chargement + validation Pydantic
│   └── store.py            # Lister, sauvegarder, supprimer
│
└── ui/                     # PySide6 — ne touche qu'à core/ et io/
    ├── app.py
    └── widgets/
```

### Règle d'or

**`core/` ne connaît ni `ui/`, ni `io/`.**

Les steps reçoivent un `pl.DataFrame` et retournent un `pl.DataFrame`. Cette règle garantit :

- Testabilité complète de `core/` sans UI ni fichiers réels
- Possibilité de remplacer Polars sans toucher à l'UI

## Key Conventions

### Chargement de fichiers

- **Excel** : backend `fastexcel` (binding Rust sur `calamine`)
- **CSV** : séparateur `;` par défaut (exports Excel français), configurable dans le preset
- **Encodage CSV** : `utf8-lossy` par défaut pour absorber les caractères `cp1252`/`latin-1`
- **Chargement différé** : au moment de la sélection → headers uniquement (`n_rows=0`) ;
  au moment de l'exécution → fichier complet
- **Valeurs uniques** d'une colonne : chargées à la demande uniquement (pas au démarrage)

### Format de preset (TOML + Pydantic v2)

Chaque preset est un fichier `.toml` avec une section `[meta]` et une liste `[[steps]]`.
Chaque step a un champ `action` qui discrimine le modèle Pydantic.
Validation au chargement — erreur explicite avant toute exécution.

```toml
[meta]
name = "Rapport mensuel RH"
description = "Nettoyage du fichier RH brut"
csv_separator = ";"
csv_encoding = "utf8-lossy"

[[steps]]
action = "drop_columns"
columns = ["colonne_tmp", "doublon_export"]

[[steps]]
action = "filter_rows"
combine = "AND"
conditions = [
  { column = "statut", operator = "eq", value = "Actif" },
  { column = "salaire", operator = "gt", value = 25000 }
]
```

### Pattern registre d'actions

```python
REGISTRY: dict[str, Callable] = {}

def action(name: str):
    def decorator(fn):
        REGISTRY[name] = fn
        return fn
    return decorator

@action("drop_columns")
def drop_columns(df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
    return df.drop(columns)
```

### Schéma courant par step (UI)

L'ordre des steps impacte l'UI : si une colonne est supprimée en step 1, elle ne doit plus
apparaître dans les dropdowns des steps suivants. L'UI recalcule le schéma disponible à chaque
modification du pipeline via `compute_schema_at_step(steps, headers, index)`.

## Environment Setup

```bash
# Créer et activer l'environnement virtuel
uv venv
.venv\Scripts\activate

# Installer les dépendances de développement
uv pip install -e ".[dev]"

# Configurer les git hooks
git config core.hooksPath .hooks
```

## Instruction Files

| File                                                            | Purpose                           |
| --------------------------------------------------------------- | --------------------------------- |
| `core/advanced-cognitive-conduct.instructions.md`               | Core reasoning framework          |
| `core/commit-standards.instructions.md`                         | Git commit conventions            |
| `core/hexagonal-architecture-standards.instructions.md`         | **Non applicable** (see override) |
| `languages/python/python-development-standards.instructions.md` | Python coding standards           |
| `languages/python/python-formatting-standards.instructions.md`  | Code formatting rules             |
| `languages/python/pyproject-standards.instructions.md`          | pyproject.toml conventions        |

## Project-Specific Overrides

- **Pas d'architecture hexagonale** : l'instruction `hexagonal-architecture-standards` ne
  s'applique pas. Ce projet utilise des couches plates (`core/`, `io/`, `presets/`, `ui/`).
- **Pas de `cx_Freeze`** : la distribution utilise PyInstaller ou Nuitka (pas cx_Freeze).
- **`uv`** remplace `pip` pour toutes les opérations sur les dépendances.
- **`ty`** est l'outil de type checking principal (en complément de `pyright`).
- Les steps du pipeline sont des **fonctions pures** — ne pas les convertir en classes.

## Important Notes

- `core/` doit rester **sans dépendance** sur `ui/` et `io/` — toujours vérifier avant d'importer.
- Les tests de `core/` ne nécessitent **aucun fichier réel** — utiliser des DataFrames construits
  en mémoire.
- Les presets TOML sont **créés et modifiés par des utilisateurs non-techniques** — les messages
  d'erreur Pydantic doivent être traduits en langage clair avant d'être affichés.
- Points encore à définir :
  - Schéma Pydantic complet pour tous les types de steps
  - UX de création/édition/sauvegarde d'un preset depuis l'interface
  - Rapport de fin d'exécution (lignes en entrée/sortie, erreurs)
  - Gestion des erreurs utilisateur (colonne absente, valeur incompatible)
  - Nommage du fichier de sortie (suffixe, répertoire, écrasement)
