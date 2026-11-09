// CODE MAP / COMMENTING GUIDE
// File purpose: Vite-kehityspalvelimen ja tuotantokoontiversion asetukset.
// Structure: imports and settings first, followed by types and helper functions, with initialization and event handlers last.

import { defineConfig } from "vite";

export default defineConfig({
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: false
      }
    }
  }
});
