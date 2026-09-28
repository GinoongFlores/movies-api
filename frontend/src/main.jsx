import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

// No StrictMode. In dev it runs effects twice, so GET /movies would fire
// twice and the network tab would not match the lesson.
createRoot(document.getElementById("root")).render(<App />);
