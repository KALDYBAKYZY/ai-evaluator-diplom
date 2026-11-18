from django.urls import path

from apps.pitch.views import SessionDetailView, SessionListView, SessionMessageView, SessionNextView

urlpatterns = [
    path("sessions/", SessionListView.as_view()),
    path("sessions/<uuid:pk>/", SessionDetailView.as_view()),
    path("sessions/<uuid:pk>/next/", SessionNextView.as_view()),
    path("sessions/<uuid:pk>/messages/", SessionMessageView.as_view()),
]
