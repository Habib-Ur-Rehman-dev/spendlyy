# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Spendly is a personal expense-tracker built as a **step-by-step teaching scaffold**. Much of the app is intentionally incomplete: routes in `app.py` under the "Placeholder routes" comment return plain strings like `"Add expense — coming in Step 7"`, and `database/db.py` is an empty stub documenting the functions a student is expected to write. Treat these as unimplemented-by-design, not bugs — do not "fix" a placeholder unless the task is to implement that step.

## Commands

All commands use the project virtualenv (`venv/`). On this Windows/PowerShell setup, `python` on the PATH may resolve to a Microsoft Store stub, so invoke the venv interpreter by path:

```powershell
# Run the app — serves http://127.0.0.1:5001 with debug/auto-reload on
.\venv\Scripts\python.exe app.py

# Install / update dependencies
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Run the test suite (pytest + pytest-flask are installed; no tests exist yet)
.\venv\Scripts\python.exe -m pytest

# Run a single test
.\venv\Scripts\python.exe -m pytest tests/test_file.py::test_name
```

The dev server runs on **port 5001** (not the Flask default 5000).

## Architecture

- **`app.py`** — the entire backend: one Flask app with thin route functions, each rendering a template or returning a placeholder string. There is no blueprint/package split; add routes here.
- **`database/db.py`** — intended data layer (SQLite). The stub's docstring is the contract: `get_db()` (connection with `row_factory` + foreign keys enabled), `init_db()` (`CREATE TABLE IF NOT EXISTS`), `seed_db()`. The DB file `expense_tracker.db` is gitignored. Nothing in `app.py` wires to the database yet.
- **Templates (`templates/`)** — Jinja inheritance. Every page `{% extends "base.html" %}`. `base.html` owns the shared navbar + footer and exposes four blocks: `title`, `head`, `content`, `scripts`. Footer links (terms/privacy) are defined once here via `url_for`, so they apply to every page.
- **Page-scoped CSS/JS convention** — page-specific styling and behavior go *inside the child template* via `{% block head %}` (a `<style>` block) and `{% block scripts %}` (vanilla `<script>`), keeping features self-contained. Examples: the "See how it works" video modal in `landing.html`, and the scoped `.legal-*` card styling in `terms.html` / `privacy.html`. This project uses **no JS framework** — keep client code vanilla, no third-party libraries.

## Data-layer rules (SQLite) — non-negotiable

- **No ORM.** Use the standard-library `sqlite3` only — no SQLAlchemy or any
  other ORM.
- **Parameterized queries only.** Always pass values via `?` placeholders
  (`execute`/`executemany`). Never build SQL with string formatting (f-strings,
  `%`, `.format()`, or concatenation) — including for values that "look safe".
- **Foreign keys always on.** Every connection must run
  `PRAGMA foreign_keys = ON;`. Obtain connections through `get_db()` (which
  already does this) rather than calling `sqlite3.connect()` directly.
- **Money is `REAL`.** Store `amount` as a float (`REAL`), not an integer.

## Styling

`static/css/style.css` is the single global stylesheet and defines the whole visual system through CSS custom properties in `:root` — colors (`--ink`, `--paper`, `--accent`, `--border`, …), fonts (`--font-display`, `--font-body`), and radii (`--radius-sm/md/lg`). New UI should reuse these tokens rather than hard-coding values so it stays on-theme. The legal pages establish a reusable badge + card pattern (`.legal-badge`, `.legal-card`, accent-numbered sections) worth matching for similar content pages.
