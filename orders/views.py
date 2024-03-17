from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, serializers
from rest_framework.generics import CreateAPIView, GenericAPIView, get_object_or_404
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.response import Response

from mobiles.models import Mobile
from orders.models import Order
from orders.serializers import BuySerializer, OrderSerializer


class OrdersView(GenericAPIView, CreateModelMixin, UpdateModelMixin):
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

    def get_object(self):
        order = get_object_or_404(Order, pk=self.request.data["id"])
        self.check_object_permissions(self.request, order)
        return order

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        is_many = self.request.query_params.get("mobile")
        return Response(OrderSerializer(queryset, many=(not is_many)).data)

    def perform_create(self, serializer):
        if Order.objects.filter(
            mobile=serializer.validated_data["mobile"],
            user=self.request.user,
            is_purchased=False,
        ).exists():
            raise serializers.ValidationError({"message": "Order already exists"})
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


def check_order_quantity(order):
    if order.quantity > order.mobile.quantity:
        raise serializers.ValidationError(
            {"message": f"not enough quantity for mobile {order.mobile.name}"}
        )


class BuyView(CreateAPIView):
    serializer_class = BuySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        not_purchased_orders = []
        total_price = 0
        if "mobiles" not in serializer.validated_data:
            not_purchased_orders = self.queryset.filter(user=user, is_purchased=False)
            if not not_purchased_orders:
                raise serializers.ValidationError(
                    {"message": "there are no in cart mobiles"}
                )
            serializer.validated_data["mobiles"] = not_purchased_orders
            serializer.validated_data["quantities"] = []
            for order in not_purchased_orders:
                serializer.validated_data["quantities"].append(order.quantity)
                check_order_quantity(order)
                total_price += order.quantity * order.mobile.price

        else:
            for idx, mobile_id in enumerate(serializer.validated_data["mobiles"]):
                mobile = get_object_or_404(Mobile, id=mobile_id)
                try:
                    order = self.queryset.get(
                        mobile=mobile, user=user, is_purchased=False
                    )
                except ObjectDoesNotExist:
                    order = Order(
                        user=user,
                        mobile=mobile,
                        quantity=serializer.validated_data["quantities"][idx],
                    )
                    print(order)
                order.quantity = serializer.validated_data["quantities"][idx]
                check_order_quantity(order)
                total_price += (
                    order.mobile.price * serializer.validated_data["quantities"][idx]
                )
                not_purchased_orders.append(order)
        if total_price > user.credit:
            raise serializers.ValidationError(
                {"message": "Not enough credit", "amount": total_price - user.credit}
            )
        for order in not_purchased_orders:
            order.is_purchased = True
            order.mobile.quantity -= order.quantity
            user.credit -= total_price
            user.save()
            order.mobile.save()
            order.save()
