"""Định tuyến hội thoại đơn giản (V1): câu hỏi -> FAQ Engine."""
from budgetbot.faq.faq import answer as faq_answer


def route(message: str) -> str:
    """V1: mọi câu hỏi kiến thức -> FAQ. V2: phân loại FAQ vs Rule."""
    return faq_answer(message)
