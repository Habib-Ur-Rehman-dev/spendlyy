# Spec 01 — Database Setup

**Status:** Draft
**Step:** 1 (Database Setup)
**Owner:** database/db.py

## 1. Overview

Establish the SQLite data layer for Spendly. This step delivers the database
connection helper, schema creation, and development seed data. No routes are
wired to the database in this step — it only makes the data layer importable and
correct so later steps (auth, expense CRUD) can build on it.

## 2. Goals

- A single SQLite database file the app can open reliably.
- A schema that supports user accounts and per-user expenses.
- Reusable helpers matching the contract already documented in `database/db.py`:
  `get_db()`, `init_db()`, `seed_db()`.
- Foreign keys enforced and rows accessible by column name.

## 3. Non-goals

- Authentication logic, password hashing policy, or session handling (Step 3+).
- Expense CRUD routes or forms (Step 7+).
- Migrations / schema versioning (out of scope for a teaching scaffold).
- Any ORM. Use the standard library `sqlite3` only.

## 4. Database file & connection

- **File:** `expense_tracker.db` at the project root (already gitignored).
- **Connection settings** (every connection from `get_db()`):
  - `row_factory = sqlite3.Row` so rows are accessible by column name.
  - `PRAGMA foreign_keys = ON;` executed on each connection (SQLite defaults it
    off per-connection).

## 5. Schema

### `users`
| Column          | Type     | Constraints                                   |
|-----------------|----------|-----------------------------------------------|
| `id`            | INTEGER  | PRIMARY KEY AUTOINCREMENT                      |
| `name`          | TEXT     | NOT NULL                                       |
| `email`         | TEXT     | NOT NULL UNIQUE                                |
| `password_hash` | TEXT     | NOT NULL                                       |
| `created_at`    | TEXT     | NOT NULL DEFAULT (datetime('now'))            |

### `expenses`
| Column        | Type    | Constraints                                              |
|---------------|---------|---------------------------------------------------------|
| `id`          | INTEGER | PRIMARY KEY AUTOINCREMENT                                |
| `user_id`     | INTEGER | NOT NULL, REFERENCES `users(id)` ON DELETE CASCADE      |
| `amount`      | REAL    | NOT NULL, CHECK (`amount` >= 0)                          |
| `category`    | TEXT    | NOT NULL                                                |
| `description` | TEXT    |                                                         |
| `date`        | TEXT    | NOT NULL  (ISO `YYYY-MM-DD`)                             |
| `created_at`  | TEXT    | NOT NULL DEFAULT (datetime('now'))                      |

- Categories are stored as free text, constrained to a **fixed list** defined as
  the `CATEGORIES` constant in `database/db.py` (single source of truth, reused by
  the form dropdown and server-side validation in later steps):
  **Food, Transport, Bills, Health, Entertainment, Shopping, Other**. A dedicated
  categories table is intentionally deferred.
- Index: `CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);`

## 6. Function contracts (`database/db.py`)

- **`get_db()`** → `sqlite3.Connection`
  Opens `expense_tracker.db`, sets `row_factory = sqlite3.Row`, enables
  `PRAGMA foreign_keys = ON`, and returns the connection. Callers are
  responsible for closing it (or it is closed via the app teardown in a later
  step).

- **`init_db()`** → `None`
  Creates all tables and indexes using `CREATE TABLE IF NOT EXISTS` (idempotent —
  safe to call repeatedly). Commits.

- **`seed_db()`** → `None`
  Inserts sample development data: one demo user and a handful of expenses across
  the known categories. Must be safe to run on an already-seeded DB (guard by
  checking for existing rows, or clear-then-insert). Commits.

## 7. Seed data

- One demo user (`demo@spendly.app`, name "Demo User") whose password is stored
  **hashed** via `werkzeug.security.generate_password_hash` (never plaintext).
  The dev password is `demo1234` (exposed as `DEMO_PASSWORD` for later login).
- **8 expenses** for that user spanning every fixed category and a range of
  dates, so later list/summary screens have something to render.

## 8. Integration expectation

- `init_db()` (and optionally `seed_db()`) must be runnable so a developer can
  create the database on a fresh checkout — e.g. `python -c "from database.db
  import init_db, seed_db; init_db(); seed_db()"`. Wiring it into app startup or
  a Flask CLI command is allowed but not required by this step.
- No route changes in this step.

## 9. Acceptance criteria

- Importing `database.db` and calling `init_db()` on a clean checkout creates
  `expense_tracker.db` with the `users` and `expenses` tables.
- `get_db()` returns a connection where `row["email"]`-style access works and
  foreign-key constraints are enforced (deleting a user cascades to expenses).
- Calling `init_db()` twice does not error or duplicate schema.
- `seed_db()` populates the demo user and expenses and is safe to re-run.
