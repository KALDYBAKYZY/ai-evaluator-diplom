import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Rubric",
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
                ("title", models.CharField(max_length=255)),
                ("version", models.PositiveIntegerField(default=1)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Черновик"),
                            ("approved", "Согласована"),
                            ("archived", "В архиве"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("title", "version")},
            },
        ),
        migrations.CreateModel(
            name="Criterion",
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
                ("code", models.SlugField()),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("weight", models.DecimalField(decimal_places=2, max_digits=4)),
                (
                    "agent_type",
                    models.CharField(
                        choices=[
                            ("market", "Рынок и клиент"),
                            ("business_model", "Бизнес-модель"),
                            ("finance", "Финансы"),
                            ("technology", "Технология"),
                            ("innovation", "Инновационность"),
                        ],
                        max_length=30,
                    ),
                ),
                ("levels", models.JSONField(blank=True, default=dict)),
                ("order", models.PositiveSmallIntegerField(default=0)),
                (
                    "rubric",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="criteria",
                        to="rubrics.rubric",
                    ),
                ),
            ],
            options={
                "ordering": ["order"],
                "unique_together": {("rubric", "code")},
            },
        ),
    ]
