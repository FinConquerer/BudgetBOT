/**
 * HTTP client dùng chung. fetch thuần, tự gắn JWT Bearer, đọc lỗi FastAPI (detail),
 * 401 -> xoá token + gọi handler đăng xuất. BudgetBOT không có khái niệm "space".
 */
const BASE = import.meta.env.VITE_API_BASE ?? "/api";
const ACCESS_KEY = "bb-access";

export function getAccessToken() {
  return typeof window !== "undefined" ? window.localStorage.getItem(ACCESS_KEY) : null;
}
export function setAccessToken(token) {
  if (token) window.localStorage.setItem(ACCESS_KEY, token);
}
export function clearAuth() {
  window.localStorage.removeItem(ACCESS_KEY);
}

/** Lỗi API mang theo HTTP status. */
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function extractMessage(body) {
  const detail = body?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  return null;
}

let onUnauthorized = () => {};
/** AuthProvider đăng ký handler để auto-logout khi gặp 401. */
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn || (() => {});
}

/**
 * Gọi API. Tự gắn JSON + Bearer. Trả về JSON (hoặc null khi 204).
 * @param {string} path - đường dẫn sau BASE, ví dụ "/plan"
 * @param {RequestInit} [options]
 */
export async function apiFetch(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getAccessToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401 && !path.startsWith("/auth/")) {
    clearAuth();
    onUnauthorized();
    throw new ApiError("Phiên đăng nhập đã hết hạn.", 401);
  }

  if (res.status === 204) return null;

  let body = null;
  try {
    body = await res.json();
  } catch {
    body = null;
  }

  if (!res.ok) {
    throw new ApiError(extractMessage(body) || `HTTP ${res.status}`, res.status);
  }
  return body;
}
