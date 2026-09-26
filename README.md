# Movies REST API

Flask + Python + SQLite sample project for **Xavier Ateneo ITCC 14**.

A small JSON REST API for a `movies` resource, plus a browser page that uses it.
Use it to practice CRUD endpoints, validation, SQLite, and a first fullstack step: HTML that calls the API with `fetch`.

## How this maps to MVC

This sample is organized for lecture use around **Model–View–Controller**:

| MVC piece | In this project | Job |
|-----------|-----------------|-----|
| **Model** | `models.py` (+ `movies.db`) | Schema, SQLite, CRUD helpers. No HTTP. |
| **View** | JSON from `jsonify(...)` on `/movies`, and `templates/index.html` | Two views. The API View is JSON. The HTML View is the page in the browser. The page does not read the database. |
| **Controller** | Route handlers in `app.py` | Read the request, validate, call the Model, choose status code, return JSON. |

**Typical request flow (example: `POST /movies`):**

1. Client sends HTTP + JSON body → Flask routes it to a function in `app.py` (**Controller**).
2. Controller validates required fields (`title`, `year`, `genre`). Bad input → **400** (never touches the DB).
3. Controller calls `create_movie(...)` in `models.py` (**Model**) to INSERT into SQLite.
4. Controller returns `jsonify(movie)` with **201**.
   That JSON body is the **API View**.

**Browser path (the HTML page):**

1. You open `http://127.0.0.1:5000`.
   The Controller sees `Accept: text/html` and returns `templates/index.html` (HTML View).
2. `static/app.js` runs `fetch("/movies")`.
   That is a normal `GET /movies`, the same request as curl.
3. The Controller and Model handle it as before and return JSON (API View).
4. The script turns that JSON into list rows.
   Create, edit, and delete are `POST`, `PUT`, and `DELETE` the same way.

`seed.py` is starter data for demos (hand-crafted, not from an external movie API). It uses the same Model helpers as a real create request.

## Project layout

```
movies-api/
  app.py                 # Controller: routes, validation, JSON API View
  models.py              # Model: SQLite schema + CRUD
  seed.py                # Hand-crafted sample movies (demo data)
  templates/index.html   # HTML View: page structure, no database access
  static/app.js          # fetch() calls to the /movies JSON API
  static/style.css       # page styling only
  requirements.txt       # Python dependencies
  README.md              # This file
  .gitignore
  movies.db              # Created automatically on first run (gitignored)
```

## Movie fields

| Field      | Type   | Required | Notes                |
|------------|--------|----------|----------------------|
| `id`       | int    | auto     | Primary key          |
| `title`    | string | yes      | Non-empty            |
| `year`     | int    | yes      | e.g. 2019            |
| `genre`    | string | yes      | Non-empty            |
| `director` | string | no       | Optional             |
| `rating`   | float  | no       | Between 1.0 and 10.0 |

## Setup

```bash
cd movies-api

# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate it
# macOS / Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Seed manually — also happens automatically on first run
python seed.py

# 5. Run the server
python app.py
```

The server listens on **http://127.0.0.1:5000**.

On first start, the app creates `movies.db`, builds the `movies` table, and seeds **14** original sample movies if the table is empty.

## Open the UI

With the server running, open **http://127.0.0.1:5000** in a browser.

You get a page to list movies, open one, add, edit, and delete.
The page does not read `movies.db` itself.
`static/app.js` calls the JSON API with `fetch` (`GET`, `POST`, `PUT`, and `DELETE` on `/movies`).

Open the site from the running server.
Do not double-click `templates/index.html`.
`fetch` only works on `http://127.0.0.1:5000`, where Flask serves the page.

`/movies` is still JSON.
The `curl` examples below work the same while the UI is open.

`curl http://127.0.0.1:5000/` still returns the JSON welcome.
A browser asks for HTML, so that same path shows the page.

## Endpoints

| Method   | Path            | Success | Error cases      |
|----------|-----------------|---------|------------------|
| `GET`    | `/movies`       | 200     | —                |
| `GET`    | `/movies/<id>`  | 200     | 404 not found    |
| `POST`   | `/movies`       | 201     | 400 bad body     |
| `PUT`    | `/movies/<id>`  | 200     | 400 / 404        |
| `DELETE` | `/movies/<id>`  | 200     | 404 not found    |

CORS stays on via `flask-cors`.
The bundled page is same-origin, so it does not need CORS.
A frontend on another origin can still call `/movies`.

---

## Sample `curl` commands

Assumes the server is running at `http://127.0.0.1:5000`.

### 1. List all movies — **200**

```bash
curl -i http://127.0.0.1:5000/movies
```

Expected: `HTTP/1.1 200 OK` and a JSON array of movies.

### 2. Get one movie — **200**

```bash
curl -i http://127.0.0.1:5000/movies/1
```

Expected: `HTTP/1.1 200 OK` and one movie object.

### 3. Get missing movie — **404**

```bash
curl -i http://127.0.0.1:5000/movies/9999
```

Expected: `HTTP/1.1 404 NOT FOUND`

```json
{"error": "Movie with id 9999 not found."}
```

### 4. Create a movie — **201**

```bash
curl -i -X POST http://127.0.0.1:5000/movies \
  -H "Content-Type: application/json" \
  -d '{"title":"Campus Lights","year":2026,"genre":"Drama","director":"Mara Dela Cruz","rating":8.0}'
```

Expected: `HTTP/1.1 201 CREATED` and the new movie (with an `id`).

### 5. Create with missing required fields — **400**

```bash
curl -i -X POST http://127.0.0.1:5000/movies \
  -H "Content-Type: application/json" \
  -d '{"title":"Incomplete Film"}'
```

Expected: `HTTP/1.1 400 BAD REQUEST`

```json
{"error": "Missing required field(s): year, genre."}
```

### 6. Update a movie — **200**

```bash
curl -i -X PUT http://127.0.0.1:5000/movies/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Midnight Lanterns (Director Cut)","year":2019,"genre":"Drama","director":"Elena Marquez","rating":8.5}'
```

Expected: `HTTP/1.1 200 OK` and the updated movie.

### 7. Update with bad body — **400**

```bash
curl -i -X PUT http://127.0.0.1:5000/movies/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Only Title"}'
```

Expected: `HTTP/1.1 400 BAD REQUEST` with a clear `error` message.

### 8. Update missing movie — **404**

```bash
curl -i -X PUT http://127.0.0.1:5000/movies/9999 \
  -H "Content-Type: application/json" \
  -d '{"title":"Ghost Film","year":2020,"genre":"Horror"}'
```

Expected: `HTTP/1.1 404 NOT FOUND`.

### 9. Delete a movie — **200**

```bash
curl -i -X DELETE http://127.0.0.1:5000/movies/14
```

Expected: `HTTP/1.1 200 OK`

```json
{"message": "Movie with id 14 deleted."}
```

### 10. Delete missing movie — **404**

```bash
curl -i -X DELETE http://127.0.0.1:5000/movies/9999
```

Expected: `HTTP/1.1 404 NOT FOUND`.

---

## Tips for students

- Always send `Content-Type: application/json` on `POST` and `PUT`.
- Required fields on create/update: **title**, **year**, **genre**.
- Optional fields: **director**, **rating** (1–10).
- To reset the database, stop the server, delete `movies.db`, then run `python app.py` again (or `python seed.py`).
- The browser UI and the `curl` commands use the same `/movies` routes.
- `/movies` stays JSON. HTML is only the page at `/` when a browser asks for it.

## License

Educational sample for Xavier Ateneo ITCC 14 coursework.
