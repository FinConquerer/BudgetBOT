/** Tiêu đề trang chuẩn: luôn đặt đầu mỗi page. Tiêu đề + mô tả + vùng actions bên phải. */
import { Stack, Box, Typography } from "@mui/material";

/** @param {{title:string, description?:string, actions?:React.ReactNode}} props */
export default function PageHeader({ title, description, actions }) {
  return (
    <Stack
      direction={{ xs: "column", sm: "row" }}
      justifyContent="space-between"
      alignItems={{ xs: "flex-start", sm: "center" }}
      spacing={2}
      sx={{ mb: 3 }}
      className="gsap-in"
    >
      <Box>
        <Typography variant="h4">{title}</Typography>
        {description && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, maxWidth: 640 }}>
            {description}
          </Typography>
        )}
      </Box>
      {actions && <Box>{actions}</Box>}
    </Stack>
  );
}
