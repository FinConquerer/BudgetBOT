/**
 * Context quản lý chế độ sáng/tối. Lưu lựa chọn vào localStorage và bọc ThemeProvider + CssBaseline.
 */
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { useTranslation } from "react-i18next";
import { buildTheme } from "./index.js";

const STORAGE_KEY = "bb-color-mode";
const ColorModeContext = createContext({ mode: "light", toggle: () => {} });

/** Hook tiêu dùng chế độ màu: trả { mode, toggle }. */
export function useColorMode() {
  return useContext(ColorModeContext);
}

function initialMode() {
  if (typeof window === "undefined") return "light";
  const saved = window.localStorage.getItem(STORAGE_KEY);
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

/** @param {{children: React.ReactNode}} props */
export default function ColorModeProvider({ children }) {
  const [mode, setMode] = useState(initialMode);
  const { i18n } = useTranslation();
  const language = i18n.language;

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, mode);
  }, [mode]);

  const ctx = useMemo(
    () => ({ mode, toggle: () => setMode((m) => (m === "dark" ? "light" : "dark")) }),
    [mode],
  );

  const theme = useMemo(() => buildTheme(mode, language), [mode, language]);

  return (
    <ColorModeContext.Provider value={ctx}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}
