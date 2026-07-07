from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ExclusionViewSet, SourceListView, StatsView

router = DefaultRouter()
router.register("exclusions", ExclusionViewSet, basename="exclusion")

urlpatterns = [
    path("", include(router.urls)),
    path("sources/", SourceListView.as_view(), name="sources"),
    path("stats/", StatsView.as_view(), name="stats"),
]
