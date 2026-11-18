from evaluator.config import MAX_SCORE, MIN_SCORE
from evaluator.evidence import verify_all
from evaluator.llm import LLMClient
from evaluator.models import AgentResult, Chunk, CriterionSpec, Evidence
from evaluator.prompting import load, render_document, render_levels


class BaseAgent:
    agent_type: str = ""
    role: str = ""

    def build_prompt(self, criterion: CriterionSpec, chunks: list[Chunk]) -> str:
        return load("agent").format(
            role=self.role,
            code=criterion.code,
            name=criterion.name,
            description=criterion.description,
            levels=render_levels(criterion),
            document=render_document(chunks),
        )

    def run(self, llm: LLMClient, criterion: CriterionSpec, chunks: list[Chunk]) -> AgentResult:
        raw = llm.complete_json(load("system"), self.build_prompt(criterion, chunks))
        return to_result(raw, criterion, self.agent_type, chunks)


def clamp_score(value) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        return MIN_SCORE
    return max(MIN_SCORE, min(MAX_SCORE, score))


def to_result(raw: dict, criterion: CriterionSpec, agent_type: str, chunks: list[Chunk]) -> AgentResult:
    evidence = [
        Evidence(slide_no=item.get("slide_no"), quote=str(item.get("quote", "")))
        for item in raw.get("evidence", [])
        if isinstance(item, dict)
    ]
    return AgentResult(
        criterion_id=criterion.id,
        agent_type=agent_type,
        score=clamp_score(raw.get("score")),
        justification=str(raw.get("justification", "")),
        evidence=verify_all(evidence, chunks),
        missing=[str(m) for m in raw.get("missing", [])],
    )
