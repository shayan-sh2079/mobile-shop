from django.urls import path

from orders.views import OrdersView

urlpatterns = [
    path("", OrdersView.as_view()),
]
