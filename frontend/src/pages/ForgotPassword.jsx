/** Trang quên mật khẩu: xác minh username + email rồi đặt mật khẩu mới. */
import { useState } from "react";
import { Alert, Box, Button, Link, Stack, TextField, Typography } from "@mui/material";
import { Link as RouterLink, Navigate, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import AuthShell from "../components/AuthShell.jsx";
import { useAuth } from "../auth/AuthContext.jsx";
import { resetPassword } from "../api/auth.js";
import { ApiError } from "../api/client.js";

export default function ForgotPassword() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthed } = useAuth();
  const [form, setForm] = useState({ username: "", email: "", new_password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  if (isAuthed) return <Navigate to="/" replace />;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await resetPassword(form);
      setDone(true);
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("common.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title={t("auth.forgot.title")}
      subtitle={t("auth.forgot.subtitle")}
      footer={
        <Typography variant="body2" color="text.secondary">
          <Link component={RouterLink} to="/login">
            {t("auth.forgot.backToLogin")}
          </Link>
        </Typography>
      }
    >
      <Box component="form" onSubmit={handleSubmit}>
        <Stack spacing={2}>
          {done ? (
            <Alert severity="success">{t("auth.forgot.success")}</Alert>
          ) : (
            <>
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
                label={t("auth.fields.emailRequired")}
                type="email"
                value={form.email}
                onChange={set("email")}
                helperText={t("auth.forgot.emailHint")}
                required
                fullWidth
              />
              <TextField
                label={t("auth.forgot.newPassword")}
                type="password"
                value={form.new_password}
                onChange={set("new_password")}
                helperText={t("auth.hint.password")}
                required
                fullWidth
              />
              <Button type="submit" variant="contained" size="large" disabled={busy} fullWidth>
                {t("auth.forgot.submit")}
              </Button>
            </>
          )}
        </Stack>
      </Box>
    </AuthShell>
  );
}
