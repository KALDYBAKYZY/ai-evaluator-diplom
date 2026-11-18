from evaluator.llm import LLMClient
from evaluator.models import Chunk
from evaluator.prompting import load, render_document


class InvestorMentor:
    def __init__(self, llm: LLMClient | None = None, question_count: int = 4):
        self.llm = llm or LLMClient()
        self.question_count = question_count

    def questions(self, chunks: list[Chunk], missing: list[str]) -> list[str]:
        prompt = load("investor_questions").format(
            count=self.question_count,
            missing="\n".join(f"- {m}" for m in missing) or "- нет данных",
            document=render_document(chunks),
        )
        raw = self.llm.complete_json(load("system"), prompt)
        return [str(q) for q in raw.get("questions", [])][: self.question_count]

    def feedback(self, chunks: list[Chunk], transcript: list[tuple[str, str]]) -> dict:
        prompt = load("investor_feedback").format(
            document=render_document(chunks),
            transcript="\n".join(f"{speaker}: {text}" for speaker, text in transcript),
        )
        raw = self.llm.complete_json(load("system"), prompt)
        return {
            "strengths": [str(s) for s in raw.get("strengths", [])],
            "remarks": [str(r) for r in raw.get("remarks", [])],
            "slide_refs": [r for r in raw.get("slide_refs", []) if isinstance(r, int)],
        }
