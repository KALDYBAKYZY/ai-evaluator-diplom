import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from pptx import Presentation
from rest_framework.test import APIClient

from apps.accounts.models import Course, User
from apps.projects.models import Project, TeamMember


def make_pptx() -> bytes:
    presentation = Presentation()
    for title, body in [
        ("Проблема", "Студенты тратят много времени на поиск жилья рядом с вузом."),
        ("Бизнес-модель", "Мы зарабатываем на подписке 2000 тенге в месяц для арендодателей."),
    ]:
        slide = presentation.slides.add_slide(presentation.slide_layouts[1])
        slide.shapes.title.text = title
        slide.placeholders[1].text = body
    buffer = io.BytesIO()
    presentation.save(buffer)
    return buffer.getvalue()


@pytest.fixture
def setup(db, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.CELERY_TASK_ALWAYS_EAGER = True
    call_command("seed_demo")
    course = Course.objects.get()
    student = User.objects.get(username="student")
    teacher = User.objects.get(username="teacher")
    project = Project.objects.create(course=course, title="Жильё для студентов")
    TeamMember.objects.create(project=project, user=student)
    return project, student, teacher


def client_for(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.mark.django_db(transaction=True)
def test_upload_evaluate_review_and_pitch(setup):
    project, student, teacher = setup
    student_api = client_for(student)

    upload = SimpleUploadedFile("pitch.pptx", make_pptx())
    response = student_api.post(f"/api/projects/{project.id}/submissions/", {"file": upload}, format="multipart")
    assert response.status_code == 201, response.data
    submission_id = response.data["id"]

    for mode in ("multi_agent", "single_ai"):
        response = student_api.post("/api/runs/", {"submission": submission_id, "mode": mode}, format="json")
        assert response.status_code == 202

    runs = student_api.get(f"/api/runs/?submission={submission_id}").data
    assert {r["mode"] for r in runs} == {"multi_agent", "single_ai"}
    assert all(r["status"] == "done" and len(r["scores"]) == 5 for r in runs)

    run = runs[0]
    response = student_api.post(f"/api/runs/{run['id']}/review/", {}, format="json")
    assert response.status_code == 403

    override = {"overrides": [{"criterion_score": run["scores"][0]["id"], "teacher_score": 5}], "comment": "Хорошо"}
    response = client_for(teacher).post(f"/api/runs/{run['id']}/review/", override, format="json")
    assert response.status_code == 200
    assert response.data["review"]["final_score"] is not None

    session = student_api.post("/api/pitch/sessions/", {"submission": submission_id}, format="json").data
    state = student_api.post(f"/api/pitch/sessions/{session['id']}/next/").data
    assert state["stage"] == "pitch" and state["remaining_sec"] <= 300
    state = student_api.post(f"/api/pitch/sessions/{session['id']}/next/").data
    assert state["stage"] == "qa" and state["questions"]
    student_api.post(f"/api/pitch/sessions/{session['id']}/messages/", {"content": "Наш клиент — арендодатели."}, format="json")
    state = student_api.post(f"/api/pitch/sessions/{session['id']}/next/").data
    assert state["stage"] == "feedback" and state["feedback"]["remarks"]
