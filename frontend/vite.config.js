import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server only. The API stays on Flask (port 5000).
// We do not proxy /movies. Fetch goes to port 5000 so students see CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
  },
});
