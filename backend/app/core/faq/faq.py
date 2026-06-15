"""FAQ Engine — tra cứu câu trả lời từ DB (keyword matching). Nâng cấp RAG/LLM ở V2."""
import json
from pathlib import Path

_DATA = Path(__file__).resolve().parents[3] / "data" / "faq.json"


def load_faq(path: Path | None = None) -> list[dict]:
    """Nạp DB hỏi đáp."""
    p = path or _DATA
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def answer(question: str, faqs: list[dict] | None = None) -> str:
    """Trả lời theo độ trùng từ khoá; không khớp -> câu mặc định."""
    faqs = faqs if faqs is not None else load_faq()
    q = question.lower()
    best, best_score = None, 0
    for item in faqs:
        score = sum(1 for kw in item["keywords"] if kw.lower() in q)
        if score > best_score:
            best, best_score = item, score
    if best is None:
        return "Xin lỗi, mình chưa có thông tin cho câu hỏi này. Bạn thử hỏi cách khác nhé."
    return best["answer"]
