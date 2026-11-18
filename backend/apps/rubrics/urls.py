from rest_framework.routers import DefaultRouter

from apps.rubrics.views import RubricViewSet

router = DefaultRouter()
router.register("rubrics", RubricViewSet, basename="rubric")

urlpatterns = router.urls
