from celery import shared_task

from apps.evaluations.models import EvalRun
from apps.evaluations.services import execute_run


@shared_task
def run_evaluation(run_id: str) -> str:
    run = EvalRun.objects.select_related("submission__project", "rubric").get(id=run_id)
    run.status = EvalRun.Status.RUNNING
    run.save(update_fields=["status", "updated_at"])
    try:
        execute_run(run)
    except Exception as exc:
        run.status = EvalRun.Status.FAILED
        run.error = str(exc)[:2000]
        run.save(update_fields=["status", "error", "updated_at"])
    return run.status
