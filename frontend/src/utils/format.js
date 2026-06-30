/**
 * Helper format hiển thị. Nguyên tắc: mọi hiển thị tiền/tỷ lệ đi qua đây để nhất quán.
 */

/** Format số tiền VND (làm tròn về đồng), ví dụ 4166666.67 -> "4.166.667 ₫". @param {number} v */
export function formatVnd(v) {
  const n = Math.round(Number(v) || 0);
  return `${n.toLocaleString("vi-VN")} ₫`;
}

/** Làm tròn tiền tới hàng nghìn để hiển thị thân thiện. @param {number} v */
export function formatVndRounded(v) {
  const n = Math.round((Number(v) || 0) / 1000) * 1000;
  return `${n.toLocaleString("vi-VN")} ₫`;
}

/** Format số rút gọn: 1300000 -> "1,3 tr"; 15000000 -> "15 tr". @param {number} v */
export function formatCompactVnd(v) {
  const n = Number(v) || 0;
  const fmt = (x, d = 1) => x.toLocaleString("vi-VN", { maximumFractionDigits: d });
  if (Math.abs(n) >= 1_000_000_000) return `${fmt(n / 1_000_000_000)} tỷ`;
  if (Math.abs(n) >= 1_000_000) return `${fmt(n / 1_000_000)} tr`;
  if (Math.abs(n) >= 1_000) return `${fmt(n / 1_000, 0)}k`;
  return String(Math.round(n));
}

/** Tỷ lệ 0..1 (hoặc 0..100) -> "15,3%". @param {number} v @param {boolean} alreadyPercent */
export function formatPercent(v, alreadyPercent = false) {
  const n = (Number(v) || 0) * (alreadyPercent ? 1 : 100);
  return `${n.toLocaleString("vi-VN", { maximumFractionDigits: 1 })}%`;
}

/** Map trạng thái mục tiêu rulebase -> token màu palette. @param {string} status */
export function goalTone(status) {
  switch (status) {
    case "feasible":
      return "success";
    case "tight":
      return "warning";
    case "not_feasible":
      return "error";
    default:
      return "info";
  }
}
