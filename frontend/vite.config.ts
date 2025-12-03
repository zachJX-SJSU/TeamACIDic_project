import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// If you want to avoid CORS in dev, you can add a proxy here later.
// For now we just talk directly to http://localhost:8000 from axios.

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
});
