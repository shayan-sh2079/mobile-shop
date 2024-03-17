from django.urls import path

from orders.views import BuyView, OrdersView

urlpatterns = [path("", OrdersView.as_view()), path("buy/", BuyView.as_view())]
