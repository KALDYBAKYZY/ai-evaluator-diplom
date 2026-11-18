from rest_framework import serializers

from apps.projects.models import Document, Project, Submission


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "original_name", "file_type", "size_bytes", "created_at"]


class SubmissionSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Submission
        fields = ["id", "project", "version", "status", "documents", "created_at"]
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):
    latest_submission = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "course", "title", "description", "data_source", "consent_external_ai", "latest_submission", "created_at"]

    def get_latest_submission(self, obj):
        submission = obj.submissions.order_by("-version").first()
        return SubmissionSerializer(submission).data if submission else None
