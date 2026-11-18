from django.contrib import admin

from apps.pitch.models import PitchMessage, PitchSession, PitchStage


class PitchStageInline(admin.TabularInline):
    model = PitchStage
    extra = 0


@admin.register(PitchSession)
class PitchSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "status", "model_name", "created_at")
    inlines = [PitchStageInline]


admin.site.register(PitchMessage)
