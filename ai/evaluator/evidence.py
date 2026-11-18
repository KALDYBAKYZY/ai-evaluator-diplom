import re

from evaluator.models import Chunk, Evidence


def normalize(text: str) -> str:
    text = text.lower().replace("ё", "е")
    text = re.sub(r"[«»\"'“”„]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def verify(evidence: Evidence, chunks: list[Chunk], min_length: int = 8) -> Evidence:
    quote = normalize(evidence.quote)
    if len(quote) < min_length:
        evidence.verified = False
        return evidence
    candidates = [c for c in chunks if c.slide_no == evidence.slide_no] or chunks
    for chunk in candidates:
        if quote in normalize(chunk.content):
            evidence.slide_no = chunk.slide_no
            evidence.verified = True
            return evidence
    evidence.verified = False
    return evidence


def verify_all(items: list[Evidence], chunks: list[Chunk]) -> list[Evidence]:
    return [verify(item, chunks) for item in items]
