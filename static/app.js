/*
  Frontend for the Movies REST API.

  This file is not the Controller and not the Model.
    Controller  app.py       /movies routes still return JSON.
    Model       models.py    SQLite. This file never imports it.
    API View    jsonify()    What fetch() receives.
    HTML View   index.html   Page structure. This script fills it in.

  fetch() is this page talking to the same routes as curl:
    GET    /movies
    GET    /movies/<id>
    POST   /movies
    PUT    /movies/<id>
    DELETE /movies/<id>
*/

const listEl = document.querySelector("#movie-list");
const panelEl = document.querySelector("#panel");
const listStatusEl = document.querySelector("#list-status");
const addBtn = document.querySelector("#add-btn");

const cardTemplate = document.querySelector("#card-template");
const detailTemplate = document.querySelector("#detail-template");
const formTemplate = document.querySelector("#form-template");

let selectedId = null;

addBtn.addEventListener("click", () => showForm(null));

listEl.addEventListener("click", (event) => {
  const button = event.target.closest("[data-id]");
  if (!button) return;
  showDetail(Number(button.dataset.id));
});

loadMovies();

async function loadMovies() {
  listStatusEl.textContent = "Loading movies…";
  try {
    const movies = await api("/movies");
    renderList(movies);
    listStatusEl.textContent = movies.length
      ? `${movies.length} ${movies.length === 1 ? "movie" : "movies"}`
      : "No movies yet. Add one.";
  } catch (error) {
    listStatusEl.textContent = error.message;
  }
}

function renderList(movies) {
  listEl.replaceChildren();
  for (const movie of movies) {
    const node = cardTemplate.content.cloneNode(true);
    const button = node.querySelector("[data-id]");
    button.dataset.id = String(movie.id);
    button.classList.toggle("is-selected", movie.id === selectedId);
    button.setAttribute("aria-current", movie.id === selectedId ? "true" : "false");
    text(button, "title", movie.title);
    text(button, "rating", formatRating(movie.rating));
    const meta = [movie.genre, movie.year, movie.director].filter(Boolean);
    text(button, "meta", meta.join(" · "));
    listEl.append(node);
  }
}

function highlightSelection() {
  for (const button of listEl.querySelectorAll("[data-id]")) {
    const on = Number(button.dataset.id) === selectedId;
    button.classList.toggle("is-selected", on);
    button.setAttribute("aria-current", on ? "true" : "false");
  }
}

async function showDetail(id) {
  selectedId = id;
  highlightSelection();
  try {
    const movie = await api(`/movies/${id}`);
    renderDetail(movie);
  } catch (error) {
    selectedId = null;
    highlightSelection();
    showMessage(error.message);
  }
}

function renderDetail(movie, note) {
  const node = detailTemplate.content.cloneNode(true);
  const root = node.querySelector(".detail");
  text(root, "route", `GET /movies/${movie.id}`);
  text(root, "title", movie.title);
  text(root, "year", String(movie.year));
  text(root, "genre", movie.genre);
  text(root, "director", movie.director || "-");
  text(root, "rating", movie.rating == null ? "-" : `${Number(movie.rating).toFixed(1)} / 10`);
  text(root, "id", String(movie.id));
  if (note) {
    const status = root.querySelector("[data-field='status']");
    status.hidden = false;
    status.textContent = note;
  }
  root.querySelector("[data-action='edit']").addEventListener("click", () => showForm(movie));
  root.querySelector("[data-action='delete']").addEventListener("click", () => removeMovie(movie));
  panelEl.replaceChildren(node);
  root.querySelector("h2").focus();
}

function showForm(movie) {
  const editing = movie != null;
  selectedId = editing ? movie.id : null;
  highlightSelection();

  const node = formTemplate.content.cloneNode(true);
  const form = node.querySelector("form");
  text(form, "route", editing ? `PUT /movies/${movie.id}` : "POST /movies");
  text(form, "heading", editing ? "Edit movie" : "Add a movie");

  if (editing) {
    form.elements.title.value = movie.title;
    form.elements.year.value = movie.year;
    form.elements.genre.value = movie.genre;
    form.elements.director.value = movie.director || "";
    form.elements.rating.value = movie.rating == null ? "" : movie.rating;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    saveMovie(form, editing ? movie.id : null);
  });
  form.querySelector("[data-action='cancel']").addEventListener("click", () => {
    if (editing) showDetail(movie.id);
    else {
      selectedId = null;
      highlightSelection();
      showMessage("Select a movie, or add one.");
    }
  });

  panelEl.replaceChildren(node);
  form.querySelector("h2").focus();
}

async function saveMovie(form, id) {
  const errorEl = form.querySelector("[data-field='error']");
  errorEl.hidden = true;
  const submit = form.querySelector("[type='submit']");
  submit.disabled = true;

  try {
    const payload = readForm(form);
    const movie = id == null
      ? await api("/movies", { method: "POST", body: JSON.stringify(payload) })
      : await api(`/movies/${id}`, { method: "PUT", body: JSON.stringify(payload) });
    selectedId = movie.id;
    renderDetail(movie, "Saved.");
    await loadMovies();
  } catch (error) {
    errorEl.hidden = false;
    errorEl.textContent = error.message;
    submit.disabled = false;
  }
}

async function removeMovie(movie) {
  const ok = window.confirm(`Delete "${movie.title}"? This calls DELETE /movies/${movie.id}.`);
  if (!ok) return;
  try {
    await api(`/movies/${movie.id}`, { method: "DELETE" });
    selectedId = null;
    showMessage(`Deleted "${movie.title}".`);
    addBtn.focus();
    await loadMovies();
  } catch (error) {
    const errorEl = panelEl.querySelector("[data-field='error']");
    if (errorEl) {
      errorEl.hidden = false;
      errorEl.textContent = error.message;
    } else {
      showMessage(error.message);
    }
  }
}

function readForm(form) {
  const director = form.elements.director.value.trim();
  const ratingRaw = form.elements.rating.value.trim();
  return {
    title: form.elements.title.value.trim(),
    year: Number(form.elements.year.value),
    genre: form.elements.genre.value.trim(),
    director: director || null,
    rating: ratingRaw === "" ? null : Number(ratingRaw),
  };
}

function showMessage(message) {
  panelEl.replaceChildren();
  const p = document.createElement("p");
  p.className = "panel-empty";
  p.textContent = message;
  panelEl.append(p);
}

function text(root, name, value) {
  root.querySelector(`[data-field='${name}']`).textContent = value;
}

function formatRating(rating) {
  if (rating == null) return "-";
  return Number(rating).toFixed(1);
}

async function api(path, options = {}) {
  // Accept: application/json asks for the API View (JSON), not the HTML page.
  const response = await fetch(path, {
    cache: "no-store",
    ...options,
    headers: {
      Accept: "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {}),
    },
  });

  const body = await response.text();
  let data = null;
  if (body) {
    try {
      data = JSON.parse(body);
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    const message = data && data.error ? data.error : `Request failed (${response.status}).`;
    throw new Error(message);
  }
  return data;
}
