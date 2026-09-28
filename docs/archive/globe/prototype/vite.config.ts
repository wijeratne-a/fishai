import { defineConfig } from "vite";

export default defineConfig({
  optimizeDeps: {
    exclude: ["maplibre-gl"],
  },
  worker: {
    format: "es",
  },
  server: {
    port: 5173,
    strictPort: true,
  },
  preview: {
    port: 4173,
  },
  build: {
    sourcemap: true,
    target: "es2022",
  },
});
