from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Rubric(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        APPROVED = "approved", "Согласована"
        ARCHIVED = "archived", "В архиве"

    title = models.CharField(max_length=255)
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        unique_together = [("title", "version")]

    def __str__(self):
        return f"{self.title} v{self.version}"


class Criterion(BaseModel):
    class AgentType(models.TextChoices):
        MARKET = "market", "Рынок и клиент"
        BUSINESS_MODEL = "business_model", "Бизнес-модель"
        FINANCE = "finance", "Финансы"
        TECHNOLOGY = "technology", "Технология"
        INNOVATION = "innovation", "Инновационность"

    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, related_name="criteria")
    code = models.SlugField(max_length=50)
    name = models.CharField(max_length=255)
    description = models.TextField()
    weight = models.DecimalField(max_digits=4, decimal_places=2)
    agent_type = models.CharField(max_length=30, choices=AgentType.choices)
    levels = models.JSONField(default=dict, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = [("rubric", "code")]

    def __str__(self):
        return self.name
