/** Trang trợ lý hội thoại: hỏi đáp FAQ một lượt (không cần đăng nhập). */
import { useEffect, useRef, useState } from "react";
import {
  Box,
  Chip,
  IconButton,
  Paper,
  Stack,
  TextField,
  Typography,
  useTheme,
  CircularProgress,
} from "@mui/material";
import { PaperAirplaneIcon, ChatBubbleLeftRightIcon } from "@heroicons/react/24/outline";
import { useTranslation } from "react-i18next";
import PageHeader from "../components/PageHeader.jsx";
import EmptyState from "../components/EmptyState.jsx";
import { askFaq } from "../api/chat.js";
import { ApiError } from "../api/client.js";
import { useStaggerIn } from "../utils/gsap.js";

function Bubble({ role, children, meta }) {
  const isUser = role === "user";
  return (
    <Stack direction="row" justifyContent={isUser ? "flex-end" : "flex-start"} sx={{ mb: 1.5 }}>
      <Paper
        elevation={0}
        sx={{
          px: 2,
          py: 1.25,
          maxWidth: "78%",
          borderRadius: 3,
          bgcolor: isUser ? "primary.main" : "background.subtle",
          color: isUser ? "primary.contrastText" : "text.primary",
          border: isUser ? "none" : "1px solid",
          borderColor: "divider",
        }}
      >
        <Typography variant="body2" sx={{ whiteSpace: "pre-wrap" }}>
          {children}
        </Typography>
        {meta}
      </Paper>
    </Stack>
  );
}

export default function Chat() {
  const { t } = useTranslation();
  const theme = useTheme();
  const rootRef = useRef(null);
  const endRef = useRef(null);
  useStaggerIn(rootRef, theme);

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  function send(e) {
    e.preventDefault();
    ask(input.trim());
  }

  async function ask(question) {
    if (!question || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: question }]);
    setBusy(true);
    try {
      const res = await askFaq(question);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: res.answer,
          intent: res.intent,
          sentiment: res.sentiment,
        },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: err instanceof ApiError ? err.message : t("common.error") },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Box ref={rootRef} sx={{ display: "flex", flexDirection: "column", height: "calc(100vh - 134px)" }}>
      <PageHeader title={t("chat.title")} description={t("chat.subtitle")} />

      <Paper
        sx={{ flexGrow: 1, borderRadius: 3, p: 2, overflowY: "auto", minHeight: 0 }}
        className="gsap-in"
      >
        {messages.length === 0 ? (
          <Box sx={{ height: "100%", display: "grid", placeItems: "center" }}>
            <Stack alignItems="center" spacing={2}>
              <EmptyState
                bare
                icon={<ChatBubbleLeftRightIcon />}
                title={t("chat.empty.title")}
                description={t("chat.empty.description")}
              />
              <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", justifyContent: "center", gap: 1, maxWidth: 560 }}>
                {t("chat.suggestions", { returnObjects: true }).map((s) => (
                  <Chip
                    key={s}
                    label={s}
                    onClick={() => ask(s)}
                    variant="outlined"
                    sx={{ cursor: "pointer" }}
                  />
                ))}
              </Stack>
            </Stack>
          </Box>
        ) : (
          <>
            {messages.map((m, i) => (
              <Bubble
                key={i}
                role={m.role}
                meta={
                  m.role === "assistant" && m.intent ? (
                    <Stack direction="row" spacing={0.5} sx={{ mt: 1 }}>
                      <Chip size="small" variant="outlined" label={`${t("chat.intent")}: ${m.intent}`} />
                      <Chip size="small" variant="outlined" label={`${t("chat.sentiment")}: ${m.sentiment}`} />
                    </Stack>
                  ) : null
                }
              >
                {m.content}
              </Bubble>
            ))}
            {busy && (
              <Stack direction="row" spacing={1} alignItems="center" sx={{ color: "text.secondary" }}>
                <CircularProgress size={16} />
                <Typography variant="caption">{t("common.loading")}</Typography>
              </Stack>
            )}
          </>
        )}
        <div ref={endRef} />
      </Paper>

      <Paper component="form" onSubmit={send} sx={{ mt: 2, p: 1, borderRadius: 3 }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <TextField
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t("chat.placeholder")}
            fullWidth
            size="small"
            sx={{ "& fieldset": { border: "none" } }}
          />
          <IconButton type="submit" color="primary" disabled={busy || !input.trim()}>
            <PaperAirplaneIcon style={{ width: 22, height: 22 }} />
          </IconButton>
        </Stack>
      </Paper>
    </Box>
  );
}
