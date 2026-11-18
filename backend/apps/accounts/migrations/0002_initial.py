import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("rubrics", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="assignment",
            name="rubric",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assignments",
                to="rubrics.rubric",
            ),
        ),
        migrations.AddField(
            model_name="assignment",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assignments",
                to="accounts.course",
            ),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="enrollments",
                to="accounts.course",
            ),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="enrollments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="ltiplatform",
            unique_together={("issuer", "client_id")},
        ),
        migrations.AddField(
            model_name="course",
            name="platform",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="courses",
                to="accounts.ltiplatform",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="platform",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="users",
                to="accounts.ltiplatform",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="enrollment",
            unique_together={("user", "course", "role")},
        ),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                condition=models.Q(("lti_sub", ""), _negated=True),
                fields=("platform", "lti_sub"),
                name="unique_lti_user_per_platform",
            ),
        ),
    ]
