import time
from concurrent.futures import ThreadPoolExecutor

from evaluator.agents import get_agent
from evaluator.baseline import SingleAIBaseline
from evaluator.config import PROMPT_VERSION
from evaluator.llm import LLMClient
from evaluator.models import AgentResult, Chunk, CriterionSpec, EvaluationResult

MODES = ("multi_agent", "single_ai")


def weighted_total(results: list[AgentResult], criteria: list[CriterionSpec]) -> float:
    weights = {c.id: c.weight for c in criteria}
    total_weight = sum(weights.get(r.criterion_id, 0) for r in results)
    if total_weight == 0:
        return 0.0
    return round(sum(r.score * weights.get(r.criterion_id, 0) for r in results) / total_weight, 2)


def evaluate(mode: str, criteria: list[CriterionSpec], chunks: list[Chunk], llm: LLMClient | None = None, max_workers: int = 5) -> EvaluationResult:
    if mode not in MODES:
        raise ValueError(f"Unknown mode: {mode}")
    llm = llm or LLMClient()
    started = time.perf_counter()
    if mode == "multi_agent":
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            results = list(pool.map(lambda c: get_agent(c.agent_type).run(llm, c, chunks), criteria))
    else:
        results = SingleAIBaseline().run(llm, criteria, chunks)
    return EvaluationResult(
        mode=mode,
        model_name=llm.name,
        prompt_version=PROMPT_VERSION,
        results=results,
        total_score=weighted_total(results, criteria),
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
