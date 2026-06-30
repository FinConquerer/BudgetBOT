/** Biểu đồ donut phân bổ 50/30/20 (ECharts). Màu lấy từ theme nên tự theo dark mode. */
import ReactECharts from "echarts-for-react";
import { useTheme } from "@mui/material";
import { useTranslation } from "react-i18next";
import { allocationPieOption } from "../utils/charts.js";

/** @param {{allocation:{needs:number, wants:number, savings:number}}} props */
export default function AllocationChart({ allocation }) {
  const theme = useTheme();
  const { t } = useTranslation();
  const labels = {
    needs: t("planner.allocation.needs"),
    wants: t("planner.allocation.wants"),
    savings: t("planner.allocation.savings"),
  };
  return (
    <ReactECharts
      opts={{ renderer: "svg" }}
      style={{ height: 280, width: "100%" }}
      notMerge
      option={allocationPieOption(theme, allocation, labels)}
    />
  );
}
