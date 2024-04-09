from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("", views.ReviewsView, basename="reviews")

urlpatterns = [
    path(r"", include(router.urls)),
]
