/**
 * Builder option cho ECharts. Option đọc màu từ theme.palette để tự theo dark mode;
 * animation tắt khi reduced-motion.
 */
import { reduced } from "./gsap.js";

/** @param {object} theme */
export function echartsAnimation(theme) {
  return reduced(theme) ? { animation: false } : { animation: true, animationDuration: 600 };
}

/**
 * Pie phân bổ ngân sách (50/30/20).
 * @param {object} theme
 * @param {{needs:number, wants:number, savings:number}} allocation
 * @param {{needs:string, wants:string, savings:string}} labels
 */
export function allocationPieOption(theme, allocation, labels) {
  const p = theme.palette;
  return {
    ...echartsAnimation(theme),
    tooltip: {
      trigger: "item",
      formatter: (d) => `${d.name}: ${d.value.toLocaleString("vi-VN")} ₫ (${d.percent}%)`,
    },
    legend: {
      bottom: 0,
      textStyle: { color: p.text.secondary },
      icon: "circle",
    },
    series: [
      {
        type: "pie",
        radius: ["52%", "76%"],
        avoidLabelOverlap: true,
        itemStyle: { borderColor: p.background.paper, borderWidth: 2 },
        label: { show: false },
        data: [
          { value: Math.round(allocation.needs || 0), name: labels.needs, itemStyle: { color: p.primary.main } },
          { value: Math.round(allocation.wants || 0), name: labels.wants, itemStyle: { color: p.warning.main } },
          { value: Math.round(allocation.savings || 0), name: labels.savings, itemStyle: { color: p.success.main } },
        ],
      },
    ],
  };
}
