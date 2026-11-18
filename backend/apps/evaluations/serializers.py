from rest_framework import serializers

from apps.evaluations.models import CriterionScore, EvalRun, Evidence, ExpertRating, TeacherReview


class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = ["id", "slide_no", "quote", "verified"]


class CriterionScoreSerializer(serializers.ModelSerializer):
    criterion_name = serializers.CharField(source="criterion.name", read_only=True)
    weight = serializers.DecimalField(source="criterion.weight", max_digits=4, decimal_places=2, read_only=True)
    evidence = EvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = CriterionScore
        fields = ["id", "criterion", "criterion_name", "weight", "agent_type", "ai_score", "teacher_score", "justification", "missing", "evidence"]
        read_only_fields = ["criterion", "agent_type", "ai_score", "justification", "missing"]


class TeacherReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherReview
        fields = ["id", "final_score", "comment", "status", "reviewer", "created_at"]
        read_only_fields = ["final_score", "reviewer", "created_at"]


class EvalRunSerializer(serializers.ModelSerializer):
    scores = CriterionScoreSerializer(many=True, read_only=True)
    review = TeacherReviewSerializer(read_only=True)

    class Meta:
        model = EvalRun
        fields = ["id", "submission", "rubric", "mode", "status", "model_name", "prompt_version", "total_score", "duration_ms", "error", "scores", "review", "created_at"]
        read_only_fields = fields


class StartRunSerializer(serializers.Serializer):
    submission = serializers.UUIDField()
    mode = serializers.ChoiceField(choices=EvalRun.Mode.choices, default=EvalRun.Mode.MULTI_AGENT)
    rubric = serializers.UUIDField(required=False)


class ScoreOverrideSerializer(serializers.Serializer):
    criterion_score = serializers.UUIDField()
    teacher_score = serializers.IntegerField(min_value=1, max_value=5)


class ReviewInputSerializer(serializers.Serializer):
    overrides = ScoreOverrideSerializer(many=True, required=False)
    comment = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=TeacherReview.Status.choices, default=TeacherReview.Status.APPROVED)


class ExpertRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertRating
        fields = ["id", "submission", "criterion", "score", "comment", "created_at"]
