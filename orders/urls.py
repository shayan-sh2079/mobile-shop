from django.urls import include, path
from rest_framework.routers import DefaultRouter

from orders.views import BuyView, OrdersView

router = DefaultRouter()
router.register(r"order", OrdersView, basename="order_list")
router.register(r"buy", BuyView, basename="buy_list")

urlpatterns = [path(r"", include(router.urls))]
