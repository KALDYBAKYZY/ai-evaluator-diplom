from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.response import Response
from rest_framework.views import APIView


@method_decorator(ensure_csrf_cookie, name="dispatch")
class MeView(APIView):
    def get(self, request):
        user = request.user
        enrollments = user.enrollments.select_related("course")
        return Response(
            {
                "id": str(user.id),
                "name": user.get_full_name() or user.username,
                "is_superuser": user.is_superuser,
                "courses": [
                    {"id": str(e.course_id), "title": e.course.title, "role": e.role} for e in enrollments
                ],
            }
        )
