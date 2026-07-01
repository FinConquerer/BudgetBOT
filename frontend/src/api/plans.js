/** API rulebase: tạo kế hoạch, what-if, và lịch sử kế hoạch đã lưu (cần đăng nhập). */
import { apiFetch } from "./client.js";

/** Tạo kế hoạch ngân sách (không cần đăng nhập). @param {object} req PlanRequest */
export function makePlan(req) {
  return apiFetch("/plan", { method: "POST", body: JSON.stringify(req) });
}

/** Chạy kịch bản what-if. @param {{profile:object, change:{field:string, delta:number}}} body */
export function runWhatIf(body) {
  return apiFetch("/what-if", { method: "POST", body: JSON.stringify(body) });
}

/** Lưu kế hoạch vào lịch sử (cần đăng nhập). @param {object} req PlanRequest */
export function createSavedPlan(req) {
  return apiFetch("/plans", { method: "POST", body: JSON.stringify(req) });
}

export function listSavedPlans({ limit = 20, offset = 0 } = {}) {
  const q = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiFetch(`/plans?${q.toString()}`);
}

export function deleteSavedPlan(id) {
  return apiFetch(`/plans/${id}`, { method: "DELETE" });
}
