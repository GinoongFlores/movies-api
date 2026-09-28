import { useState } from "react";

// Create and edit share this form.
// Submit builds the JSON body. App.jsx sends POST /movies or PUT /movies/<id>.

export default function MovieForm({ movie, error, saving, onSubmit, onCancel }) {
  const editing = movie != null;
  const [title, setTitle] = useState(movie ? movie.title : "");
  const [year, setYear] = useState(movie ? String(movie.year) : "");
  const [genre, setGenre] = useState(movie ? movie.genre : "");
  const [director, setDirector] = useState(movie && movie.director ? movie.director : "");
  const [rating, setRating] = useState(movie && movie.rating != null ? String(movie.rating) : "");

  function handleSubmit(event) {
    event.preventDefault();
    const directorValue = director.trim();
    const ratingValue = rating.trim();
    onSubmit(
      {
        title: title.trim(),
        year: Number(year),
        genre: genre.trim(),
        director: directorValue || null,
        rating: ratingValue === "" ? null : Number(ratingValue),
      },
      editing ? movie.id : null,
    );
  }

  return (
    <form onSubmit={handleSubmit} autoComplete="off">
      <p className="route">{editing ? `PUT /movies/${movie.id}` : "POST /movies"}</p>
      <h2 tabIndex={-1} autoFocus>{editing ? "Edit movie" : "Add a movie"}</h2>
      <p className="hint">Required: title, year, genre. The API returns 400 if those are missing or invalid.</p>
      <label>
        Title
        <input value={title} onChange={(event) => setTitle(event.target.value)} type="text" required />
      </label>
      <label>
        Year
        <input
          value={year}
          onChange={(event) => setYear(event.target.value)}
          type="number"
          inputMode="numeric"
          required
          min="1888"
          max="2100"
          step="1"
        />
      </label>
      <label>
        Genre
        <input value={genre} onChange={(event) => setGenre(event.target.value)} type="text" required />
      </label>
      <label>
        Director <span className="optional">optional</span>
        <input value={director} onChange={(event) => setDirector(event.target.value)} type="text" />
      </label>
      <label>
        Rating <span className="optional">optional, 1-10</span>
        <input
          value={rating}
          onChange={(event) => setRating(event.target.value)}
          type="number"
          inputMode="decimal"
          min="1"
          max="10"
          step="0.1"
        />
      </label>
      {error ? <p className="error">{error}</p> : null}
      <div className="actions">
        <button type="submit" className="btn" disabled={saving}>Save movie</button>
        <button type="button" className="btn secondary" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}
