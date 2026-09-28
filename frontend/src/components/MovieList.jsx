import { formatRating } from "../api.js";

// Draws the list. It does not call fetch.
// App.jsx loads GET /movies and passes the array in.

export default function MovieList({ movies, selectedId, status, onSelect, onAdd }) {
  return (
    <section aria-labelledby="library-heading">
      <div className="section-head">
        <div>
          <h2 id="library-heading">Library</h2>
          <p className="hint" aria-live="polite">{status}</p>
        </div>
        <button className="btn" type="button" onClick={onAdd}>Add movie</button>
      </div>
      <ul className="catalog">
        {movies.map((movie) => {
          const selected = movie.id === selectedId;
          const meta = [movie.genre, movie.year, movie.director].filter(Boolean).join(" · ");
          return (
            <li key={movie.id}>
              <button
                type="button"
                className={selected ? "row is-selected" : "row"}
                aria-current={selected ? "true" : "false"}
                onClick={() => onSelect(movie.id)}
              >
                <span className="rating">{formatRating(movie.rating)}</span>
                <span className="row-body">
                  <span className="row-title">{movie.title}</span>
                  <span className="row-meta">{meta}</span>
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
