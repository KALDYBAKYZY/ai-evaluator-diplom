import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import BaseModel


class LtiPlatform(BaseModel):
    name = models.CharField(max_length=120)
    issuer = models.URLField()
    client_id = models.CharField(max_length=255)
    deployment_id = models.CharField(max_length=255)
    auth_login_url = models.URLField()
    auth_token_url = models.URLField()
    jwks_url = models.URLField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("issuer", "client_id")]

    def __str__(self):
        return self.name


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.ForeignKey(LtiPlatform, null=True, blank=True, on_delete=models.SET_NULL, related_name="users")
    lti_sub = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["platform", "lti_sub"],
                condition=~models.Q(lti_sub=""),
                name="unique_lti_user_per_platform",
            )
        ]


class Course(BaseModel):
    platform = models.ForeignKey(LtiPlatform, null=True, blank=True, on_delete=models.SET_NULL, related_name="courses")
    lti_context_id = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Enrollment(BaseModel):
    class Role(models.TextChoices):
        STUDENT = "student", "Студент"
        INSTRUCTOR = "instructor", "Преподаватель"
        EXPERT = "expert", "Эксперт"
        ADMIN = "admin", "Администратор"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)

    class Meta:
        unique_together = [("user", "course", "role")]


class Assignment(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    rubric = models.ForeignKey("rubrics.Rubric", null=True, blank=True, on_delete=models.SET_NULL, related_name="assignments")
    lti_resource_link_id = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255)
    due_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
