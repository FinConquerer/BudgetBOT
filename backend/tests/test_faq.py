import pytest

from app.core.faq.faq import (
    FAQEngine,
    answer,
    detect_intent,
    detect_sentiment,
    load_faq,
    normalize_text,
)


def test_normalize_text_handles_vietnamese_accents_and_punctuation():
    assert normalize_text("  Quỹ KHẨN-cấp?! ", remove_accents=True) == "quy khan cap"


def test_intent_phrase_does_not_match_inside_another_word():
    intent, _ = detect_intent("Khi tôi bị mất việc thì nên làm gì?")
    assert intent == "recommendation"


def test_detect_negative_sentiment_from_phrase():
    sentiment, confidence = detect_sentiment("Tôi rất lo lắng vì đang thiếu tiền")
    assert sentiment == "negative"
    assert confidence > 0.5


def test_phrase_scoring_answers_known_faq():
    result = FAQEngine(load_faq()).analyze("Quỹ khẩn cấp nên có bao nhiêu tiền?")
    assert result.status == "answered"
    assert result.matches[0].item["id"].startswith("FAQ_")
    assert result.confidence >= 0.38


@pytest.mark.parametrize(
    ("question", "expected_id"),
    [
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
def test_savings_questions_match_the_expected_faq(question, expected_id):
    result = FAQEngine(load_faq()).analyze(question)

    assert result.status == "answered"
    assert result.matches[0].item["id"] == expected_id


def test_savings_question_without_accents_matches_the_same_faq():
    engine = FAQEngine(load_faq())

    accented = engine.analyze("Tôi nên tiết kiệm bao nhiêu mỗi tháng?")
    unaccented = engine.analyze("Toi nen tiet kiem bao nhieu moi thang?")

    assert accented.matches[0].item["id"] == "FAQ_010"
    assert unaccented.matches[0].item["id"] == accented.matches[0].item["id"]


@pytest.mark.parametrize(
    ("question", "expected_id"),
    [
        ("Tôi chưa có tiết kiệm gì cả", "INFO_014"),
        ("Tôi đang có 20 triệu tiền tiết kiệm", "INFO_005"),
    ],
)
def test_savings_information_uses_financial_assessment_intent(question, expected_id):
    result = FAQEngine(load_faq()).analyze(question)

    assert result.status == "answered"
    assert result.intent == "financial_assessment"
    assert result.matches[0].item["id"] == expected_id


def test_close_scores_ask_for_clarification():
    faqs = [
        {
            "id": "FAQ_1",
            "keywords": ["tiết kiệm"],
            "question": "Tôi nên tiết kiệm bao nhiêu?",
            "answer": "A",
        },
        {
            "id": "FAQ_2",
            "keywords": ["tiết kiệm"],
            "question": "Tôi nên bắt đầu tiết kiệm thế nào?",
            "answer": "B",
        },
    ]
    result = FAQEngine(faqs, min_confidence=0.25, ambiguity_margin=0.2).analyze(
        "Tôi muốn tiết kiệm"
    )
    assert result.status == "clarification"
    assert "1." in result.answer and "2." in result.answer


def test_low_confidence_question_does_not_guess():
    result = FAQEngine(load_faq()).analyze("Thời tiết hôm nay thế nào?")
    assert result.status == "no_match"


class FakeEmbeddingProvider:
    def encode(self, texts):
        vectors = []
        for text in texts:
            folded = normalize_text(text, remove_accents=True)
            if "quy khan cap" in folded or "phong than" in folded:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return vectors


def test_embedding_can_find_semantic_match_without_shared_words():
    faqs = [
        {
            "id": "FAQ_1",
            "keywords": ["quỹ khẩn cấp"],
            "question": "Quỹ khẩn cấp là gì?",
            "answer": "Câu trả lời về quỹ khẩn cấp",
        },
        {
            "id": "FAQ_2",
            "keywords": ["ngân sách"],
            "question": "Ngân sách là gì?",
            "answer": "Câu trả lời về ngân sách",
        },
    ]
    engine = FAQEngine(
        faqs,
        embedding_provider=FakeEmbeddingProvider(),
        embedding_weight=0.8,
        min_confidence=0.5,
    )
    result = engine.analyze("Tôi cần một khoản phòng thân")
    assert result.status == "answered"
    assert result.answer == "Câu trả lời về quỹ khẩn cấp"


def test_answer_keeps_string_api_compatible():
    assert isinstance(answer("Xin chào"), str)
