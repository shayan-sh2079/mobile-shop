from rest_framework import permissions
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import OrderSerializer


class OrdersView(GenericAPIView, CreateModelMixin):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        mobile_id = self.request.query_params.get("mobile")
        is_purchased = bool(self.request.query_params.get("is_purchased"))
        if mobile_id:
            queryset = get_object_or_404(
                Order,
                user=self.request.user,
                mobile=mobile_id,
                is_purchased=is_purchased,
            )
        else:
            queryset = Order.objects.filter(
                user=self.request.user, is_purchased=is_purchased
            )

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        is_many = self.request.query_params.get("mobile")
        return Response(OrderSerializer(queryset, many=(not is_many)).data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
