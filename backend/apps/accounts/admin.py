from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import Assignment, Course, Enrollment, LtiPlatform, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (("LTI", {"fields": ("platform", "lti_sub")}),)
    list_display = ("username", "email", "first_name", "last_name", "platform", "is_staff")


admin.site.register(LtiPlatform)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Assignment)
