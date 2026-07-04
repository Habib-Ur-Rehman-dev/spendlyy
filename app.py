import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db, init_db, seed_db

app = Flask(__name__)

# Secret key is required to sign the session cookie. Dev-only value — replace
# with a securely generated secret (e.g. via an env var) before any real deploy.
app.secret_key = "dev-only-secret-change-me"

# Ensure the database schema exists and has development data before any request
# is served. init_db() is idempotent and seed_db() skips if already seeded, so
# this is safe to run on every startup (including the debug reloader's restart).
with app.app_context():
    init_db()
    seed_db()


def current_user():
    """Return the logged-in user row, or None if not authenticated."""
    uid = session.get("user_id")
    if uid is None:
        return None
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    db.close()
    return user


@app.context_processor
def inject_current_user():
    """Make `current_user` available to every template (e.g. the navbar)."""
    return {"current_user": current_user()}


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or not password:
        return render_template("register.html", error="All fields are required.")
    if len(password) < 8:
        return render_template(
            "register.html", error="Password must be at least 8 characters."
        )

    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        db.commit()
    except sqlite3.IntegrityError:
        # UNIQUE constraint on email — surface a friendly message, don't mask it.
        db.close()
        return render_template(
            "register.html", error="That email is already registered."
        )
    user_id = cursor.lastrowid
    db.close()

    session["user_id"] = user_id
    return redirect(url_for("profile"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    db.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"] = user["id"]
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user = current_user()
    if user is None:
        return redirect(url_for("login"))

    db = get_db()
    expenses = db.execute(
        "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC, id DESC",
        (user["id"],),
    ).fetchall()
    total = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE user_id = ?",
        (user["id"],),
    ).fetchone()["total"]
    db.close()

    return render_template(
        "profile.html", user=user, expenses=expenses, total=total
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
