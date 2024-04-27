from django.urls import include, path
from rest_framework.routers import DefaultRouter

from orders.views import BuyView, OrderDetailView, OrdersView

router = DefaultRouter()
router.register(r"buy", BuyView, basename="buy_list")

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"order/", OrdersView.as_view()),
    path(r"order/<int:pk>/", OrderDetailView.as_view()),
]
