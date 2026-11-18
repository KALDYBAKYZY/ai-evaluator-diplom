from rest_framework import viewsets

from apps.rubrics.models import Rubric
from apps.rubrics.serializers import RubricSerializer


class RubricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rubric.objects.prefetch_related("criteria")
    serializer_class = RubricSerializer
