from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pylti1p3.contrib.django import DjangoCacheDataStorage, DjangoMessageLaunch, DjangoOIDCLogin
from pylti1p3.exception import LtiException

from apps.audit.services import log_action
from apps.lti.services import sync_launch
from apps.lti.tool_conf import build_tool_conf


def storage():
    return DjangoCacheDataStorage(cache_name="default")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def oidc_login(request):
    target = request.GET.get("target_link_uri") or request.POST.get("target_link_uri")
    if not target:
        return HttpResponseBadRequest("target_link_uri is required")
    try:
        oidc = DjangoOIDCLogin(request, build_tool_conf(), launch_data_storage=storage())
        return oidc.enable_check_cookies().redirect(target)
    except LtiException as exc:
        return HttpResponseBadRequest(str(exc))


@csrf_exempt
@require_http_methods(["POST"])
def launch(request):
    try:
        message_launch = DjangoMessageLaunch(request, build_tool_conf(), launch_data_storage=storage())
        launch_data = message_launch.get_launch_data()
    except LtiException as exc:
        return HttpResponseBadRequest(str(exc))
    user, course, role = sync_launch(launch_data)
    login(request, user)
    log_action(user, "lti.launch", course, {"role": role})
    page = "teacher" if role == "instructor" else "student"
    return redirect(f"{settings.FRONTEND_URL}/{page}?course={course.id}")


def jwks(request):
    return JsonResponse(build_tool_conf().get_jwks(), safe=False)
