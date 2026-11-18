from django.contrib import admin

from apps.rubrics.models import Criterion, Rubric


class CriterionInline(admin.TabularInline):
    model = Criterion
    extra = 0


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    list_display = ("title", "version", "status")
    inlines = [CriterionInline]
