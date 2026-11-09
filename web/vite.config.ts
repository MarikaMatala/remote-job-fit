// CODE MAP / COMMENTING GUIDE
// File purpose: Vite-kehityspalvelimen ja tuotantokoontiversion asetukset.
// Structure: tuonnit ja asetukset ensin, tyypit ja apufunktiot seuraavaksi, käynnistys ja tapahtumat lopuksi.

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
