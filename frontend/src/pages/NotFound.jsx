/** Trang 404. */
import { Box, Button } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import EmptyState from "../components/EmptyState.jsx";

export default function NotFound() {
  const { t } = useTranslation();
  return (
    <Box sx={{ maxWidth: 480, mx: "auto", mt: 6 }}>
      <EmptyState
        title={t("notFound.title")}
        description={t("notFound.description")}
        action={
          <Button variant="contained" component={RouterLink} to="/">
            {t("notFound.home")}
          </Button>
        }
      />
    </Box>
  );
}
