// Lớp gọi API tới backend FastAPI. Dev dùng proxy /api (xem vite.config.ts).
const BASE = import.meta.env.VITE_API_BASE ?? "/api";

export async function askFaq(question: string): Promise<string> {
  const res = await fetch(`${BASE}/faq`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error("FAQ request failed");
  return (await res.json()).answer as string;
}

export interface PlanRequest {
  monthly_income: number;
  essential_expenses: number;
  discretionary_expenses: number;
  monthly_savings: number;
}

export async function makePlan(req: PlanRequest) {
  const res = await fetch(`${BASE}/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error("Plan request failed");
  return res.json();
}
