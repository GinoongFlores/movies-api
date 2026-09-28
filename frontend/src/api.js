/*
  fetch helper for the React demo.

  This file is not the Controller and not the Model.
  It only talks to the Flask JSON API.

  The page is http://127.0.0.1:5173 (Vite).
  The API is http://127.0.0.1:5000 (Flask).
  Different ports are different origins, so the browser applies CORS.
  app.py turns CORS on with flask-cors. That is why POST and PUT work.

  The vanilla twin (static/app.js) uses relative /movies instead, because
  Flask serves that page on the same port as the API.
*/

export const API_ORIGIN = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export async function api(path, options = {}) {
  const response = await fetch(`${API_ORIGIN}${path}`, {
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

export function formatRating(rating) {
  if (rating == null || rating === "") return "-";
  return Number(rating).toFixed(1);
}
