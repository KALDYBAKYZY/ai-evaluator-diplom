from django.contrib import admin

from apps.projects.models import DocChunk, Document, Project, Submission, TeamMember


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "data_source", "consent_external_ai", "created_at")
    list_filter = ("data_source", "course")
    inlines = [TeamMemberInline]


admin.site.register(Submission)
admin.site.register(Document)
admin.site.register(DocChunk)
