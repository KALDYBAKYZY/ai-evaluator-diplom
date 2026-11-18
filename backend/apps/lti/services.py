from django.db import transaction

from apps.accounts.models import Course, Enrollment, LtiPlatform, User

INSTRUCTOR_MARKERS = ("Instructor", "Administrator", "ContentDeveloper", "TeachingAssistant")


def map_role(lti_roles: list[str]) -> str:
    if any(marker in role for role in lti_roles for marker in INSTRUCTOR_MARKERS):
        return Enrollment.Role.INSTRUCTOR
    return Enrollment.Role.STUDENT


@transaction.atomic
def sync_launch(launch_data: dict) -> tuple[User, Course, str]:
    issuer = launch_data["iss"]
    client_id = launch_data["aud"] if isinstance(launch_data["aud"], str) else launch_data["aud"][0]
    platform = LtiPlatform.objects.get(issuer=issuer, client_id=client_id)
    sub = launch_data["sub"]
    user, _ = User.objects.get_or_create(
        platform=platform,
        lti_sub=sub,
        defaults={"username": f"lti_{platform.pk.hex[:8]}_{sub}"[:150]},
    )
    user.first_name = launch_data.get("given_name", "")[:150]
    user.last_name = launch_data.get("family_name", "")[:150]
    user.email = launch_data.get("email", "")
    user.save(update_fields=["first_name", "last_name", "email"])
    context = launch_data.get("https://purl.imsglobal.org/spec/lti/claim/context", {})
    course, _ = Course.objects.get_or_create(
        platform=platform,
        lti_context_id=context.get("id", "default"),
        defaults={"title": context.get("title", "Canvas course")},
    )
    role = map_role(launch_data.get("https://purl.imsglobal.org/spec/lti/claim/roles", []))
    Enrollment.objects.get_or_create(user=user, course=course, role=role)
    return user, course, role
