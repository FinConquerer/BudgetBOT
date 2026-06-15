from app.core.faq.faq import answer, load_faq


def test_load_faq_nonempty():
    assert len(load_faq()) > 0


def test_answer_savings():
    assert "20%" in answer("Tôi nên tiết kiệm bao nhiêu %?")


def test_answer_emergency():
    assert "3-6 tháng" in answer("Quỹ khẩn cấp nên có bao nhiêu tiền?")


def test_answer_unknown():
    assert "chưa có thông tin" in answer("xyzabc khong lien quan gi ca")
