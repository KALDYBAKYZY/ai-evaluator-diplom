from rest_framework.permissions import BasePermission

from apps.accounts.models import Enrollment


def has_course_role(user, course_id, *roles: str) -> bool:
    if user.is_superuser:
        return True
    return Enrollment.objects.filter(user=user, course_id=course_id, role__in=roles).exists()


def is_instructor(user, course_id) -> bool:
    return has_course_role(user, course_id, Enrollment.Role.INSTRUCTOR, Enrollment.Role.ADMIN)


def can_access_project(user, project) -> bool:
    if is_instructor(user, project.course_id):
        return True
    return project.members.filter(user=user).exists()


class IsInstructorOfCourse(BasePermission):
    def has_object_permission(self, request, view, obj):
        course_id = getattr(obj, "course_id", None)
        return course_id is not None and is_instructor(request.user, course_id)
