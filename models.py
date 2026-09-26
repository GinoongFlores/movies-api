"""
models.py — the MODEL layer (MVC) for the Movies API.

In MVC, the Model is responsible for data:
  - What a "movie" looks like (table schema / fields)
  - How we store and retrieve movies (SQLite CRUD helpers)
  - Returning plain Python values (dicts / lists) to the Controller

This file does NOT know about Flask routes, HTTP methods, or status codes.
app.py (Controller) calls these functions and decides what JSON + code to send.

Why SQLite?
  - One file (movies.db) — no separate database server to install.
  - Built into Python (sqlite3) — perfect for ITCC 14 labs and demos.
  - Good enough for a small classroom API; later courses may use PostgreSQL.
"""

import sqlite3
from pathlib import Path

# Database file lives next to this script (project folder).
DB_PATH = Path(__file__).resolve().parent / "movies.db"

# Field rules shared with the Controller (validation in app.py).
REQUIRED_FIELDS = ("title", "year", "genre")
OPTIONAL_FIELDS = ("director", "rating")
ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------
def get_connection():
    """
    Open a SQLite connection.

    row_factory = sqlite3.Row lets us access columns by name (row["title"])
    instead of by index — clearer for students reading the code.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create the movies table if it does not already exist (schema).

    Columns match the Canvas brief:
      id        — auto-increment primary key
      title     — required text
      year      — required integer
      genre     — required text
      director  — optional text
      rating    — optional REAL (float), typically 1.0–10.0
    """
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER NOT NULL,
                genre TEXT NOT NULL,
                director TEXT,
                rating REAL
            )
            """
        )
        conn.commit()
    finally:
        # Always close — good habit even in small demos.
        conn.close()


def movie_count():
    """How many rows are in movies? Used by bootstrap/seed to detect an empty DB."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) AS count FROM movies").fetchone()
        return row["count"]
    finally:
        conn.close()


def row_to_dict(row):
    """
    Turn a sqlite3.Row into a normal dict.

    Controllers (and jsonify) work best with plain dicts — this is the
    Model's job: present data in a simple shape, not Flask-specific types.
    """
    if row is None:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "year": row["year"],
        "genre": row["genre"],
        "director": row["director"],
        "rating": row["rating"],
    }


# ---------------------------------------------------------------------------
# CRUD helpers — Create, Read, Update, Delete
# The Controller calls these; it never writes raw SQL itself.
# ---------------------------------------------------------------------------
def get_all_movies():
    """READ many: return every movie as a list of dicts (ordered by id)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, title, year, genre, director, rating FROM movies ORDER BY id"
        ).fetchall()
        return [row_to_dict(row) for row in rows]
    finally:
        conn.close()


def get_movie_by_id(movie_id):
    """
    READ one: return a movie dict, or None if the id is missing.

    Returning None (instead of raising) lets the Controller map that to HTTP 404.
    The "?" placeholder prevents SQL injection — always use parameters, not f-strings.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, title, year, genre, director, rating FROM movies WHERE id = ?",
            (movie_id,),
        ).fetchone()
        return row_to_dict(row)
    finally:
        conn.close()


def create_movie(data):
    """
    CREATE: insert one movie, then return the full row (including new id).

    Expects a dict already validated by the Controller (title, year, genre, …).
    lastrowid gives us the auto-generated primary key after INSERT.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO movies (title, year, genre, director, rating)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["title"],
                data["year"],
                data["genre"],
                data.get("director"),
                data.get("rating"),
            ),
        )
        conn.commit()
        movie_id = cursor.lastrowid
    finally:
        conn.close()
    return get_movie_by_id(movie_id)


def update_movie(movie_id, data):
    """
    UPDATE: replace fields for an existing movie.

    Returns the updated dict, or None if the id was not found.
    (Controller already checks 404 in our routes, but the Model stays safe.)
    """
    existing = get_movie_by_id(movie_id)
    if existing is None:
        return None

    updated = {
        "title": data["title"],
        "year": data["year"],
        "genre": data["genre"],
        "director": data.get("director"),
        "rating": data.get("rating"),
    }

    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE movies
            SET title = ?, year = ?, genre = ?, director = ?, rating = ?
            WHERE id = ?
            """,
            (
                updated["title"],
                updated["year"],
                updated["genre"],
                updated["director"],
                updated["rating"],
                movie_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return get_movie_by_id(movie_id)


def delete_movie(movie_id):
    """
    DELETE: remove a movie by id.

    Returns True if a row was deleted, False if the id did not exist.
    Controller turns False into HTTP 404.
    """
    existing = get_movie_by_id(movie_id)
    if existing is None:
        return False

    conn = get_connection()
    try:
        conn.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        conn.commit()
    finally:
        conn.close()
    return True
