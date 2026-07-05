import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/api": "http://localhost:8080",
      "/agent-api": {
        target: "http://localhost:8001",
        rewrite: (path) => path.replace(/^\/agent-api/, "")
      }
    }
  }
});
