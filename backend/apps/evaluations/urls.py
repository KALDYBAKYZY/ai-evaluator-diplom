from rest_framework.routers import DefaultRouter

from apps.evaluations.views import EvalRunViewSet, ExpertRatingViewSet

router = DefaultRouter()
router.register("runs", EvalRunViewSet, basename="run")
router.register("expert-ratings", ExpertRatingViewSet, basename="expert-rating")

urlpatterns = router.urls
