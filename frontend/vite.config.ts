import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy /api -> backend FastAPI khi dev (tránh cấu hình CORS phức tạp).
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
