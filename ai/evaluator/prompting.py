from functools import lru_cache
from pathlib import Path

from evaluator.models import Chunk, CriterionSpec

PROMPTS_DIR = Path(__file__).parent / "prompts"


@lru_cache
def load(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def render_document(chunks: list[Chunk]) -> str:
    return "\n\n".join(f"[slide {c.slide_no}]\n{c.content.strip()}" for c in chunks if c.content.strip())


def render_levels(criterion: CriterionSpec) -> str:
    if not criterion.levels:
        return "1 — не раскрыто; 3 — раскрыто частично; 5 — раскрыто полно и подтверждено"
    return "\n".join(f"{k} — {v}" for k, v in sorted(criterion.levels.items()))


def render_criterion(criterion: CriterionSpec) -> str:
    return f"code: {criterion.code}\nname: {criterion.name}\ndescription: {criterion.description}\nlevels:\n{render_levels(criterion)}"
