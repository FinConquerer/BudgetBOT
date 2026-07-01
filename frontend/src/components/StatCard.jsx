/** Thẻ KPI: nhãn + giá trị (số tiền/tỷ lệ) + icon, viền accent. Số dùng CountUpValue. */
import { Paper, Stack, Box, Typography } from "@mui/material";
import CountUpValue from "./CountUpValue.jsx";

/**
 * @param {{
 *   label: string,
 *   value?: string,
 *   count?: number,
 *   format?: (n:number)=>string,
 *   icon?: React.ReactNode,
 *   accent?: string,
 *   note?: string
 * }} props
 */
export default function StatCard({ label, value, count, format, icon, accent = "#6366f1", note }) {
  return (
    <Paper
      sx={{
        p: 2.5,
        borderRadius: 3,
        height: "100%",
        border: `2px solid ${accent}33`,
      }}
      className="gsap-in"
    >
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1}>
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
            {label}
          </Typography>
          <Typography variant="h5" sx={{ mt: 0.5 }}>
            {count != null && format ? <CountUpValue value={count} format={format} /> : value}
          </Typography>
          {note && (
            <Typography variant="caption" color="text.secondary">
              {note}
            </Typography>
          )}
        </Box>
        {icon && (
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              bgcolor: `${accent}1F`,
              color: accent,
              display: "grid",
              placeItems: "center",
              "& svg": { width: 22, height: 22 },
            }}
          >
            {icon}
          </Box>
        )}
      </Stack>
    </Paper>
  );
}
