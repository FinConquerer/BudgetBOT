/**
 * Quản lý phiên đăng nhập. Đăng nhập là TUỲ CHỌN trong BudgetBOT: Planner và Trợ lý
 * dùng được khi chưa đăng nhập; đăng nhập mở thêm tính năng lưu kế hoạch/lịch sử.
 */
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import * as authApi from "../api/auth.js";
import { getAccessToken, setUnauthorizedHandler } from "../api/client.js";

const AuthContext = createContext(null);

/** Hook tiêu dùng: { status, user, isAuthed, login, register, logout, reload }. */
export function useAuth() {
  return useContext(AuthContext);
}

/** @param {{children: React.ReactNode}} props */
export default function AuthProvider({ children }) {
  const [status, setStatus] = useState("loading"); // loading | authed | anon
  const [user, setUser] = useState(null);

  async function loadSession() {
    try {
      const me = await authApi.getMe();
      setUser(me);
      setStatus("authed");
    } catch {
      authApi.logout();
      setUser(null);
      setStatus("anon");
    }
  }

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setUser(null);
      setStatus("anon");
    });
    if (getAccessToken()) loadSession();
    else setStatus("anon");
  }, []);

  async function login(credentials) {
    const res = await authApi.login(credentials);
    setUser(res.user);
    setStatus("authed");
    return res;
  }

  async function register(body) {
    await authApi.register(body);
    return login({ username: body.username, password: body.password });
  }

  function logout() {
    authApi.logout();
    setUser(null);
    setStatus("anon");
  }

  const value = useMemo(
    () => ({ status, user, isAuthed: status === "authed", login, register, logout, reload: loadSession }),
    [status, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
