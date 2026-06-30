/** Trang đăng nhập. */
import { useState } from "react";
import { Alert, Box, Button, Link, Stack, TextField, Typography } from "@mui/material";
import { Link as RouterLink, Navigate, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import AuthShell from "../components/AuthShell.jsx";
import { useAuth } from "../auth/AuthContext.jsx";
import { ApiError } from "../api/client.js";

export default function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthed, login } = useAuth();
  const [form, setForm] = useState({ username: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  if (isAuthed) return <Navigate to="/" replace />;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(form);
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("common.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title={t("auth.login.title")}
      subtitle={t("auth.login.subtitle")}
      footer={
        <Typography variant="body2" color="text.secondary">
          {t("auth.login.noAccount")}{" "}
          <Link component={RouterLink} to="/register">
            {t("auth.login.toRegister")}
          </Link>
        </Typography>
      }
    >
      <Box component="form" onSubmit={handleSubmit}>
        <Stack spacing={2}>
          {error && (
            <Alert severity="error" onClose={() => setError("")}>
              {error}
            </Alert>
          )}
          <TextField
            label={t("auth.fields.username")}
            value={form.username}
            onChange={set("username")}
            autoFocus
            required
            fullWidth
          />
          <TextField
            label={t("auth.fields.password")}
            type="password"
            value={form.password}
            onChange={set("password")}
            required
            fullWidth
          />
          <Button type="submit" variant="contained" size="large" disabled={busy} fullWidth>
            {t("auth.login.submit")}
          </Button>
          <Box sx={{ textAlign: "right" }}>
            <Link component={RouterLink} to="/forgot-password" variant="body2">
              {t("auth.login.forgot")}
            </Link>
          </Box>
        </Stack>
      </Box>
    </AuthShell>
  );
}
