import { formatRating } from "../api.js";

// One movie, already loaded by App.jsx via GET /movies/<id>.
// Edit and Delete only report the click. They do not send HTTP themselves.

export default function MovieDetail({ movie, note, error, onEdit, onDelete }) {
  const rating = movie.rating == null ? "-" : `${formatRating(movie.rating)} / 10`;
  return (
    <article className="detail">
      <p className="route">GET /movies/{movie.id}</p>
      <h2 tabIndex={-1} autoFocus>{movie.title}</h2>
      <p className="meta">
        <span>{movie.genre}</span>
        <span>{movie.year}</span>
      </p>
      <dl>
        <div>
          <dt>Director</dt>
          <dd>{movie.director || "-"}</dd>
        </div>
        <div>
          <dt>Rating</dt>
          <dd>{rating}</dd>
        </div>
        <div>
          <dt>Id</dt>
          <dd>{movie.id}</dd>
        </div>
      </dl>
      {note ? <p className="ok">{note}</p> : null}
      {error ? <p className="error">{error}</p> : null}
      <div className="actions">
        <button type="button" className="btn" onClick={() => onEdit(movie)}>Edit</button>
        <button type="button" className="btn danger" onClick={() => onDelete(movie)}>Delete</button>
      </div>
    </article>
  );
}
