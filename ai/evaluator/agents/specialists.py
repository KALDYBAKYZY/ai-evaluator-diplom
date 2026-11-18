from evaluator.agents.base import BaseAgent


class MarketAgent(BaseAgent):
    agent_type = "market"
    role = "Аналитик рынка: целевой сегмент, размер рынка, конкуренты, подтверждение спроса."


class BusinessModelAgent(BaseAgent):
    agent_type = "business_model"
    role = "Эксперт по бизнес-моделям: клиент, проблема, ценность продукта, способ заработка, экономические допущения."


class FinanceAgent(BaseAgent):
    agent_type = "finance"
    role = "Финансовый аналитик: финансовый план, реалистичность расчётов, потребность в инвестициях."


class TechnologyAgent(BaseAgent):
    agent_type = "technology"
    role = "Технический эксперт: реализуемость решения, MVP или прототип, технические риски."


class InnovationAgent(BaseAgent):
    agent_type = "innovation"
    role = "Эксперт по инновациям: новизна, отличие от аналогов, масштабируемость."
