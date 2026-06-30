/**
 * Dựng MUI theme cho BudgetBOT (light/dark) — port nguyên tắc từ budget-planner.
 * Token màu, typography, bo góc và component override tập trung tại đây để toàn app nhất quán.
 */
import { createTheme } from "@mui/material/styles";
import { viVN, enUS } from "@mui/material/locale";

const SANS = '"Public Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
export const MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace';

const BRAND = {
  primary: "#6366f1",
  success: "#10b981",
  warning: "#f59e0b",
  error: "#ef4444",
  info: "#2563eb",
};

function palette(mode) {
  const dark = mode === "dark";
  return {
    mode,
    primary: { main: BRAND.primary, contrastText: "#fff" },
    success: { main: BRAND.success },
    warning: { main: BRAND.warning },
    error: { main: BRAND.error },
    info: { main: BRAND.info },
    background: dark
      ? { default: "#0e1016", paper: "#171a22", subtle: "#21242f" }
      : { default: "#f8fafc", paper: "#ffffff", subtle: "#f4f6fa" },
    text: dark
      ? { primary: "#ffffff", secondary: "#c9d1d9", disabled: "#94a3b8" }
      : { primary: "#0f172a", secondary: "#475569", disabled: "#94a3b8" },
    divider: dark ? "#2a2f3a" : "#e2e8f0",
  };
}

/**
 * @param {"light"|"dark"} mode
 * @param {string} language - mã ngôn ngữ i18n hiện tại ("vi"|"en")
 */
export function buildTheme(mode, language) {
  const reducedMotion =
    typeof window !== "undefined" &&
    window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  const dark = mode === "dark";

  const theme = createTheme(
    {
      palette: palette(mode),
      motion: { reducedMotion: Boolean(reducedMotion) },
      customShadows: {
        dialog: dark
          ? "0 24px 60px rgba(0,0,0,0.6)"
          : "0 24px 60px rgba(15,23,42,0.18)",
      },
      typography: {
        fontFamily: SANS,
        h1: { fontWeight: 800, letterSpacing: "-0.028em" },
        h2: { fontWeight: 800, letterSpacing: "-0.024em" },
        h3: { fontWeight: 700, letterSpacing: "-0.02em" },
        h4: { fontWeight: 800, letterSpacing: "-0.018em" },
        h5: { fontWeight: 700, letterSpacing: "-0.014em" },
        h6: { fontWeight: 700, letterSpacing: "-0.012em" },
        button: { textTransform: "none", fontWeight: 600 },
      },
      shape: { borderRadius: 12 },
      components: {
        MuiButton: {
          defaultProps: { disableElevation: true },
          styleOverrides: {
            root: {
              textTransform: "none",
              fontWeight: 600,
              borderRadius: 8,
              ...(reducedMotion
                ? {}
                : {
                    transition: "transform .15s ease, box-shadow .15s ease",
                    "&:hover:not(.no-hover-lift):not([data-no-hover-lift])": {
                      transform: "translateY(-1px)",
                    },
                  }),
            },
          },
        },
        MuiTextField: { defaultProps: { size: "small" } },
        MuiOutlinedInput: {
          styleOverrides: {
            root: {
              borderRadius: 8,
              "& .MuiOutlinedInput-notchedOutline": { borderWidth: 1.25 },
              "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                borderWidth: 1.5,
                borderColor: BRAND.primary,
              },
            },
            input: { "&::placeholder": { opacity: 0.72 } },
          },
        },
        MuiPaper: { styleOverrides: { root: { backgroundImage: "none" } } },
        MuiDialog: {
          styleOverrides: {
            paper: {
              borderRadius: 12,
              boxShadow: dark
                ? "0 24px 60px rgba(0,0,0,0.6)"
                : "0 24px 60px rgba(15,23,42,0.18)",
            },
          },
        },
        MuiDialogActions: {
          styleOverrides: {
            root: (themeArg) => ({
              borderTop: `1px solid ${themeArg.theme.palette.divider}`,
              padding: "12px 24px",
              gap: 8,
              justifyContent: "flex-end",
            }),
          },
        },
        MuiBackdrop: {
          styleOverrides: {
            root: reducedMotion ? {} : { backdropFilter: "blur(6px)" },
          },
        },
        MuiChip: {
          styleOverrides: {
            sizeSmall: { height: "auto", minHeight: 22, paddingTop: 1, paddingBottom: 1 },
          },
        },
        MuiTableCell: {
          styleOverrides: { head: { fontWeight: 700, fontSize: 13 } },
        },
        MuiTooltip: { styleOverrides: { tooltip: { borderRadius: 6 } } },
      },
    },
    language === "en" ? enUS : viVN,
  );

  return theme;
}
