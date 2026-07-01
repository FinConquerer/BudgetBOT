import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Cấu hình Vite cho frontend BudgetBOT.
// Proxy /api -> backend FastAPI khi dev để tránh cấu hình CORS phức tạp.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
