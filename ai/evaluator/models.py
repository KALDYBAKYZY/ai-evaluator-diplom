from dataclasses import dataclass, field


@dataclass(frozen=True)
class Chunk:
    slide_no: int
    content: str


@dataclass(frozen=True)
class CriterionSpec:
    id: str
    code: str
    name: str
    description: str
    weight: float
    agent_type: str
    levels: dict[str, str] = field(default_factory=dict)


@dataclass
class Evidence:
    slide_no: int | None
    quote: str
    verified: bool = False


@dataclass
class AgentResult:
    criterion_id: str
    agent_type: str
    score: int
    justification: str
    evidence: list[Evidence] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)


@dataclass
class EvaluationResult:
    mode: str
    model_name: str
    prompt_version: str
    results: list[AgentResult]
    total_score: float
    duration_ms: int
