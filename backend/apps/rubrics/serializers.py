from rest_framework import serializers

from apps.rubrics.models import Criterion, Rubric


class CriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criterion
        fields = ["id", "code", "name", "description", "weight", "agent_type", "levels", "order"]


class RubricSerializer(serializers.ModelSerializer):
    criteria = CriterionSerializer(many=True, read_only=True)

    class Meta:
        model = Rubric
        fields = ["id", "title", "version", "status", "criteria"]
