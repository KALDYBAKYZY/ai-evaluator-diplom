from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from evaluator import Chunk, CriterionSpec, evaluate
from evaluator.llm import LLMClient

from apps.evaluations.models import CriterionScore, EvalRun, Evidence
from apps.projects.models import DocChunk


def load_chunks(submission) -> tuple[list[Chunk], dict[int, DocChunk]]:
    rows = list(DocChunk.objects.filter(document__submission=submission).order_by("slide_no"))
    return [Chunk(r.slide_no, r.content) for r in rows], {r.slide_no: r for r in rows}


def load_criteria(rubric) -> list[CriterionSpec]:
    return [
        CriterionSpec(
            id=str(c.id),
            code=c.code,
            name=c.name,
            description=c.description,
            weight=float(c.weight),
            agent_type=c.agent_type,
            levels=c.levels,
        )
        for c in rubric.criteria.all()
    ]


def execute_run(run: EvalRun, llm: LLMClient | None = None) -> EvalRun:
    project = run.submission.project
    if not project.can_send_to_external_ai and (llm or LLMClient()).provider != "mock":
        raise PermissionError("Нет согласия на передачу работы внешним AI-сервисам")
    chunks, by_slide = load_chunks(run.submission)
    criteria = load_criteria(run.rubric)
    result = evaluate(run.mode, criteria, chunks, llm)
    with transaction.atomic():
        run.scores.all().delete()
        for item in result.results:
            score = CriterionScore.objects.create(
                run=run,
                criterion_id=item.criterion_id,
                agent_type=item.agent_type,
                ai_score=item.score,
                justification=item.justification,
                missing=item.missing,
            )
            Evidence.objects.bulk_create(
                [
                    Evidence(score=score, chunk=by_slide.get(e.slide_no), slide_no=e.slide_no, quote=e.quote, verified=e.verified)
                    for e in item.evidence
                ]
            )
        run.model_name = result.model_name
        run.prompt_version = result.prompt_version
        run.total_score = Decimal(str(result.total_score))
        run.duration_ms = result.duration_ms
        run.status = EvalRun.Status.DONE
        run.error = ""
        run.save()
    return run


def final_score_from_teacher(run: EvalRun) -> Decimal:
    total_weight = Decimal("0")
    total = Decimal("0")
    for score in run.scores.select_related("criterion"):
        value = score.teacher_score or score.ai_score
        total += Decimal(value) * score.criterion.weight
        total_weight += score.criterion.weight
    return (total / total_weight).quantize(Decimal("0.01")) if total_weight else Decimal("0")


def rubric_weight_sum(rubric) -> Decimal:
    return rubric.criteria.aggregate(total=Sum("weight"))["total"] or Decimal("0")
