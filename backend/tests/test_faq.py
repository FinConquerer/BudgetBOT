import pytest

from app.core.faq.faq import (
    FAQEngine,
    answer,
    detect_intent,
    detect_sentiment,
    load_faq,
    normalize_text,
)


def test_normalize_text_basic():
    assert normalize_text("  Xin CHÀO!!! ", remove_accents=True) == "xin chao"


def test_normalize_text_keep_accents():
    assert normalize_text("  Quỹ KHẨN-cấp?! ", remove_accents=False) == "quỹ khẩn cấp"


@pytest.mark.parametrize(
    ("text", "expected_intent"),
    [
        ("Tôi muốn lập ngân sách cá nhân", "budget_planning"),
        ("Tôi nên tiết kiệm bao nhiêu mỗi tháng?", "recommendation"),
        ("Tôi đang có 20 triệu tiền tiết kiệm", "financial_assessment"),
        ("Tôi bị nợ thẻ tín dụng thì làm sao?", "debt_management"),
    ],
)
def test_detect_intent_common_cases(text, expected_intent):
    intent, confidence = detect_intent(text)

    assert intent == expected_intent
    assert confidence > 0


@pytest.mark.parametrize(
    ("text", "expected_sentiment"),
    [
        ("Tôi rất lo lắng vì thiếu tiền", "negative"),
        ("Tôi thấy ổn và muốn tiết kiệm thêm", "positive"),
        ("Tôi muốn hỏi về quỹ khẩn cấp", "neutral"),
    ],
)
def test_detect_sentiment_common_cases(text, expected_sentiment):
    sentiment, confidence = detect_sentiment(text)

    assert sentiment == expected_sentiment
    assert confidence >= 0


@pytest.mark.parametrize(
    ("question", "expected_id"),
    [
        ("Quỹ khẩn cấp là gì?", "FAQ_016"),
        ("Quỹ khẩn cấp nên có bao nhiêu tiền?", "FAQ_017"),
        ("Tôi nên tiết kiệm bao nhiêu mỗi tháng?", "FAQ_010"),
        ("Tôi rất khó tiết kiệm, phải làm sao?", "FAQ_011"),
        ("Tiết kiệm tự động có nên dùng không?", "FAQ_012"),
        ("Gửi tiết kiệm ngân hàng có lợi không?", "FAQ_013"),
        ("Tiết kiệm có kỳ hạn khác gì không kỳ hạn?", "FAQ_014"),
        ("Tôi nên tiết kiệm hay đầu tư trước?", "FAQ_015"),
        ("Nên trả nợ hay tiết kiệm trước?", "FAQ_025"),
        ("Làm sao để tôi tiết kiệm nhiều hơn?", "RCM_035"),
    ],
)
def test_faq_engine_returns_expected_id(question, expected_id):
    engine = FAQEngine(load_faq())
    result = engine.analyze(question)

    assert result.status == "answered"
    assert result.matches
    assert result.matches[0].item["id"] == expected_id


def test_question_without_accents_still_matches():
    engine = FAQEngine(load_faq())

    result = engine.analyze("Quy khan cap nen co bao nhieu tien?")

    assert result.status == "answered"
    assert result.matches[0].item["id"].startswith("FAQ_")


def test_unknown_question_returns_no_match():
    engine = FAQEngine(load_faq())

    result = engine.analyze("Hôm nay trời có mưa không?")

    assert result.status == "no_match"


def test_empty_question_returns_no_match():
    engine = FAQEngine(load_faq())

    result = engine.analyze("   ")

    assert result.status == "no_match"


def test_answer_function_returns_string():
    response = answer("Quỹ khẩn cấp là gì?")

    assert isinstance(response, str)
    assert len(response) > 0


def test_faq_loaded_successfully():
    faqs = load_faq()

    assert isinstance(faqs, list)
    assert len(faqs) > 0
    assert "id" in faqs[0]
    assert "question" in faqs[0]
    assert "answer" in faqs[0]


def test_result_has_required_fields():
    engine = FAQEngine(load_faq())

    result = engine.analyze("Tôi nên tiết kiệm bao nhiêu mỗi tháng?")

    assert hasattr(result, "status")
    assert hasattr(result, "answer")
    assert hasattr(result, "confidence")
    assert hasattr(result, "matches")
    assert hasattr(result, "intent")
