from django.db import transaction
from django.utils import timezone
from evaluator.investor import InvestorMentor, is_expired, next_stage, planned_seconds, remaining_seconds
from evaluator.llm import LLMClient

from apps.evaluations.models import CriterionScore
from apps.evaluations.services import load_chunks
from apps.pitch.models import PitchMessage, PitchSession, PitchStage


def current_stage(session: PitchSession) -> PitchStage | None:
    return session.stages.filter(ended_at__isnull=True).order_by("-started_at").first()


def missing_aspects(session: PitchSession) -> list[str]:
    scores = CriterionScore.objects.filter(run__submission=session.submission, run__status="done").order_by("-run__created_at")
    seen: list[str] = []
    for score in scores[:10]:
        for item in score.missing:
            if item not in seen:
                seen.append(item)
    return seen


@transaction.atomic
def advance(session: PitchSession, auto: bool = False, llm: LLMClient | None = None) -> PitchSession:
    now = timezone.now()
    active = current_stage(session)
    if active:
        active.ended_at = now
        active.auto_ended = auto
        active.save(update_fields=["ended_at", "auto_ended", "updated_at"])
    upcoming = next_stage(active.stage if active else None)
    if upcoming is None:
        session.status = PitchSession.Status.FINISHED
        session.save(update_fields=["status", "updated_at"])
        return session
    PitchStage.objects.create(session=session, stage=upcoming, planned_sec=planned_seconds(upcoming), started_at=now)
    session.status = upcoming
    mentor = InvestorMentor(llm)
    session.model_name = mentor.llm.name
    chunks, _ = load_chunks(session.submission)
    if upcoming == PitchSession.Status.QA:
        session.questions = mentor.questions(chunks, missing_aspects(session))
        for question in session.questions:
            PitchMessage.objects.create(session=session, stage=upcoming, speaker=PitchMessage.Speaker.INVESTOR, content=question)
    if upcoming == PitchSession.Status.FEEDBACK:
        transcript = [(m.speaker, m.content) for m in session.messages.all()]
        session.feedback = mentor.feedback(chunks, transcript)
    session.save()
    return session


def sync_timer(session: PitchSession) -> PitchSession:
    active = current_stage(session)
    if active and is_expired(active.planned_sec, active.started_at, timezone.now()):
        return advance(session, auto=True)
    return session


def state(session: PitchSession) -> dict:
    active = current_stage(session)
    now = timezone.now()
    return {
        "id": str(session.id),
        "status": session.status,
        "stage": active.stage if active else None,
        "planned_sec": active.planned_sec if active else None,
        "remaining_sec": remaining_seconds(active.planned_sec, active.started_at, now) if active else None,
        "questions": session.questions,
        "feedback": session.feedback,
        "stages": [
            {"stage": s.stage, "planned_sec": s.planned_sec, "actual_sec": s.actual_sec, "auto_ended": s.auto_ended}
            for s in session.stages.all()
        ],
    }
