import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("projects", "0001_initial"),
        ("rubrics", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EvalRun",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "mode",
                    models.CharField(
                        choices=[
                            ("multi_agent", "Несколько агентов"),
                            ("single_ai", "Один AI-ассистент"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("queued", "В очереди"),
                            ("running", "Выполняется"),
                            ("done", "Готово"),
                            ("failed", "Ошибка"),
                        ],
                        default="queued",
                        max_length=20,
                    ),
                ),
                ("model_name", models.CharField(blank=True, max_length=120)),
                ("prompt_version", models.CharField(blank=True, max_length=30)),
                (
                    "total_score",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=4, null=True
                    ),
                ),
                ("duration_ms", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "cost_usd",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=8, null=True
                    ),
                ),
                ("error", models.TextField(blank=True)),
                (
                    "requested_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "rubric",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="runs",
                        to="rubrics.rubric",
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="runs",
                        to="projects.submission",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="CriterionScore",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("agent_type", models.CharField(max_length=30)),
                (
                    "ai_score",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ]
                    ),
                ),
                (
                    "teacher_score",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                    ),
                ),
                ("justification", models.TextField(blank=True)),
                ("missing", models.JSONField(blank=True, default=list)),
                (
                    "criterion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="scores",
                        to="rubrics.criterion",
                    ),
                ),
                (
                    "run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scores",
                        to="evaluations.evalrun",
                    ),
                ),
            ],
            options={
                "ordering": ["criterion__order"],
                "unique_together": {("run", "criterion")},
            },
        ),
        migrations.CreateModel(
            name="Evidence",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("slide_no", models.PositiveIntegerField(blank=True, null=True)),
                ("quote", models.TextField()),
                ("verified", models.BooleanField(default=False)),
                (
                    "chunk",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="evidence",
                        to="projects.docchunk",
                    ),
                ),
                (
                    "score",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evidence",
                        to="evaluations.criterionscore",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TeacherReview",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("final_score", models.DecimalField(decimal_places=2, max_digits=4)),
                ("comment", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("approved", "Утверждено"),
                            ("needs_revision", "На доработку"),
                        ],
                        default="approved",
                        max_length=20,
                    ),
                ),
                (
                    "reviewer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "run",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="review",
                        to="evaluations.evalrun",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ExpertRating",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "score",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ]
                    ),
                ),
                ("comment", models.TextField(blank=True)),
                (
                    "criterion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="expert_ratings",
                        to="rubrics.criterion",
                    ),
                ),
                (
                    "expert",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="expert_ratings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expert_ratings",
                        to="projects.submission",
                    ),
                ),
            ],
            options={
                "unique_together": {("submission", "criterion", "expert")},
            },
        ),
    ]
