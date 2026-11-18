from evaluator.agents.base import to_result
from evaluator.llm import LLMClient
from evaluator.models import AgentResult, Chunk, CriterionSpec
from evaluator.prompting import load, render_criterion, render_document


class SingleAIBaseline:
    agent_type = "single_ai"

    def build_prompt(self, criteria: list[CriterionSpec], chunks: list[Chunk]) -> str:
        return load("baseline").format(
            criteria="\n\n".join(render_criterion(c) for c in criteria),
            document=render_document(chunks),
        )

    def run(self, llm: LLMClient, criteria: list[CriterionSpec], chunks: list[Chunk]) -> list[AgentResult]:
        raw = llm.complete_json(load("system"), self.build_prompt(criteria, chunks))
        by_code = {item.get("code"): item for item in raw.get("criteria", []) if isinstance(item, dict)}
        return [to_result(by_code.get(c.code, {}), c, self.agent_type, chunks) for c in criteria]
