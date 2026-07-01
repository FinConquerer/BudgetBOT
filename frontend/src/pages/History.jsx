/** Lịch sử kế hoạch đã lưu (cần đăng nhập): danh sách + xoá. */
import { useEffect, useRef, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Grid,
  IconButton,
  Paper,
  Skeleton,
  Stack,
  Typography,
  useTheme,
} from "@mui/material";
import { TrashIcon, ClockIcon } from "@heroicons/react/24/outline";
import { Link as RouterLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import PageHeader from "../components/PageHeader.jsx";
import EmptyState from "../components/EmptyState.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import { useAuth } from "../auth/AuthContext.jsx";
import { listSavedPlans, deleteSavedPlan } from "../api/plans.js";
import { ApiError } from "../api/client.js";
import { formatVnd } from "../utils/format.js";
import { MONO } from "../theme/index.js";
import { useStaggerIn } from "../utils/gsap.js";

export default function History() {
  const { t, i18n } = useTranslation();
  const theme = useTheme();
  const { isAuthed } = useAuth();
  const rootRef = useRef(null);
  useStaggerIn(rootRef, theme);

  const [items, setItems] = useState(null);
  const [error, setError] = useState("");
  const [target, setTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);

  async function load() {
    try {
      const res = await listSavedPlans({ limit: 50 });
      setItems(res.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("common.error"));
    }
  }

  useEffect(() => {
    if (isAuthed) load();
  }, [isAuthed]);

  async function confirmDelete() {
    if (!target) return;
    setDeleting(true);
    try {
      await deleteSavedPlan(target.id);
      setItems((list) => list.filter((p) => p.id !== target.id));
      setTarget(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("common.error"));
    } finally {
      setDeleting(false);
    }
  }

  if (!isAuthed) {
    return (
      <Box ref={rootRef}>
        <PageHeader title={t("history.title")} description={t("history.subtitle")} />
        <EmptyState
          icon={<ClockIcon />}
          title={t("history.loginRequired.title")}
          description={t("history.loginRequired.description")}
          action={
            <Button variant="contained" component={RouterLink} to="/login">
              {t("topbar.login")}
            </Button>
          }
        />
      </Box>
    );
  }

  return (
    <Box ref={rootRef}>
      <PageHeader title={t("history.title")} description={t("history.subtitle")} />

      {error && (
        <Alert severity="error" onClose={() => setError("")} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {items == null ? (
        <Stack spacing={1.5}>
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} variant="rounded" height={84} />
          ))}
        </Stack>
      ) : items.length === 0 ? (
        <EmptyState
          icon={<ClockIcon />}
          title={t("history.empty.title")}
          description={t("history.empty.description")}
          action={
            <Button variant="contained" component={RouterLink} to="/planner">
              {t("nav.planner")}
            </Button>
          }
        />
      ) : (
        <Stack spacing={1.5}>
          {items.map((p) => (
            <Paper key={p.id} sx={{ p: 2, borderRadius: 3 }} className="gsap-in">
              <Grid container alignItems="center" spacing={1}>
                <Grid item xs={12} sm={5}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                    {p.financial_goal || t("history.noGoal")}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {t("history.createdAt")}: {new Date(p.created_at).toLocaleDateString(i18n.language)}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" color="text.secondary">
                    {t("history.income")}
                  </Typography>
                  <Typography sx={{ fontFamily: MONO, fontVariantNumeric: "tabular-nums" }}>
                    {formatVnd(p.monthly_income)}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" color="text.secondary">
                    {t("history.surplus")}
                  </Typography>
                  <Typography
                    sx={{ fontFamily: MONO, fontVariantNumeric: "tabular-nums" }}
                    color={p.monthly_surplus >= 0 ? "success.main" : "error.main"}
                  >
                    {formatVnd(p.monthly_surplus)}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={1} sx={{ textAlign: "right" }}>
                  <IconButton color="error" onClick={() => setTarget(p)} aria-label="delete">
                    <TrashIcon style={{ width: 20, height: 20 }} />
                  </IconButton>
                </Grid>
              </Grid>
            </Paper>
          ))}
        </Stack>
      )}

      <ConfirmDialog
        open={Boolean(target)}
        onClose={() => setTarget(null)}
        onConfirm={confirmDelete}
        confirming={deleting}
        title={t("history.confirmDelete.title")}
        description={t("history.confirmDelete.description")}
      />
    </Box>
  );
}
