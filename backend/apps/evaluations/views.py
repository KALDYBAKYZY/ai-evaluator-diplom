from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.accounts.models import Enrollment
from apps.audit.services import log_action
from apps.common.permissions import can_access_project, has_course_role, is_instructor
from apps.evaluations.models import CriterionScore, EvalRun, ExpertRating, TeacherReview
from apps.evaluations.serializers import (
    EvalRunSerializer,
    ExpertRatingSerializer,
    ReviewInputSerializer,
    StartRunSerializer,
)
from apps.evaluations.services import final_score_from_teacher
from apps.evaluations.tasks import run_evaluation
from apps.projects.models import Submission
from apps.rubrics.models import Rubric


class EvalRunViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = EvalRunSerializer

    def get_queryset(self):
        queryset = EvalRun.objects.select_related("submission__project").prefetch_related("scores__evidence", "scores__criterion")
        submission_id = self.request.query_params.get("submission")
        if submission_id:
            queryset = queryset.filter(submission_id=submission_id)
        user = self.request.user
        if user.is_superuser:
            return queryset
        teaching = Enrollment.objects.filter(
            user=user, role__in=[Enrollment.Role.INSTRUCTOR, Enrollment.Role.ADMIN]
        ).values("course_id")
        return queryset.filter(
            Q(submission__project__course_id__in=teaching) | Q(submission__project__members__user=user)
        ).distinct()

    def create(self, request):
        data = StartRunSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        submission = get_object_or_404(Submission.objects.select_related("project", "assignment__rubric"), id=data.validated_data["submission"])
        if not can_access_project(request.user, submission.project):
            raise PermissionDenied()
        rubric = self._pick_rubric(submission, data.validated_data.get("rubric"))
        run = EvalRun.objects.create(submission=submission, rubric=rubric, mode=data.validated_data["mode"], requested_by=request.user)
        log_action(request.user, "evaluation.start", run, {"mode": run.mode})
        transaction.on_commit(lambda: run_evaluation.delay(str(run.id)))
        return Response(EvalRunSerializer(run).data, status=status.HTTP_202_ACCEPTED)

    def _pick_rubric(self, submission, rubric_id):
        if rubric_id:
            return get_object_or_404(Rubric, id=rubric_id)
        if submission.assignment and submission.assignment.rubric:
            return submission.assignment.rubric
        rubric = Rubric.objects.order_by("-version").first()
        if not rubric:
            raise ValidationError("Нет рубрики. Выполните: python manage.py seed_demo")
        return rubric

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        run = self.get_object()
        if not is_instructor(request.user, run.submission.project.course_id):
            raise PermissionDenied("Утверждать оценку может только преподаватель")
        if run.status != EvalRun.Status.DONE:
            raise ValidationError("Оценка ещё не готова")
        data = ReviewInputSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        with transaction.atomic():
            for item in data.validated_data.get("overrides", []):
                CriterionScore.objects.filter(id=item["criterion_score"], run=run).update(teacher_score=item["teacher_score"])
            TeacherReview.objects.update_or_create(
                run=run,
                defaults={
                    "reviewer": request.user,
                    "final_score": final_score_from_teacher(run),
                    "comment": data.validated_data.get("comment", ""),
                    "status": data.validated_data["status"],
                },
            )
        log_action(request.user, "evaluation.review", run)
        run.refresh_from_db()
        return Response(EvalRunSerializer(run).data)

    def get_object(self):
        run = get_object_or_404(EvalRun, id=self.kwargs["pk"])
        if not (self.request.user.is_superuser or can_access_project(self.request.user, run.submission.project)):
            raise PermissionDenied()
        return run


class ExpertRatingViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ExpertRatingSerializer

    def get_queryset(self):
        return ExpertRating.objects.filter(expert=self.request.user)

    def perform_create(self, serializer):
        submission = serializer.validated_data["submission"]
        if not has_course_role(self.request.user, submission.project.course_id, Enrollment.Role.EXPERT):
            raise PermissionDenied("Только эксперт курса")
        serializer.save(expert=self.request.user)
