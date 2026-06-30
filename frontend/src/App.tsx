import { useState } from "react";
import { askFaq, makePlan } from "./api";

export default function App() {
  const [question, setQuestion] = useState("");
  const [faqAnswer, setFaqAnswer] = useState("");
  const [form, setForm] = useState({
    monthly_income: 0,
    essential_expenses: 0,
    discretionary_expenses: 0,
    monthly_savings: 0,
  });
  const [plan, setPlan] = useState<unknown>(null);

  const onAsk = async () => question && setFaqAnswer(await askFaq(question));
  const onPlan = async () => form.monthly_income > 0 && setPlan(await makePlan(form));
  const num = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: Number(e.target.value) });

  return (
    <main style={{ maxWidth: 640, margin: "2rem auto", fontFamily: "system-ui" }}>
      <h1>💰 BudgetBOT</h1>
      <p>Trợ lý ngân sách cá nhân — chỉ tham khảo, không phải lời khuyên đầu tư.</p>

      <section>
        <h2>Hỏi đáp</h2>
        <input value={question} onChange={(e) => setQuestion(e.target.value)}
          placeholder="Nên tiết kiệm bao nhiêu %?" style={{ width: "70%" }} />
        <button onClick={onAsk}>Hỏi</button>
        {faqAnswer && <p><b>Trả lời:</b> {faqAnswer}</p>}
      </section>

      <section>
        <h2>Lập kế hoạch</h2>
        {(["monthly_income", "essential_expenses", "discretionary_expenses", "monthly_savings"] as const).map((k) => (
          <div key={k}>
            <label>{k}: </label>
            <input type="number" value={form[k]} onChange={num(k)} />
          </div>
        ))}
        <button onClick={onPlan}>Tính</button>
        {plan != null && <pre>{JSON.stringify(plan, null, 2)}</pre>}
      </section>
    </main>
  );
}
