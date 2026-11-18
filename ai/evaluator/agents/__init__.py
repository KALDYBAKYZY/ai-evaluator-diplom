from evaluator.agents.base import BaseAgent
from evaluator.agents.specialists import (
    BusinessModelAgent,
    FinanceAgent,
    InnovationAgent,
    MarketAgent,
    TechnologyAgent,
)

REGISTRY: dict[str, BaseAgent] = {
    agent.agent_type: agent
    for agent in (MarketAgent(), BusinessModelAgent(), FinanceAgent(), TechnologyAgent(), InnovationAgent())
}


def get_agent(agent_type: str) -> BaseAgent:
    if agent_type not in REGISTRY:
        raise KeyError(f"No agent for type: {agent_type}")
    return REGISTRY[agent_type]


__all__ = ["BaseAgent", "REGISTRY", "get_agent"]
