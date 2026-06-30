"""FAQ Engine kết hợp: nhận diện ý định, cảm xúc, chấm điểm cụm từ và embedding."""

from __future__ import annotations

import json
import math
import os
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Protocol, Sequence

_DATA = Path(__file__).resolve().parents[3] / "data" / "faq.json"
_NON_WORDS = re.compile(r"[^\w%]+", re.UNICODE)

_INTENT_BY_PREFIX = {
    "GREET": "greeting",
    "ABOUT": "about_bot",
    "FAQ": "financial_knowledge",
    "INFO": "financial_assessment",
    "RCM": "recommendation",
    "FALL": "fallback",
}

_INTENT_CUES = {
    "greeting": ("xin chao", "chao buoi", "hello", "hi", "hey", "cam on", "tam biet"),
    "about_bot": ("ban la ai", "chatbot", "tro ly", "ban lam duoc gi", "chuc nang"),
    "budget_planning": (
        "lap ngan sach",
        "ngan sach ca nhan",
        "phan bo thu nhap",
        "ke hoach chi tieu",
    ),
    "debt_management": (
        "no the tin dung",
        "tra no",
        "quan ly no",
        "dang no",
        "bi no",
    ),
    "financial_assessment": (
        "tai chinh cua toi",
        "danh gia tai chinh",
        "thu nhap cua toi",
        "chi tieu cua toi",
        "toi dang co",
        "tinh hinh cua toi",
        "tiet kiem cua toi",
        "tien tiet kiem",
        "chua co tiet kiem",
        "khong co tiet kiem",
    ),
    "recommendation": (
        "toi nen",
        "co nen",
        "nen lam gi",
        "tu van",
        "goi y",
        "khuyen nghi",
        "phu hop voi toi",
    ),
    "financial_knowledge": (
        "la gi",
        "tai sao",
        "bao nhieu",
        "nhu the nao",
        "cach nao",
        "quy tac",
    ),
}

_POSITIVE_CUES = {
    "cam on",
    "tot",
    "tuyet voi",
    "vui",
    "on dinh",
    "on",
    "hai long",
    "thanh cong",
}
_NEGATIVE_CUES = {
    "lo lang",
    "cang thang",
    "so hai",
    "kho khan",
    "khong du",
    "thieu tien",
    "vo no",
    "mat viec",
    "that nghiep",
    "be tac",
}

_NO_MATCH_MESSAGE = (
    "Mình chưa đủ chắc chắn để trả lời câu này. "
    "Bạn có thể nói rõ hơn chủ đề tài chính bạn đang quan tâm không?"
)


class EmbeddingProvider(Protocol):
    """Giao diện chung để có thể thay đổi mô hình embedding về sau."""

    def encode(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Trả về một vector embedding tương ứng với mỗi văn bản đầu vào."""


class SentenceTransformerEmbeddingProvider:
    """Bộ chuyển đổi giúp chỉ tải mô hình ``sentence-transformers`` khi cần."""

    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:  # pragma: no cover - phụ thuộc gói tùy chọn
            raise RuntimeError(
                "Chế độ embedding yêu cầu cài đặt bằng "
                "`pip install sentence-transformers`."
            ) from exc
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        return self._model.encode(list(texts), normalize_embeddings=True).tolist()


@dataclass(frozen=True)
class FAQMatch:
    """Một FAQ ứng viên cùng chi tiết các thành phần điểm."""

    item: dict
    score: float
    lexical_score: float
    embedding_score: float | None = None


@dataclass(frozen=True)
class FAQResult:
    """Kết quả phân tích có cấu trúc dành cho lớp chat hoặc API."""

    answer: str
    intent: str
    sentiment: str
    confidence: float
    status: str
    matches: tuple[FAQMatch, ...]


def load_faq(path: Path | None = None) -> list[dict]:
    """Đọc kho kiến thức FAQ từ tệp JSON."""
    with (path or _DATA).open(encoding="utf-8") as file:
        return json.load(file)


def normalize_text(text: str, *, remove_accents: bool = False) -> str:
    """Chuẩn hóa chữ hoa, Unicode, dấu câu và khoảng trắng thừa."""
    normalized = unicodedata.normalize("NFKC", text).lower().strip()
    if remove_accents:
        normalized = unicodedata.normalize("NFD", normalized)
        normalized = "".join(char for char in normalized if not unicodedata.combining(char))
        normalized = normalized.replace("đ", "d")
    return " ".join(_NON_WORDS.sub(" ", normalized).split())


def _tokens(text: str) -> set[str]:
    return set(normalize_text(text, remove_accents=True).split())


def _contains_phrase(text: str, phrase: str) -> bool:
    """So khớp cụm từ theo ranh giới từ, không khớp bên trong từ khác."""
    return f" {phrase} " in f" {text} "


def _dice(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return 2 * len(left & right) / (len(left) + len(right))


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    # Cosine của embedding có thể âm; độ tin cậy xếp hạng dùng thang 0..1.
    return max(0.0, min(1.0, (dot / (left_norm * right_norm) + 1) / 2))


def detect_intent(text: str) -> tuple[str, float]:
    """Nhận diện ý định hội thoại từ các cụm từ gợi ý gồm nhiều từ."""
    folded = normalize_text(text, remove_accents=True)
    scores: dict[str, float] = {}
    for intent, phrases in _INTENT_CUES.items():
        matches = [phrase for phrase in phrases if _contains_phrase(folded, phrase)]
        if matches:
            longest = max(len(phrase.split()) for phrase in matches)
            scores[intent] = min(1.0, 0.55 + 0.1 * longest + 0.05 * (len(matches) - 1))

    if not scores:
        return "financial_knowledge", 0.35
    intent, score = max(scores.items(), key=lambda item: item[1])
    return intent, score


def detect_sentiment(text: str) -> tuple[str, float]:
    """Nhận diện cảm xúc tích cực, tiêu cực hoặc trung tính từ các cụm từ."""
    folded = normalize_text(text, remove_accents=True)
    positive = sum(1 for phrase in _POSITIVE_CUES if _contains_phrase(folded, phrase))
    negative = sum(1 for phrase in _NEGATIVE_CUES if _contains_phrase(folded, phrase))
    if positive == negative:
        return "neutral", 0.5
    total = positive + negative
    if negative > positive:
        return "negative", min(1.0, 0.6 + negative / (2 * total))
    return "positive", min(1.0, 0.6 + positive / (2 * total))


class FAQEngine:
    """Xếp hạng FAQ theo từ vựng, ý định và vector ngữ nghĩa tùy chọn."""

    def __init__(
        self,
        faqs: Sequence[dict],
        *,
        embedding_provider: EmbeddingProvider | None = None,
        min_confidence: float = 0.38,
        ambiguity_margin: float = 0.04,
        embedding_weight: float = 0.45,
    ) -> None:
        if not faqs:
            raise ValueError("Kho kiến thức FAQ không được để trống")
        if not 0 <= embedding_weight <= 1:
            raise ValueError("embedding_weight phải nằm trong khoảng từ 0 đến 1")

        self.faqs = list(faqs)
        self.embedding_provider = embedding_provider
        self.min_confidence = min_confidence
        self.ambiguity_margin = ambiguity_margin
        self.embedding_weight = embedding_weight
        self._documents = [self._embedding_document(item) for item in self.faqs]
        self._faq_embeddings = (
            list(embedding_provider.encode(self._documents)) if embedding_provider else None
        )
        if self._faq_embeddings is not None and len(self._faq_embeddings) != len(self.faqs):
            raise ValueError("Bộ cung cấp embedding trả về sai số lượng vector")

    @staticmethod
    def _embedding_document(item: dict) -> str:
        keywords = ". ".join(item.get("keywords", []))
        return f"{item.get('question', '')}. {keywords}"

    @staticmethod
    def _item_intent(item: dict) -> str:
        prefix = str(item.get("id", "FAQ")).split("_", maxsplit=1)[0]
        return _INTENT_BY_PREFIX.get(prefix, "financial_knowledge")

    def _lexical_score(self, query: str, item: dict, intent: str) -> float:
        """Ưu tiên câu và cụm từ dài, cụ thể hơn các từ khóa đơn lẻ."""
        folded_query = normalize_text(query, remove_accents=True)
        query_tokens = set(folded_query.split())
        folded_question = normalize_text(item.get("question", ""), remove_accents=True)
        question_tokens = set(folded_question.split())

        keyword_phrases = [
            normalize_text(keyword, remove_accents=True)
            for keyword in item.get("keywords", [])
            if keyword.strip()
        ]
        exact_phrases = [
            phrase
            for phrase in keyword_phrases
            if phrase and _contains_phrase(folded_query, phrase)
        ]
        phrase_score = 0.0
        if exact_phrases:
            longest = max(len(phrase.split()) for phrase in exact_phrases)
            phrase_coverage = max(
                len(phrase.split()) / len(query_tokens) for phrase in exact_phrases
            )
            phrase_score = min(
                1.0,
                (0.55 + 0.12 * longest + 0.04 * (len(exact_phrases) - 1))
                * phrase_coverage,
            )

        keyword_overlap = max(
            (_dice(query_tokens, set(phrase.split())) for phrase in keyword_phrases),
            default=0.0,
        )
        question_overlap = _dice(query_tokens, question_tokens)
        sequence_score = SequenceMatcher(None, folded_query, folded_question).ratio()
        exact_question = 1.0 if folded_query == folded_question else 0.0
        intent_score = 1.0 if intent == self._item_intent(item) else 0.0

        return min(
            1.0,
            0.32 * phrase_score
            + 0.23 * keyword_overlap
            + 0.20 * question_overlap
            + 0.10 * sequence_score
            + 0.10 * intent_score
            + 0.05 * exact_question,
        )

    def rank(self, query: str, *, limit: int = 3) -> list[FAQMatch]:
        """Trả về các FAQ ứng viên theo thứ tự độ tin cậy kết hợp."""
        if not normalize_text(query):
            return []

        intent, _ = detect_intent(query)
        query_embedding = None
        if self.embedding_provider is not None:
            encoded = list(self.embedding_provider.encode([query]))
            if len(encoded) != 1:
                raise ValueError("Bộ cung cấp embedding phải trả về một vector truy vấn")
            query_embedding = encoded[0]

        matches = []
        for index, item in enumerate(self.faqs):
            lexical_score = self._lexical_score(query, item, intent)
            embedding_score = None
            score = lexical_score
            if query_embedding is not None and self._faq_embeddings is not None:
                embedding_score = _cosine(query_embedding, self._faq_embeddings[index])
                score = (
                    (1 - self.embedding_weight) * lexical_score
                    + self.embedding_weight * embedding_score
                )
            matches.append(
                FAQMatch(
                    item=item,
                    score=round(score, 6),
                    lexical_score=round(lexical_score, 6),
                    embedding_score=(
                        round(embedding_score, 6) if embedding_score is not None else None
                    ),
                )
            )

        return sorted(matches, key=lambda match: match.score, reverse=True)[:limit]

    def analyze(self, question: str) -> FAQResult:
        """Phân tích để trả lời, hỏi lại khi mơ hồ hoặc báo độ tin cậy thấp."""
        intent, _ = detect_intent(question)
        sentiment, _ = detect_sentiment(question)
        matches = tuple(self.rank(question, limit=3))
        if not matches:
            return FAQResult(
                answer=_NO_MATCH_MESSAGE,
                intent=intent,
                sentiment=sentiment,
                confidence=0.0,
                status="no_match",
                matches=matches,
            )

        top = matches[0]
        runner_up = matches[1] if len(matches) > 1 else None
        if top.score < self.min_confidence:
            return FAQResult(
                answer=_NO_MATCH_MESSAGE,
                intent=intent,
                sentiment=sentiment,
                confidence=top.score,
                status="no_match",
                matches=matches,
            )

        is_ambiguous = (
            runner_up is not None
            and top.score >= self.min_confidence * 0.8
            and top.score - runner_up.score <= self.ambiguity_margin
        )
        if is_ambiguous:
            options = "\n".join(
                f"{index}. {match.item['question']}" for index, match in enumerate(matches[:2], 1)
            )
            return FAQResult(
                answer=f"Mình tìm thấy hai chủ đề khá gần nhau. Bạn muốn hỏi:\n{options}",
                intent=intent,
                sentiment=sentiment,
                confidence=top.score,
                status="clarification",
                matches=matches,
            )

        return FAQResult(
            answer=top.item["answer"],
            intent=intent,
            sentiment=sentiment,
            confidence=top.score,
            status="answered",
            matches=matches,
        )


@lru_cache(maxsize=1)
def get_default_engine() -> FAQEngine:
    """Khởi tạo và lưu engine mặc định; embedding được bật qua biến môi trường."""
    model_name = os.getenv("FAQ_EMBEDDING_MODEL", "").strip()
    provider = SentenceTransformerEmbeddingProvider(model_name) if model_name else None
    return FAQEngine(load_faq(), embedding_provider=provider)


def analyze(question: str, faqs: list[dict] | None = None) -> FAQResult:
    """Trả về ý định, cảm xúc, độ tin cậy và câu trả lời có cấu trúc."""
    engine = FAQEngine(faqs) if faqs is not None else get_default_engine()
    return engine.analyze(question)


def answer(question: str, faqs: list[dict] | None = None) -> str:
    """Trả về chuỗi văn bản, tương thích với Streamlit và chatbot router hiện tại."""
    return analyze(question, faqs).answer
