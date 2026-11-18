import subprocess

import pytest

from apps.accounts.models import Enrollment, LtiPlatform
from apps.lti.services import map_role, sync_launch
from apps.lti.tool_conf import build_tool_conf


@pytest.fixture
def keys(tmp_path, settings):
    private_key = tmp_path / "private.key"
    public_key = tmp_path / "public.key"
    subprocess.run(["openssl", "genrsa", "-out", str(private_key), "2048"], check=True, capture_output=True)
    subprocess.run(["openssl", "rsa", "-in", str(private_key), "-pubout", "-out", str(public_key)], check=True, capture_output=True)
    settings.LTI_PRIVATE_KEY_PATH = private_key
    settings.LTI_PUBLIC_KEY_PATH = public_key


@pytest.fixture
def platform(db):
    return LtiPlatform.objects.create(
        name="Canvas test",
        issuer="https://canvas.test.instructure.com",
        client_id="10000000000001",
        deployment_id="1:abc",
        auth_login_url="http://localhost:3000/api/lti/authorize_redirect",
        auth_token_url="http://localhost:3000/login/oauth2/token",
        jwks_url="http://localhost:3000/api/lti/security/jwks",
    )


def test_jwks_contains_public_key(keys, platform):
    jwks = build_tool_conf().get_jwks()
    assert jwks["keys"] and jwks["keys"][0]["kty"] == "RSA"


def test_role_mapping():
    assert map_role(["http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor"]) == Enrollment.Role.INSTRUCTOR
    assert map_role(["http://purl.imsglobal.org/vocab/lis/v2/membership#Learner"]) == Enrollment.Role.STUDENT


def test_sync_launch_creates_user_course_and_role(platform):
    user, course, role = sync_launch(
        {
            "iss": platform.issuer,
            "aud": platform.client_id,
            "sub": "user-123",
            "given_name": "Айгерим",
            "https://purl.imsglobal.org/spec/lti/claim/context": {"id": "ctx-1", "title": "Предпринимательство"},
            "https://purl.imsglobal.org/spec/lti/claim/roles": ["http://purl.imsglobal.org/vocab/lis/v2/membership#Learner"],
        }
    )
    assert user.first_name == "Айгерим" and course.title == "Предпринимательство" and role == "student"
