from django.urls import path

from apps.lti.views import jwks, launch, oidc_login

urlpatterns = [
    path("login/", oidc_login, name="lti-login"),
    path("launch/", launch, name="lti-launch"),
    path("jwks/", jwks, name="lti-jwks"),
]
