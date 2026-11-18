from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from apps.accounts.models import Enrollment
from apps.audit.services import log_action
from apps.common.permissions import can_access_project, has_course_role
from apps.projects.models import Project, TeamMember
from apps.projects.serializers import ProjectSerializer, SubmissionSerializer
from apps.projects.services import UploadError, create_submission


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Project.objects.all()
        teaching = Enrollment.objects.filter(
            user=user, role__in=[Enrollment.Role.INSTRUCTOR, Enrollment.Role.ADMIN]
        ).values("course_id")
        return Project.objects.filter(Q(course_id__in=teaching) | Q(members__user=user)).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if not has_course_role(self.request.user, course.id, *Enrollment.Role.values):
            raise PermissionDenied("Нет доступа к курсу")
        project = serializer.save(created_by=self.request.user)
        TeamMember.objects.get_or_create(project=project, user=self.request.user)
        log_action(self.request.user, "project.create", project)

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser])
    def submissions(self, request, pk=None):
        project = self.get_object()
        if not can_access_project(request.user, project):
            raise PermissionDenied()
        uploaded = request.FILES.get("file")
        if not uploaded:
            raise ValidationError({"file": "Файл обязателен"})
        try:
            submission = create_submission(project, uploaded, request.user)
        except UploadError as exc:
            raise ValidationError({"file": str(exc)}) from exc
        log_action(request.user, "submission.upload", submission)
        return Response(SubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
