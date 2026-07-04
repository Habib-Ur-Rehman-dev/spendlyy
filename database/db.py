"""SQLite data layer for Spendly.

Provides:
    get_db()   — a SQLite connection with row_factory and foreign keys enabled
    init_db()  — creates all tables/indexes using CREATE TABLE IF NOT EXISTS
    seed_db()  — inserts sample data for development

Run directly to create and seed the database on a fresh checkout:
    python -m database.db
"""

import os
import sqlite3

from werkzeug.security import generate_password_hash

# Demo login credentials for development. The password is stored hashed (never in
# plaintext); this constant just documents what to log in with once auth exists.
DEMO_EMAIL = "demo@spendly.app"
DEMO_PASSWORD = "demo1234"

# Resolve the database path relative to the project root so it works no matter
# what the current working directory is.
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expense_tracker.db")

# Fixed set of expense categories. Single source of truth for the whole app —
# reuse this for the add/edit form dropdown and server-side validation in later
# steps. `category` is stored as free text, so this list is what constrains it.
CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]


def get_db():
    """Return a SQLite connection with rows accessible by name and FKs enforced."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Create all tables and indexes. Idempotent — safe to call repeatedly."""
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at    TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            amount      REAL NOT NULL CHECK (amount >= 0),
            category    TEXT NOT NULL,
            description TEXT,
            date        TEXT NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
        """
    )
    conn.commit()
    conn.close()


def seed_db():
    """Insert sample development data. Safe to re-run (skips if already seeded)."""
    init_db()
    conn = get_db()

    # Guard: don't duplicate seed data on repeated runs.
    already = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    if already:
        conn.close()
        return

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", DEMO_EMAIL, generate_password_hash(DEMO_PASSWORD)),
    )
    user_id = cursor.lastrowid

    sample_expenses = [
        # (amount, category, description, date) — spans every fixed category
        (3200.00, "Food", "Groceries", "2026-03-08"),
        (650.00, "Food", "Dinner out", "2026-03-27"),
        (1800.00, "Transport", "Fuel", "2026-03-15"),
        (4500.00, "Bills", "Electricity bill", "2026-03-05"),
        (2050.00, "Health", "Pharmacy", "2026-03-12"),
        (1500.00, "Entertainment", "Movie night", "2026-03-18"),
        (2400.00, "Shopping", "New shoes", "2026-03-21"),
        (1200.00, "Other", "Misc supplies", "2026-03-24"),
    ]
    conn.executemany(
        """
        INSERT INTO expenses (user_id, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        [(user_id, *row) for row in sample_expenses],
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    seed_db()
    print(f"Initialized and seeded database at {DB_PATH}")
