from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import can_access_project
from apps.pitch.models import PitchMessage, PitchSession
from apps.pitch.services import advance, current_stage, state, sync_timer
from apps.projects.models import Submission


class CreateSessionSerializer(serializers.Serializer):
    submission = serializers.UUIDField()


class MessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=5000)


def get_session(request, pk) -> PitchSession:
    session = get_object_or_404(PitchSession.objects.select_related("submission__project"), id=pk)
    if not can_access_project(request.user, session.submission.project):
        raise PermissionDenied()
    return session


class SessionListView(APIView):
    def post(self, request):
        data = CreateSessionSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        submission = get_object_or_404(Submission.objects.select_related("project"), id=data.validated_data["submission"])
        if not can_access_project(request.user, submission.project):
            raise PermissionDenied()
        session = PitchSession.objects.create(submission=submission, student=request.user)
        return Response(state(session), status=status.HTTP_201_CREATED)


class SessionDetailView(APIView):
    def get(self, request, pk):
        return Response(state(sync_timer(get_session(request, pk))))


class SessionNextView(APIView):
    def post(self, request, pk):
        session = get_session(request, pk)
        if session.status == PitchSession.Status.FINISHED:
            raise ValidationError("Сессия уже завершена")
        return Response(state(advance(session)))


class SessionMessageView(APIView):
    def post(self, request, pk):
        session = sync_timer(get_session(request, pk))
        active = current_stage(session)
        if not active or active.stage not in (PitchSession.Status.PITCH, PitchSession.Status.QA):
            raise ValidationError("Сейчас нельзя отправлять ответы")
        data = MessageSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        PitchMessage.objects.create(
            session=session,
            stage=active.stage,
            speaker=PitchMessage.Speaker.STUDENT,
            content=data.validated_data["content"],
            offset_sec=int((timezone.now() - active.started_at).total_seconds()),
        )
        return Response(state(session), status=status.HTTP_201_CREATED)
