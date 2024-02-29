from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"", views.MobileViewSet, basename="mobiles")

urlpatterns = [
    path(r"", include(router.urls)),
]
