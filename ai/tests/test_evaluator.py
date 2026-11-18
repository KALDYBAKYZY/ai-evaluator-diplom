from datetime import datetime, timedelta

from evaluator import Chunk, CriterionSpec, evaluate
from evaluator.evidence import verify
from evaluator.experiment import summary
from evaluator.investor import next_stage, remaining_seconds
from evaluator.models import Evidence

CHUNKS = [
    Chunk(1, "Студенты тратят много времени на поиск жилья рядом с вузом."),
    Chunk(2, "Мы зарабатываем на подписке 2000 тенге в месяц для арендодателей."),
]

CRITERIA = [
    CriterionSpec("c1", "market", "Рынок и клиент", "Сегмент и спрос", 0.2, "market"),
    CriterionSpec("c2", "business_model", "Бизнес-модель", "Способ заработка", 0.25, "business_model"),
    CriterionSpec("c3", "finance", "Финансы", "План", 0.2, "finance"),
    CriterionSpec("c4", "technology", "Технология", "MVP", 0.2, "technology"),
    CriterionSpec("c5", "innovation", "Инновационность", "Новизна", 0.15, "innovation"),
]


def test_verify_finds_quote_on_slide():
    item = verify(Evidence(slide_no=2, quote="зарабатываем на подписке"), CHUNKS)
    assert item.verified and item.slide_no == 2


def test_verify_rejects_invented_quote():
    item = verify(Evidence(slide_no=1, quote="у нас 10 000 платящих клиентов"), CHUNKS)
    assert not item.verified


def test_multi_agent_and_baseline_use_same_criteria():
    multi = evaluate("multi_agent", CRITERIA, CHUNKS)
    single = evaluate("single_ai", CRITERIA, CHUNKS)
    assert [r.criterion_id for r in multi.results] == [r.criterion_id for r in single.results]
    assert 1 <= multi.total_score <= 5


def test_timeline():
    start = datetime(2026, 1, 1, 10, 0, 0)
    assert next_stage(None) == "pitch"
    assert next_stage("pitch") == "qa"
    assert next_stage("feedback") is None
    assert remaining_seconds(300, start, start + timedelta(seconds=120)) == 180
    assert remaining_seconds(300, start, start + timedelta(seconds=400)) == 0


def test_metrics_summary():
    result = summary([3, 4, 2, 5], [3, 3, 2, 4])
    assert result["exact"] == 0.5
    assert result["within_one"] == 1.0
