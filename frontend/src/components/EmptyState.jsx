/** Trạng thái rỗng: icon + tiêu đề + mô tả + action. `bare` bỏ khung Paper. */
import { Paper, Stack, Box, Typography } from "@mui/material";

/**
 * @param {{
 *   icon?: React.ReactNode,
 *   title: string,
 *   description?: string,
 *   action?: React.ReactNode,
 *   bare?: boolean
 * }} props
 */
export default function EmptyState({ icon, title, description, action, bare = false }) {
  const content = (
    <Stack spacing={1.5} alignItems="center" sx={{ textAlign: "center", py: 5, px: 3 }}>
      {icon && (
        <Box
          sx={{
            width: 56,
            height: 56,
            borderRadius: 3,
            bgcolor: "action.hover",
            color: "primary.main",
            display: "grid",
            placeItems: "center",
            "& svg": { width: 28, height: 28 },
          }}
        >
          {icon}
        </Box>
      )}
      <Typography variant="h6">{title}</Typography>
      {description && (
        <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 420 }}>
          {description}
        </Typography>
      )}
      {action && <Box sx={{ mt: 1 }}>{action}</Box>}
    </Stack>
  );

  if (bare) return content;
  return (
    <Paper sx={{ borderRadius: 3, border: "1px dashed", borderColor: "divider" }}>{content}</Paper>
  );
}
