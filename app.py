"""
Movies REST API — Flask + SQLite sample for Xavier Ateneo ITCC 14.

==============================================================================
HOW THIS PROJECT MAPS TO MVC (lecture talking points)
==============================================================================
MVC = Model–View–Controller. We split the app so each part has one job:

  Model (models.py)
    - Owns the data and the database (SQLite file movies.db).
    - Creates the table, runs CRUD queries, returns plain Python dicts.
    - Knows NOTHING about HTTP, URLs, or status codes.

  View (two of them, on purpose)
    - API View: JSON from jsonify(...) on the /movies routes.
      curl, Postman, and the browser's fetch() all see this.
      Those routes stay JSON. They do not render HTML.
    - HTML View: templates/index.html (styled by static/style.css).
      A browser paints this. It does not query SQLite.
      static/app.js calls the JSON API with fetch(). That script is
      the frontend talking to the same REST routes as curl.
    - In a classic server-rendered app, the route builds the HTML from
      the database. Here the page is a client of the API. That is the
      fullstack step: same Controller and Model, a second View.

  Controller (this file — app.py)
    - Route handlers receive the HTTP request.
    - They validate input, call the Model, pick the status code, and
      return JSON (the API View).
    - Example flow for POST /movies:
        request JSON → validate → create_movie() → jsonify + 201

Why separate them?
  - Students can change the database without rewriting every route.
  - Students can add a frontend later without rewriting models.py.
    The HTML page does that: models.py is unchanged.
  - Easier to test and to explain in class: "Controller talks HTTP;
    Model talks SQLite; the API View is the JSON body; the HTML View
    is the page that calls that API."

Endpoints (JSON API, unchanged):
  GET    /movies
  GET    /movies/<id>
  POST   /movies
  PUT    /movies/<id>
  DELETE /movies/<id>

Browser UI:
  GET    /     HTML when the client prefers text/html (see index())
               curl without that Accept header still gets JSON
==============================================================================
"""

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

# Model layer — all database work lives in models.py (not here).
from models import (
    REQUIRED_FIELDS,
    create_movie,
    delete_movie,
    get_all_movies,
    get_movie_by_id,
    init_db,
    movie_count,
    update_movie,
)
from seed import seed

# ---------------------------------------------------------------------------
# App setup (still Controller concerns: create the Flask app, enable CORS)
# ---------------------------------------------------------------------------
app = Flask(__name__)

# flask-cors lets a page on another origin call this API.
# The HTML UI in templates/ is served by this same Flask app (same origin),
# so it does not need CORS. CORS stays on for a separate frontend later.
# Optional for curl/Postman.
CORS(app)


# ---------------------------------------------------------------------------
# Input validation (Controller helper)
# Controllers should not trust raw client input. We check required fields
# and types BEFORE calling the Model. Bad input → 400, never touch the DB.
# ---------------------------------------------------------------------------
def validate_movie_payload(data):
    """
    Validate JSON body for POST/PUT.

    Required fields: title, year, genre.
    Optional fields: director, rating.

    Returns (cleaned_data, error_message). On success, error_message is None.
    """
    if data is None or not isinstance(data, dict):
        return None, "Request body must be a JSON object."

    # Required fields must be present and not empty/null.
    missing = [field for field in REQUIRED_FIELDS if field not in data or data[field] in (None, "")]
    if missing:
        return None, f"Missing required field(s): {', '.join(missing)}."

    cleaned = {}

    # title — non-empty string
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return None, "Field 'title' must be a non-empty string."
    cleaned["title"] = title.strip()

    # year — integer (also accept numeric strings like "2020" from forms)
    year = data.get("year")
    if isinstance(year, bool) or not isinstance(year, int):
        try:
            year = int(year)
        except (TypeError, ValueError):
            return None, "Field 'year' must be an integer."
    if year < 1888 or year > 2100:
        return None, "Field 'year' must be between 1888 and 2100."
    cleaned["year"] = year

    # genre — non-empty string
    genre = data.get("genre")
    if not isinstance(genre, str) or not genre.strip():
        return None, "Field 'genre' must be a non-empty string."
    cleaned["genre"] = genre.strip()

    # director — optional string
    if "director" in data and data["director"] is not None:
        director = data["director"]
        if not isinstance(director, str):
            return None, "Field 'director' must be a string."
        cleaned["director"] = director.strip() or None
    else:
        cleaned["director"] = None

    # rating — optional float between 1 and 10
    if "rating" in data and data["rating"] is not None and data["rating"] != "":
        rating = data["rating"]
        try:
            rating = float(rating)
        except (TypeError, ValueError):
            return None, "Field 'rating' must be a number."
        if rating < 1 or rating > 10:
            return None, "Field 'rating' must be between 1 and 10."
        cleaned["rating"] = round(rating, 1)
    else:
        cleaned["rating"] = None

    return cleaned, None


# ===========================================================================
# ROUTES = Controller actions
# /movies: read request → (validate) → call Model → return JSON + code.
# jsonify(...) is the API View for those routes.
# GET / is the exception for browsers: it returns the HTML View and does
# not call the Model. The page's JavaScript calls /movies itself.
# ===========================================================================


@app.get("/")
def index():
    """
    GET / : HTML page for browsers, JSON welcome for API clients.

    A browser navigation sends Accept: text/html at a higher quality than
    JSON, so we render templates/index.html (HTML View). That template
    does not touch the database. static/app.js loads data with fetch()
    against the /movies routes below (API View).

    curl's default Accept is */*, so text/html and application/json tie.
    On a tie we keep the original JSON welcome. /movies is always JSON.
    """
    html_quality = request.accept_mimetypes["text/html"]
    json_quality = request.accept_mimetypes["application/json"]
    if html_quality > json_quality:
        return render_template("index.html")

    return jsonify(
        {
            "message": "Movies API — Xavier Ateneo ITCC 14 sample",
            "endpoints": {
                "GET /movies": "List all movies",
                "GET /movies/<id>": "Get one movie",
                "POST /movies": "Create a movie",
                "PUT /movies/<id>": "Update a movie",
                "DELETE /movies/<id>": "Delete a movie",
            },
        }
    )


@app.get("/movies")
def list_movies():
    """
    GET /movies — list all movies.

    Success: 200 + JSON array (may be empty []).
    No request body; no validation needed.
    Controller asks the Model for data, then returns it as JSON (View).
    """
    movies = get_all_movies()  # Model
    return jsonify(movies), 200  # View + status


@app.get("/movies/<int:movie_id>")
def get_movie(movie_id):
    """
    GET /movies/<id> — fetch one movie by primary key.

    Success: 200 + one movie object.
    Error:   404 if that id does not exist.
    """
    movie = get_movie_by_id(movie_id)  # Model
    if movie is None:
        return jsonify({"error": f"Movie with id {movie_id} not found."}), 404
    return jsonify(movie), 200


@app.post("/movies")
def add_movie():
    """
    POST /movies — create a new movie.

    Body (JSON): title, year, genre required; director, rating optional.
    Success: 201 + the created movie (includes new id).
    Error:   400 if JSON is missing/invalid or required fields are absent.

    Pattern: validate first → only then call create_movie (Model).
    """
    data = request.get_json(silent=True)  # silence errors; we return our own 400
    cleaned, error = validate_movie_payload(data)
    if error:
        return jsonify({"error": error}), 400

    movie = create_movie(cleaned)  # Model writes to SQLite
    return jsonify(movie), 201


@app.put("/movies/<int:movie_id>")
def put_movie(movie_id):
    """
    PUT /movies/<id> — replace/update an existing movie.

    Body: same rules as POST (title, year, genre required).
    Success: 200 + updated movie.
    Errors:  404 if id missing; 400 if body fails validation.

    We check existence first so students see a clear 404 vs 400 distinction.
    """
    if get_movie_by_id(movie_id) is None:
        return jsonify({"error": f"Movie with id {movie_id} not found."}), 404

    data = request.get_json(silent=True)
    cleaned, error = validate_movie_payload(data)
    if error:
        return jsonify({"error": error}), 400

    movie = update_movie(movie_id, cleaned)  # Model
    return jsonify(movie), 200


@app.delete("/movies/<int:movie_id>")
def remove_movie(movie_id):
    """
    DELETE /movies/<id> — remove a movie.

    Success: 200 + confirmation message.
    Error:   404 if id does not exist.
    No request body required.
    """
    deleted = delete_movie(movie_id)  # Model
    if not deleted:
        return jsonify({"error": f"Movie with id {movie_id} not found."}), 404
    return jsonify({"message": f"Movie with id {movie_id} deleted."}), 200


# ---------------------------------------------------------------------------
# Startup: create schema + seed sample data if the table is empty.
# This is app wiring (still Controller / app bootstrap), not business logic.
# ---------------------------------------------------------------------------
def bootstrap():
    """Create tables and seed sample data when the DB is empty."""
    init_db()
    if movie_count() == 0:
        seed()


# Run bootstrap when this module is imported (python app.py / flask run).
bootstrap()


if __name__ == "__main__":
    # debug=True auto-reloads on code changes — great for class demos.
    # host 0.0.0.0 lets other devices on the network reach the API if needed.
    app.run(debug=True, host="0.0.0.0", port=5000)
