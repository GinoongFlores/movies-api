import { useEffect, useState } from "react";
import { API_ORIGIN, api } from "./api.js";
import MovieDetail from "./components/MovieDetail.jsx";
import MovieForm from "./components/MovieForm.jsx";
import MovieList from "./components/MovieList.jsx";

/*
  Screen state and the fetch calls live here.

  MovieList, MovieDetail, and MovieForm only render what they are given.
  Compare with static/app.js, where one file both calls the API and rewrites the DOM.

  Routes (same as curl):
    GET    /movies
    GET    /movies/<id>
    POST   /movies
    PUT    /movies/<id>
    DELETE /movies/<id>
*/

export default function App() {
  const [movies, setMovies] = useState([]);
  const [status, setStatus] = useState("Loading movies…");
  const [selectedId, setSelectedId] = useState(null);
  const [panel, setPanel] = useState({ type: "empty" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function loadMovies() {
    setStatus("Loading movies…");
    try {
      const data = await api("/movies");
      setMovies(data);
      setStatus(
        data.length
          ? `${data.length} ${data.length === 1 ? "movie" : "movies"}`
          : "No movies yet. Add one.",
      );
    } catch (err) {
      setStatus(err.message);
    }
  }

  useEffect(() => {
    loadMovies();
  }, []);

  async function openMovie(id) {
    setSelectedId(id);
    setError("");
    try {
      const movie = await api(`/movies/${id}`);
      setPanel({ type: "detail", movie, note: "" });
    } catch (err) {
      setSelectedId(null);
      setPanel({ type: "message", text: err.message });
    }
  }

  function startCreate() {
    setSelectedId(null);
    setError("");
    setPanel({ type: "form", movie: null });
  }

  function startEdit(movie) {
    setError("");
    setPanel({ type: "form", movie });
  }

  function cancelForm(movie) {
    setError("");
    if (movie) openMovie(movie.id);
    else setPanel({ type: "empty" });
  }

  async function saveMovie(payload, id) {
    setError("");
    setSaving(true);
    try {
      const movie = id == null
        ? await api("/movies", { method: "POST", body: JSON.stringify(payload) })
        : await api(`/movies/${id}`, { method: "PUT", body: JSON.stringify(payload) });
      setSelectedId(movie.id);
      setPanel({ type: "detail", movie, note: "Saved." });
      await loadMovies();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function removeMovie(movie) {
    const ok = window.confirm(`Delete "${movie.title}"? This calls DELETE /movies/${movie.id}.`);
    if (!ok) return;
    setError("");
    try {
      await api(`/movies/${movie.id}`, { method: "DELETE" });
      setSelectedId(null);
      setPanel({ type: "message", text: `Deleted "${movie.title}".` });
      await loadMovies();
    } catch (err) {
      setError(err.message);
    }
  }

  let panelNode = <p className="panel-empty">Select a movie, or add one.</p>;
  if (panel.type === "detail") {
    panelNode = (
      <MovieDetail
        movie={panel.movie}
        note={panel.note}
        error={error}
        onEdit={startEdit}
        onDelete={removeMovie}
      />
    );
  } else if (panel.type === "form") {
    panelNode = (
      <MovieForm
        key={panel.movie ? panel.movie.id : "new"}
        movie={panel.movie}
        error={error}
        saving={saving}
        onSubmit={saveMovie}
        onCancel={() => cancelForm(panel.movie)}
      />
    );
  } else if (panel.type === "message") {
    panelNode = <p className="panel-empty">{panel.text}</p>;
  }

  return (
    <>
      <header className="top">
        <div className="wrap top-inner">
          <div>
            <p className="eyebrow">ITCC 14 · React demo</p>
            <h1>Movies</h1>
          </div>
          <p className="lede">
            Components call the Flask API at {API_ORIGIN}. They do not read the database.
            Compare with the <a href={`${API_ORIGIN}/vanilla`}>vanilla twin</a>.
          </p>
        </div>
      </header>
      <main className="wrap layout">
        <MovieList
          movies={movies}
          selectedId={selectedId}
          status={status}
          onSelect={openMovie}
          onAdd={startCreate}
        />
        <aside className="panel" aria-live="polite">{panelNode}</aside>
      </main>
      <footer className="wrap lesson">
        <details>
          <summary>Why these are separate components</summary>
          <p><code>MovieList</code> only draws the list. <code>MovieDetail</code> only draws one movie. <code>MovieForm</code> only draws the form.</p>
          <p><code>App.jsx</code> calls the API with <code>fetch</code>. The components do not import <code>models.py</code> and do not talk to SQLite.</p>
          <p>The vanilla twin at <a href={`${API_ORIGIN}/vanilla`}>/vanilla</a> does the same CRUD in one HTML file plus <code>static/app.js</code>.</p>
        </details>
      </footer>
    </>
  );
}
