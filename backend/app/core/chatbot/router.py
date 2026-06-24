"""Định tuyến tin nhắn qua quy trình phân tích FAQ kết hợp."""

from app.core.faq.faq import FAQResult, analyze


def analyze_message(message: str) -> FAQResult:
    """Trả về ý định, cảm xúc, độ tin cậy, ứng viên và câu trả lời cuối."""
    return analyze(message)


def route(message: str) -> str:
    """Giữ giao diện trả về văn bản cho các thành phần UI hiện tại."""
    return analyze_message(message).answer
