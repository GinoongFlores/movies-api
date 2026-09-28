# Movies REST API

Flask + Python + SQLite sample project for **Xavier Ateneo ITCC 14**.

A small JSON REST API for a `movies` resource.
The main browser demo is a React app that calls it with `fetch`.
A vanilla HTML/JS page does the same CRUD so you can compare.

`curl`, Bruno, and Postman still talk to JSON `/movies`.
The browser pages do not read `movies.db`.

## Run the React demo

Use two terminals. Both stay open during class.

```bash
cd movies-api

# Terminal 1: the API
python3 -m venv .venv
source .venv/bin/activate
# Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

The API listens on **http://127.0.0.1:5000**.

On first start it creates `movies.db` and seeds **14** sample movies if the table is empty.

```bash
# Terminal 2: the React UI
cd frontend
npm install
npm run dev
```

Open **http://127.0.0.1:5173**.

You get a page to list movies, open one, add, edit, and delete.
React is on port 5173. Flask is on port 5000.
Those are different origins, so the browser applies CORS.
`flask-cors` in `app.py` allows the React page to call `/movies`.

If the API is not on `http://127.0.0.1:5000`, set `VITE_API_URL` before `npm run dev`.
Do not open the React files from disk. `fetch` needs both servers running.

## Why React components for an API UI

Components split the screen into pieces that each draw one thing.
The API does not change. Every action is still `fetch` to `/movies`.
`App.jsx` asks for data. `MovieList`, `MovieDetail`, and `MovieForm` only render what they are given.
The vanilla twin does that same job in one script that both calls the API and rewrites the page.

- React: one component per piece of the screen. The `fetch` calls sit in `App.jsx`.
- Vanilla: `templates/index.html` plus `static/app.js`. That script finds nodes and fills them after each response.
- Both talk only to the JSON API. Neither imports `models.py`.

## Vanilla twin

With the API running, open **http://127.0.0.1:5000/vanilla**.

Same list, detail, create, edit, and delete.
`static/app.js` calls relative `/movies` because Flask serves that page on port 5000.
Same origin, so that page does not need CORS.

A browser that opens **http://127.0.0.1:5000/** sees a short pointer to the React app and to `/vanilla`.
It does not list movies.

`curl http://127.0.0.1:5000/` still returns the JSON welcome.
`curl` to `/movies` is unchanged. See the examples below.

## How this maps to MVC

This sample is organized for lecture use around **Model–View–Controller**:

| MVC piece | In this project | Job |
|-----------|-----------------|-----|
| **Model** | `models.py` (+ `movies.db`) | Schema, SQLite, CRUD helpers. No HTTP. |
| **View** | JSON from `jsonify(...)` on `/movies`. React components and `/vanilla` are clients of that JSON. | The API View stays JSON. Browser UIs call it. They do not read the database. |
| **Controller** | Route handlers in `app.py` | Read the request, validate, call the Model, choose status code, return JSON. |

**Typical request flow (example: `POST /movies`):**

1. Client sends HTTP + JSON body → Flask routes it to a function in `app.py` (**Controller**).
2. Controller validates required fields (`title`, `year`, `genre`). Bad input → **400** (never touches the DB).
3. Controller calls `create_movie(...)` in `models.py` (**Model**) to INSERT into SQLite.
4. Controller returns `jsonify(movie)` with **201**.
   That JSON body is the **API View**.

**Browser path (React, the main demo):**

1. You open `http://127.0.0.1:5173`.
   Vite serves the React page. Flask is not rendering that HTML.
2. `App.jsx` runs `fetch("http://127.0.0.1:5000/movies")`.
   That is a normal `GET /movies`, the same request as curl, from another port.
3. The Controller and Model handle it as before and return JSON (API View).
   CORS lets the browser read that response.
4. `MovieList` turns that JSON into rows.
   Create, edit, and delete are `POST`, `PUT`, and `DELETE` the same way.

The vanilla page at `/vanilla` does steps 2 to 4 inside `static/app.js` instead of components.

`seed.py` is starter data for demos (hand-crafted, not from an external movie API). It uses the same Model helpers as a real create request.

## Project layout

```
movies-api/
  app.py                         # Controller: routes, validation, JSON API View
  models.py                      # Model: SQLite schema + CRUD
  seed.py                        # Hand-crafted sample movies (demo data)
  frontend/                      # React demo (Vite). Main UI students open.
    src/App.jsx                  # fetch calls and screen state
    src/api.js                   # fetch helper. API origin is port 5000.
    src/components/MovieList.jsx
    src/components/MovieDetail.jsx
    src/components/MovieForm.jsx
  templates/home.html            # Browser GET / : pointer to React and /vanilla
  templates/index.html           # Vanilla twin, served at /vanilla
  static/app.js                  # Vanilla fetch() calls, one file
  static/style.css               # Shared look for the Flask pages
  requirements.txt               # Python dependencies
  README.md
  .gitignore
  movies.db                      # Created on first run (gitignored)
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

## Endpoints

| Method   | Path            | Success | Error cases      |
|----------|-----------------|---------|------------------|
| `GET`    | `/movies`       | 200     | —                |
| `GET`    | `/movies/<id>`  | 200     | 404 not found    |
| `POST`   | `/movies`       | 201     | 400 bad body     |
| `PUT`    | `/movies/<id>`  | 200     | 400 / 404        |
| `DELETE` | `/movies/<id>`  | 200     | 404 not found    |

CORS stays on via `flask-cors`.
The React app on port 5173 needs it.
The vanilla page at `/vanilla` is same-origin and does not.

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
- The React app, the vanilla page, and the `curl` commands use the same `/movies` routes.
- `/movies` stays JSON.
- Open the React demo at `http://127.0.0.1:5173`.
  The vanilla twin is `http://127.0.0.1:5000/vanilla`.

## License

Educational sample for Xavier Ateneo ITCC 14 coursework.
