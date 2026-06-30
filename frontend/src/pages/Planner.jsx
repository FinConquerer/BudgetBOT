/** Trang lập kế hoạch ngân sách: nhập liệu -> phân bổ 50/30/20, chỉ số, đánh giá mục tiêu, what-if. */
import { useRef, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  Divider,
  Grid,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Paper,
  Snackbar,
  Stack,
  TextField,
  Typography,
  useTheme,
} from "@mui/material";
import {
  BanknotesIcon,
  ArrowTrendingUpIcon,
  ScaleIcon,
  CreditCardIcon,
} from "@heroicons/react/24/outline";
import { useTranslation } from "react-i18next";
import PageHeader from "../components/PageHeader.jsx";
import StatCard from "../components/StatCard.jsx";
import EmptyState from "../components/EmptyState.jsx";
import AllocationChart from "../components/AllocationChart.jsx";
import { makePlan, runWhatIf, createSavedPlan } from "../api/plans.js";
import { ApiError } from "../api/client.js";
import { useAuth } from "../auth/AuthContext.jsx";
import { formatVnd, formatCompactVnd, formatPercent, goalTone } from "../utils/format.js";
import { useStaggerIn } from "../utils/gsap.js";

const NUM_FIELDS = [
  "fixed_expenses",
  "variable_expenses",
  "debt_payment",
  "debt_outstanding",
  "current_savings",
  "goal_amount",
];
const WHATIF_FIELDS = ["monthly_income", "fixed_expenses", "variable_expenses", "debt_payment"];

const EMPTY = {
  monthly_income: "",
  fixed_expenses: "",
  variable_expenses: "",
  debt_payment: "",
  debt_outstanding: "",
  current_savings: "",
  financial_goal: "",
  goal_amount: "",
  goal_deadline_months: "",
  income_stability: "stable",
};

function toRequest(form) {
  const num = (v) => (v === "" || v == null ? 0 : Number(v));
  return {
    monthly_income: num(form.monthly_income),
    fixed_expenses: num(form.fixed_expenses),
    variable_expenses: num(form.variable_expenses),
    debt_payment: num(form.debt_payment),
    debt_outstanding: num(form.debt_outstanding),
    current_savings: num(form.current_savings),
    financial_goal: form.financial_goal || null,
    goal_amount: num(form.goal_amount),
    goal_deadline_months: form.goal_deadline_months ? Number(form.goal_deadline_months) : null,
    income_stability: form.income_stability,
  };
}

export default function Planner() {
  const { t } = useTranslation();
  const theme = useTheme();
  const { isAuthed } = useAuth();
  const rootRef = useRef(null);
  useStaggerIn(rootRef, theme);

  const [form, setForm] = useState(EMPTY);
  const [plan, setPlan] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");

  const [whatif, setWhatif] = useState({ field: "monthly_income", delta: "" });
  const [comparison, setComparison] = useState(null);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function handleCalc(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setComparison(null);
    try {
      const res = await makePlan(toRequest(form));
      setPlan(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("common.error"));
    } finally {
      setBusy(false);
    }
  }

  async function handleWhatIf() {
    if (!whatif.delta) return;
    setError("");
    try {
      const res = await runWhatIf({
        profile: toRequest(form),
        change: { field: whatif.field, delta: Number(whatif.delta) },
      });
      setComparison(res.comparison);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("common.error"));
    }
  }

  async function handleSave() {
    try {
      await createSavedPlan(toRequest(form));
      setToast(t("planner.saved"));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("common.error"));
    }
  }

  return (
    <Box ref={rootRef}>
      <PageHeader title={t("planner.title")} description={t("planner.subtitle")} />

      {error && (
        <Alert severity="error" onClose={() => setError("")} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2.5}>
        {/* FORM */}
        <Grid item xs={12} md={5}>
          <Paper component="form" onSubmit={handleCalc} sx={{ p: 2.5, borderRadius: 3 }} className="gsap-in">
            <Stack spacing={2}>
              <TextField
                label={t("planner.form.monthlyIncome")}
                type="number"
                value={form.monthly_income}
                onChange={set("monthly_income")}
                required
                fullWidth
              />
              <Grid container spacing={2}>
                {NUM_FIELDS.map((k) => (
                  <Grid item xs={6} key={k}>
                    <TextField
                      label={t(`planner.form.${camel(k)}`)}
                      type="number"
                      value={form[k]}
                      onChange={set(k)}
                      fullWidth
                    />
                  </Grid>
                ))}
              </Grid>
              <TextField
                label={t("planner.form.goal")}
                value={form.financial_goal}
                onChange={set("financial_goal")}
                fullWidth
              />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    label={t("planner.form.goalDeadline")}
                    type="number"
                    value={form.goal_deadline_months}
                    onChange={set("goal_deadline_months")}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    select
                    label={t("planner.form.stability")}
                    value={form.income_stability}
                    onChange={set("income_stability")}
                    fullWidth
                  >
                    {["stable", "unstable", "seasonal"].map((s) => (
                      <MenuItem key={s} value={s}>
                        {t(`planner.stability.${s}`)}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
              </Grid>
              <Stack direction="row" spacing={1.5}>
                <Button type="submit" variant="contained" disabled={busy} fullWidth>
                  {t("planner.form.calc")}
                </Button>
                {isAuthed && plan && (
                  <Button variant="outlined" onClick={handleSave} className="no-hover-lift">
                    {t("planner.form.savePlan")}
                  </Button>
                )}
              </Stack>
              <Typography variant="caption" color="text.secondary">
                {t("planner.disclaimer")}
              </Typography>
            </Stack>
          </Paper>
        </Grid>

        {/* RESULTS */}
        <Grid item xs={12} md={7}>
          {!plan ? (
            <EmptyState
              icon={<BanknotesIcon />}
              title={t("planner.empty.title")}
              description={t("planner.empty.description")}
            />
          ) : (
            <Stack spacing={2.5}>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <StatCard
                    label={t("planner.result.surplus")}
                    value={formatCompactVnd(plan.summary.monthly_surplus)}
                    note={formatVnd(plan.summary.monthly_surplus)}
                    accent="#10b981"
                    icon={<BanknotesIcon />}
                  />
                </Grid>
                <Grid item xs={6} sm={3}>
                  <StatCard
                    label={t("planner.result.savingsRate")}
                    count={plan.metrics.savings_rate * 100}
                    format={(n) => `${n.toFixed(1)}%`}
                    accent="#6366f1"
                    icon={<ArrowTrendingUpIcon />}
                  />
                </Grid>
                <Grid item xs={6} sm={3}>
                  <StatCard
                    label={t("planner.result.expenseRatio")}
                    value={formatPercent(plan.metrics.expense_ratio)}
                    accent="#f59e0b"
                    icon={<ScaleIcon />}
                  />
                </Grid>
                <Grid item xs={6} sm={3}>
                  <StatCard
                    label={t("planner.result.debtRatio")}
                    value={formatPercent(plan.metrics.debt_payment_ratio)}
                    accent="#ef4444"
                    icon={<CreditCardIcon />}
                  />
                </Grid>
              </Grid>

              <Grid container spacing={2.5}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2.5, borderRadius: 3, height: "100%" }} className="gsap-in">
                    <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1 }}>
                      {t("planner.allocation.title")}
                    </Typography>
                    <AllocationChart allocation={plan.allocation} />
                  </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2.5, borderRadius: 3, height: "100%" }} className="gsap-in">
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                        {t("planner.goalAssessment")}
                      </Typography>
                      <Chip
                        size="small"
                        color={goalTone(plan.goal_assessment.status)}
                        label={plan.goal_assessment.status}
                      />
                    </Stack>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                      {plan.goal_assessment.message}
                    </Typography>
                    {plan.goal_assessment.required_monthly_saving > 0 && (
                      <Typography variant="body2">
                        {t("planner.requiredSaving")}:{" "}
                        <b>{formatVnd(plan.goal_assessment.required_monthly_saving)}</b>
                      </Typography>
                    )}
                  </Paper>
                </Grid>
              </Grid>

              {(plan.warnings?.length > 0 || plan.action_items?.length > 0) && (
                <Grid container spacing={2.5}>
                  {plan.warnings?.length > 0 && (
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2.5, borderRadius: 3, height: "100%" }} className="gsap-in">
                        <Typography variant="subtitle2" color="warning.main" sx={{ fontWeight: 700 }}>
                          {t("planner.warnings")}
                        </Typography>
                        <List dense>
                          {plan.warnings.map((w, i) => (
                            <ListItem key={i} sx={{ px: 0 }}>
                              <ListItemText primary={w} />
                            </ListItem>
                          ))}
                        </List>
                      </Paper>
                    </Grid>
                  )}
                  {plan.action_items?.length > 0 && (
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2.5, borderRadius: 3, height: "100%" }} className="gsap-in">
                        <Typography variant="subtitle2" color="primary.main" sx={{ fontWeight: 700 }}>
                          {t("planner.actions")}
                        </Typography>
                        <List dense>
                          {plan.action_items.map((a, i) => (
                            <ListItem key={i} sx={{ px: 0 }}>
                              <ListItemText primary={a} />
                            </ListItem>
                          ))}
                        </List>
                      </Paper>
                    </Grid>
                  )}
                </Grid>
              )}

              {/* WHAT-IF */}
              <Paper sx={{ p: 2.5, borderRadius: 3 }} className="gsap-in">
                <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5 }}>
                  {t("planner.whatif.title")}
                </Typography>
                <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="center">
                  <TextField
                    select
                    label={t("planner.whatif.field")}
                    value={whatif.field}
                    onChange={(e) => setWhatif({ ...whatif, field: e.target.value })}
                    sx={{ minWidth: 200 }}
                  >
                    {WHATIF_FIELDS.map((f) => (
                      <MenuItem key={f} value={f}>
                        {t(`planner.form.${camel(f)}`)}
                      </MenuItem>
                    ))}
                  </TextField>
                  <TextField
                    label={t("planner.whatif.delta")}
                    type="number"
                    value={whatif.delta}
                    onChange={(e) => setWhatif({ ...whatif, delta: e.target.value })}
                  />
                  <Button variant="outlined" onClick={handleWhatIf} className="no-hover-lift">
                    {t("planner.whatif.run")}
                  </Button>
                </Stack>
                {comparison && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Stack direction="row" spacing={4}>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          {t("planner.whatif.surplusDelta")}
                        </Typography>
                        <Typography variant="h6" color={comparison.monthly_surplus_delta >= 0 ? "success.main" : "error.main"}>
                          {comparison.monthly_surplus_delta >= 0 ? "+" : ""}
                          {formatVnd(comparison.monthly_surplus_delta)}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          {t("planner.whatif.rateDelta")}
                        </Typography>
                        <Typography variant="h6" color={comparison.savings_rate_delta >= 0 ? "success.main" : "error.main"}>
                          {comparison.savings_rate_delta >= 0 ? "+" : ""}
                          {formatPercent(comparison.savings_rate_delta)}
                        </Typography>
                      </Box>
                    </Stack>
                  </>
                )}
              </Paper>
            </Stack>
          )}
        </Grid>
      </Grid>

      <Snackbar
        open={Boolean(toast)}
        autoHideDuration={3000}
        onClose={() => setToast("")}
        message={toast}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      />
    </Box>
  );
}

/** snake_case -> camelCase để map sang key i18n trong planner.form. */
function camel(s) {
  return s.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}
