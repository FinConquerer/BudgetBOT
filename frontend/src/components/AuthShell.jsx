/** Khung trang xác thực (Login/Register): logo thương hiệu + Paper canh giữa màn hình. */
import { Box, Paper, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

/** @param {{title:string, subtitle?:string, children:React.ReactNode, footer?:React.ReactNode}} props */
export default function AuthShell({ title, subtitle, children, footer }) {
  const { t } = useTranslation();
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        p: 2,
        bgcolor: "background.default",
      }}
    >
      <Paper sx={{ p: { xs: 3, sm: 4 }, width: "100%", maxWidth: 420, borderRadius: 3 }}>
        <Stack spacing={1} alignItems="center" sx={{ mb: 3 }}>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: 3,
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              display: "grid",
              placeItems: "center",
              fontSize: 28,
            }}
          >
            💰
          </Box>
          <Typography variant="h5">{t("app.name")}</Typography>
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: "center" }}>
              {subtitle}
            </Typography>
          )}
        </Stack>
        {children}
        {footer && <Box sx={{ mt: 2, textAlign: "center" }}>{footer}</Box>}
      </Paper>
    </Box>
  );
}
