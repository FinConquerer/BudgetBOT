/**
 * Helper format hiển thị. Nguyên tắc: mọi hiển thị tiền/tỷ lệ đi qua đây để nhất quán.
 */

/** Format số tiền VND, ví dụ 20000000 -> "20.000.000 ₫". @param {number} v */
export function formatVnd(v) {
  const n = Number(v) || 0;
  return `${n.toLocaleString("vi-VN")} ₫`;
}

/** Format số rút gọn: 1.300.000 -> "1,3tr"; 15.000.000 -> "15tr". @param {number} v */
export function formatCompactVnd(v) {
  const n = Number(v) || 0;
  if (Math.abs(n) >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)} tỷ`;
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(n % 1_000_000 ? 1 : 0)} tr`;
  if (Math.abs(n) >= 1_000) return `${(n / 1_000).toFixed(0)}k`;
  return String(n);
}

/** Tỷ lệ 0..1 (hoặc 0..100) -> "12,3%". @param {number} v @param {boolean} alreadyPercent */
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
