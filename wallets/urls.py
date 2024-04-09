from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"transactions", views.TransactionsViewSet, basename="transactions")

urlpatterns = [
    path(r"", include(router.urls)),
]
