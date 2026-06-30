/** Trang đăng ký tài khoản. */
import { useState } from "react";
import { Alert, Box, Button, Link, Stack, TextField, Typography } from "@mui/material";
import { Link as RouterLink, Navigate, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import AuthShell from "../components/AuthShell.jsx";
import { useAuth } from "../auth/AuthContext.jsx";
import { ApiError } from "../api/client.js";

export default function Register() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthed, register } = useAuth();
  const [form, setForm] = useState({ username: "", password: "", email: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  if (isAuthed) return <Navigate to="/" replace />;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register({
        username: form.username,
        password: form.password,
        email: form.email || undefined,
      });
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("common.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title={t("auth.register.title")}
      subtitle={t("auth.register.subtitle")}
      footer={
        <Typography variant="body2" color="text.secondary">
          {t("auth.register.hasAccount")}{" "}
          <Link component={RouterLink} to="/login">
            {t("auth.register.toLogin")}
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
            helperText={t("auth.hint.username")}
            autoFocus
            required
            fullWidth
          />
          <TextField
            label={t("auth.fields.password")}
            type="password"
            value={form.password}
            onChange={set("password")}
            helperText={t("auth.hint.password")}
            required
            fullWidth
          />
          <TextField
            label={t("auth.fields.email")}
            type="email"
            value={form.email}
            onChange={set("email")}
            fullWidth
          />
          <Button type="submit" variant="contained" size="large" disabled={busy} fullWidth>
            {t("auth.register.submit")}
          </Button>
        </Stack>
      </Box>
    </AuthShell>
  );
}
