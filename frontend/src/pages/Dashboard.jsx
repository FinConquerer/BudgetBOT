/** Trang chính: lời chào, vài chỉ số nhanh (nếu đã đăng nhập) và lối tắt tới công cụ. */
import { useEffect, useRef, useState } from "react";
import { Alert, Box, Grid, Paper, Stack, Typography, useTheme } from "@mui/material";
import {
  ChartPieIcon,
  ChatBubbleLeftRightIcon,
  ArchiveBoxIcon,
  BanknotesIcon,
  LightBulbIcon,
} from "@heroicons/react/24/outline";
import { Link as RouterLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import PageHeader from "../components/PageHeader.jsx";
import StatCard from "../components/StatCard.jsx";
import EmptyState from "../components/EmptyState.jsx";
import { useAuth } from "../auth/AuthContext.jsx";
import { listSavedPlans } from "../api/plans.js";
import { ApiError } from "../api/client.js";
import { formatCompactVnd } from "../utils/format.js";
import { useStaggerIn } from "../utils/gsap.js";

function QuickCard({ to, icon, title, description }) {
  return (
    <Paper
      component={RouterLink}
      to={to}
      sx={{
        p: 2.5,
        borderRadius: 3,
        height: "100%",
        display: "block",
        textDecoration: "none",
        color: "inherit",
        border: "1px solid",
        borderColor: "divider",
        transition: "border-color .15s ease, transform .15s ease",
        "&:hover": { borderColor: "primary.main", transform: "translateY(-2px)" },
      }}
      className="gsap-in"
    >
      <Stack direction="row" spacing={2} alignItems="center">
        <Box
          sx={{
            width: 44,
            height: 44,
            borderRadius: 2,
            bgcolor: "rgba(99,102,241,0.14)",
            color: "primary.main",
            display: "grid",
            placeItems: "center",
            "& svg": { width: 24, height: 24 },
          }}
        >
          {icon}
        </Box>
        <Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {description}
          </Typography>
        </Box>
      </Stack>
    </Paper>
  );
}

export default function Dashboard() {
  const { t } = useTranslation();
  const theme = useTheme();
  const { isAuthed, user } = useAuth();
  const rootRef = useRef(null);
  useStaggerIn(rootRef, theme);

  const [plans, setPlans] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthed) return undefined;
    let active = true;
    (async () => {
      try {
        const res = await listSavedPlans({ limit: 5 });
        if (active) setPlans(res);
      } catch (err) {
        if (active) setError(err instanceof ApiError ? err.message : t("common.error"));
      }
    })();
    return () => {
      active = false;
    };
  }, [isAuthed, t]);

  const latest = plans?.items?.[0];

  return (
    <Box ref={rootRef}>
      <PageHeader
        title={isAuthed ? t("dashboard.greeting", { name: user?.username }) : t("dashboard.greetingGuest")}
        description={t("dashboard.subtitle")}
      />

      {error && (
        <Alert severity="error" onClose={() => setError("")} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {isAuthed && plans && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={4}>
            <StatCard label={t("dashboard.savedPlans")} value={String(plans.total)} accent="#6366f1" icon={<ArchiveBoxIcon />} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <StatCard
              label={t("dashboard.latestIncome")}
              value={latest ? formatCompactVnd(latest.monthly_income) : "—"}
              accent="#2563eb"
              icon={<BanknotesIcon />}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <StatCard
              label={t("dashboard.latestSurplus")}
              value={latest ? formatCompactVnd(latest.monthly_surplus) : "—"}
              accent="#10b981"
              icon={<BanknotesIcon />}
            />
          </Grid>
        </Grid>
      )}

      <Grid container spacing={2.5}>
        <Grid item xs={12} md={6}>
          <QuickCard
            to="/planner"
            icon={<ChartPieIcon />}
            title={t("dashboard.quick.planner")}
            description={t("dashboard.quick.plannerDesc")}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <QuickCard
            to="/chat"
            icon={<ChatBubbleLeftRightIcon />}
            title={t("dashboard.quick.chat")}
            description={t("dashboard.quick.chatDesc")}
          />
        </Grid>
      </Grid>

      {/* Giải thích quy tắc 50/30/20 */}
      <Paper sx={{ p: 2.5, borderRadius: 3, mt: 3 }} className="gsap-in">
        <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
          {t("dashboard.rule.title")}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {t("dashboard.rule.description")}
        </Typography>
        <Grid container spacing={2}>
          {[
            { pct: "50%", color: "#6366f1", title: "needs", desc: "needsDesc" },
            { pct: "30%", color: "#f59e0b", title: "wants", desc: "wantsDesc" },
            { pct: "20%", color: "#10b981", title: "savings", desc: "savingsDesc" },
          ].map((r) => (
            <Grid item xs={12} sm={4} key={r.title}>
              <Box sx={{ p: 2, borderRadius: 2, border: `2px solid ${r.color}33`, height: "100%" }}>
                <Typography variant="h5" sx={{ color: r.color, fontWeight: 800 }}>
                  {r.pct}
                </Typography>
                <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                  {t(`dashboard.rule.${r.title}`)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {t(`dashboard.rule.${r.desc}`)}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Mẹo tài chính */}
      <Alert severity="info" icon={<LightBulbIcon style={{ width: 22, height: 22 }} />} sx={{ mt: 2.5 }} className="gsap-in">
        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
          {t("dashboard.tip.title")}
        </Typography>
        <Typography variant="body2">{t("dashboard.tip.body")}</Typography>
      </Alert>

      {!isAuthed && (
        <Box sx={{ mt: 2.5 }}>
          <EmptyState
            title={t("dashboard.loginPrompt.title")}
            description={t("dashboard.loginPrompt.description")}
          />
        </Box>
      )}
    </Box>
  );
}
