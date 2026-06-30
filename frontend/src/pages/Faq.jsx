/** Trang tra cứu FAQ công khai: ô tìm kiếm + danh sách câu hỏi/đáp. */
import { useEffect, useRef, useState } from "react";
import {
  Alert,
  Box,
  Chip,
  InputAdornment,
  Paper,
  Skeleton,
  Stack,
  TextField,
  Typography,
  useTheme,
} from "@mui/material";
import { MagnifyingGlassIcon, QuestionMarkCircleIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "react-i18next";
import PageHeader from "../components/PageHeader.jsx";
import EmptyState from "../components/EmptyState.jsx";
import { listFaqs } from "../api/faq.js";
import { ApiError } from "../api/client.js";
import { useStaggerIn } from "../utils/gsap.js";

export default function Faq() {
  const { t } = useTranslation();
  const theme = useTheme();
  const rootRef = useRef(null);
  useStaggerIn(rootRef, theme);

  const [q, setQ] = useState("");
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const handle = setTimeout(async () => {
      setItems(null);
      try {
        const res = await listFaqs({ q: q.trim() || undefined, limit: 50 });
        if (active) setItems(res.items);
      } catch (err) {
        if (active) setError(err instanceof ApiError ? err.message : t("common.error"));
      }
    }, 300);
    return () => {
      active = false;
      clearTimeout(handle);
    };
  }, [q, t]);

  return (
    <Box ref={rootRef}>
      <PageHeader title={t("faq.title")} description={t("faq.subtitle")} />

      {error && (
        <Alert severity="error" onClose={() => setError("")} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TextField
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder={t("faq.searchPlaceholder")}
        fullWidth
        sx={{ mb: 2.5, maxWidth: 520 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <MagnifyingGlassIcon style={{ width: 20, height: 20 }} />
            </InputAdornment>
          ),
        }}
      />

      {items == null ? (
        <Stack spacing={1.5}>
          {[0, 1, 2, 3].map((i) => (
            <Skeleton key={i} variant="rounded" height={96} />
          ))}
        </Stack>
      ) : items.length === 0 ? (
        <EmptyState
          icon={<QuestionMarkCircleIcon />}
          title={t("faq.empty.title")}
          description={t("faq.empty.description")}
        />
      ) : (
        <Stack spacing={1.5}>
          {items.map((f) => (
            <Paper key={f.id} sx={{ p: 2.5, borderRadius: 3 }} className="gsap-in">
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                {f.question}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {f.answer}
              </Typography>
              {f.keywords?.length > 0 && (
                <Stack direction="row" spacing={0.5} sx={{ mt: 1.5, flexWrap: "wrap", gap: 0.5 }}>
                  {f.keywords.slice(0, 6).map((k) => (
                    <Chip key={k} size="small" variant="outlined" label={k} />
                  ))}
                </Stack>
              )}
            </Paper>
          ))}
        </Stack>
      )}
    </Box>
  );
}
