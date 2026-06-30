/** API xác thực: đăng ký, đăng nhập (lưu access token), lấy thông tin người dùng. */
import { apiFetch, setAccessToken, clearAuth } from "./client.js";

/** @param {{username:string, password:string, email?:string}} body */
export function register(body) {
  return apiFetch("/auth/register", { method: "POST", body: JSON.stringify(body) });
}

/** Đăng nhập, lưu token, trả về LoginResponse. @param {{username:string, password:string}} body */
export async function login(body) {
  const res = await apiFetch("/auth/login", { method: "POST", body: JSON.stringify(body) });
  setAccessToken(res.access_token);
  return res;
}

export function getMe() {
  return apiFetch("/auth/me");
}

export function logout() {
  clearAuth();
}
