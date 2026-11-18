from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Project(BaseModel):
    class DataSource(models.TextChoices):
        SYNTHETIC = "synthetic", "Синтетический кейс"
        EDUCATIONAL = "educational", "Учебный кейс"
        PAST_WORK = "past_work", "Работа прошлых лет"

    course = models.ForeignKey("accounts.Course", on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    data_source = models.CharField(max_length=20, choices=DataSource.choices, default=DataSource.SYNTHETIC)
    consent_external_ai = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")

    def __str__(self):
        return self.title

    @property
    def can_send_to_external_ai(self) -> bool:
        return self.data_source != self.DataSource.PAST_WORK or self.consent_external_ai


class TeamMember(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="team_memberships")

    class Meta:
        unique_together = [("project", "user")]


class Submission(BaseModel):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Загружено"
        PROCESSING = "processing", "Обработка"
        READY = "ready", "Готово"
        FAILED = "failed", "Ошибка"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="submissions")
    assignment = models.ForeignKey("accounts.Assignment", null=True, blank=True, on_delete=models.SET_NULL, related_name="submissions")
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        unique_together = [("project", "version")]
        ordering = ["-version"]


def document_upload_path(instance, filename):
    return f"submissions/{instance.submission_id}/{filename}"


class Document(BaseModel):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to=document_upload_path)
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)
    size_bytes = models.PositiveIntegerField(default=0)
    sha256 = models.CharField(max_length=64)


class DocChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    slide_no = models.PositiveIntegerField()
    content = models.TextField()

    class Meta:
        ordering = ["slide_no"]
        unique_together = [("document", "slide_no")]
