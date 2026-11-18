from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class PitchSession(BaseModel):
    class Status(models.TextChoices):
        CREATED = "created", "Создана"
        PITCH = "pitch", "Питч"
        QA = "qa", "Вопросы"
        FEEDBACK = "feedback", "Обратная связь"
        FINISHED = "finished", "Завершена"

    submission = models.ForeignKey("projects.Submission", on_delete=models.CASCADE, related_name="pitch_sessions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pitch_sessions")
    model_name = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    questions = models.JSONField(default=list, blank=True)
    feedback = models.JSONField(default=dict, blank=True)


class PitchStage(BaseModel):
    session = models.ForeignKey(PitchSession, on_delete=models.CASCADE, related_name="stages")
    stage = models.CharField(max_length=20)
    planned_sec = models.PositiveIntegerField()
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    auto_ended = models.BooleanField(default=False)

    class Meta:
        ordering = ["started_at"]

    @property
    def actual_sec(self) -> int | None:
        if not self.ended_at:
            return None
        return int((self.ended_at - self.started_at).total_seconds())


class PitchMessage(BaseModel):
    class Speaker(models.TextChoices):
        STUDENT = "student", "Студент"
        INVESTOR = "investor", "Инвестор"

    session = models.ForeignKey(PitchSession, on_delete=models.CASCADE, related_name="messages")
    stage = models.CharField(max_length=20)
    speaker = models.CharField(max_length=20, choices=Speaker.choices)
    content = models.TextField()
    offset_sec = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["created_at"]
