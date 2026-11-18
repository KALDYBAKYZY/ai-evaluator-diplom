from django.contrib import admin

from apps.evaluations.models import CriterionScore, EvalRun, Evidence, ExpertRating, TeacherReview


class CriterionScoreInline(admin.TabularInline):
    model = CriterionScore
    extra = 0


@admin.register(EvalRun)
class EvalRunAdmin(admin.ModelAdmin):
    list_display = ("id", "mode", "status", "total_score", "model_name", "duration_ms", "created_at")
    list_filter = ("mode", "status")
    inlines = [CriterionScoreInline]


admin.site.register(Evidence)
admin.site.register(TeacherReview)
admin.site.register(ExpertRating)
