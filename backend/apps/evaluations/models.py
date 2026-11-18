from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import BaseModel

SCORE_VALIDATORS = [MinValueValidator(1), MaxValueValidator(5)]


class EvalRun(BaseModel):
    class Mode(models.TextChoices):
        MULTI_AGENT = "multi_agent", "Несколько агентов"
        SINGLE_AI = "single_ai", "Один AI-ассистент"

    class Status(models.TextChoices):
        QUEUED = "queued", "В очереди"
        RUNNING = "running", "Выполняется"
        DONE = "done", "Готово"
        FAILED = "failed", "Ошибка"

    submission = models.ForeignKey("projects.Submission", on_delete=models.CASCADE, related_name="runs")
    rubric = models.ForeignKey("rubrics.Rubric", on_delete=models.PROTECT, related_name="runs")
    mode = models.CharField(max_length=20, choices=Mode.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    model_name = models.CharField(max_length=120, blank=True)
    prompt_version = models.CharField(max_length=30, blank=True)
    total_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    cost_usd = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    error = models.TextField(blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")


class CriterionScore(BaseModel):
    run = models.ForeignKey(EvalRun, on_delete=models.CASCADE, related_name="scores")
    criterion = models.ForeignKey("rubrics.Criterion", on_delete=models.PROTECT, related_name="scores")
    agent_type = models.CharField(max_length=30)
    ai_score = models.PositiveSmallIntegerField(validators=SCORE_VALIDATORS)
    teacher_score = models.PositiveSmallIntegerField(null=True, blank=True, validators=SCORE_VALIDATORS)
    justification = models.TextField(blank=True)
    missing = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = [("run", "criterion")]
        ordering = ["criterion__order"]


class Evidence(models.Model):
    score = models.ForeignKey(CriterionScore, on_delete=models.CASCADE, related_name="evidence")
    chunk = models.ForeignKey("projects.DocChunk", null=True, blank=True, on_delete=models.SET_NULL, related_name="evidence")
    slide_no = models.PositiveIntegerField(null=True, blank=True)
    quote = models.TextField()
    verified = models.BooleanField(default=False)


class TeacherReview(BaseModel):
    class Status(models.TextChoices):
        APPROVED = "approved", "Утверждено"
        NEEDS_REVISION = "needs_revision", "На доработку"

    run = models.OneToOneField(EvalRun, on_delete=models.CASCADE, related_name="review")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reviews")
    final_score = models.DecimalField(max_digits=4, decimal_places=2)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPROVED)


class ExpertRating(BaseModel):
    submission = models.ForeignKey("projects.Submission", on_delete=models.CASCADE, related_name="expert_ratings")
    criterion = models.ForeignKey("rubrics.Criterion", on_delete=models.PROTECT, related_name="expert_ratings")
    expert = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="expert_ratings")
    score = models.PositiveSmallIntegerField(validators=SCORE_VALIDATORS)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = [("submission", "criterion", "expert")]
