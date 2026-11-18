import hashlib
import tempfile
from pathlib import Path

from django.conf import settings
from django.db import transaction
from evaluator.extraction import detect_type, extract_chunks

from apps.projects.models import DocChunk, Document, Project, Submission


class UploadError(ValueError):
    pass


def validate_upload(uploaded) -> str:
    try:
        file_type = detect_type(uploaded.name)
    except ValueError as exc:
        raise UploadError("Разрешены только PDF и PPTX") from exc
    if uploaded.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise UploadError(f"Файл больше {settings.MAX_UPLOAD_MB} МБ")
    return file_type


def sha256_of(uploaded) -> str:
    digest = hashlib.sha256()
    for part in uploaded.chunks():
        digest.update(part)
    uploaded.seek(0)
    return digest.hexdigest()


@transaction.atomic
def create_submission(project: Project, uploaded, user) -> Submission:
    file_type = validate_upload(uploaded)
    last = project.submissions.order_by("-version").first()
    submission = Submission.objects.create(project=project, version=(last.version + 1) if last else 1, submitted_by=user)
    document = Document.objects.create(
        submission=submission,
        file=uploaded,
        original_name=Path(uploaded.name).name[:255],
        file_type=file_type,
        size_bytes=uploaded.size,
        sha256=sha256_of(uploaded),
    )
    ingest_document(document)
    submission.status = Submission.Status.READY
    submission.save(update_fields=["status", "updated_at"])
    return submission


def ingest_document(document: Document) -> int:
    with tempfile.NamedTemporaryFile(suffix=f".{document.file_type}") as tmp:
        with document.file.open("rb") as source:
            for part in iter(lambda: source.read(1024 * 1024), b""):
                tmp.write(part)
        tmp.flush()
        chunks = extract_chunks(tmp.name, document.file_type)
    DocChunk.objects.bulk_create(
        [DocChunk(document=document, slide_no=c.slide_no, content=c.content) for c in chunks]
    )
    return len(chunks)
