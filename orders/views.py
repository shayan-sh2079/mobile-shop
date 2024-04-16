from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from mobiles.models import Mobile
from orders.models import Item, Order, PurchasedOrder
from orders.serializers import OrderSerializer, PurchasedSerializer

Transaction = apps.get_model("wallets", "Transaction")


class OrdersView(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        mobile_id = self.request.query_params.get("mobile")
        if mobile_id:
            queryset = get_object_or_404(
                Order,
                user=self.request.user,
                mobile=mobile_id,
            )
        else:
            queryset = Order.objects.filter(user=self.request.user)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        is_many = self.request.query_params.get("mobile")
        return Response(OrderSerializer(queryset, many=(not is_many)).data)

    def perform_create(self, serializer):
        if Order.objects.filter(
            mobile=serializer.validated_data["mobile"],
            user=self.request.user,
        ).exists():
            raise serializers.ValidationError({"message": "Order already exists"})
        serializer.save(user=self.request.user)


def check_order_quantity(order):
    if order.quantity > order.mobile.quantity:
        raise serializers.ValidationError(
            {"message": f"not enough quantity for mobile {order.mobile.name}"}
        )


class BuyView(CreateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = PurchasedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchasedOrder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        not_purchased_orders = []
        total_price = 0
        if "mobiles" not in serializer.validated_data:
            not_purchased_orders = Order.objects.filter(user=user)
            if not not_purchased_orders:
                raise serializers.ValidationError(
                    {"message": "there are no in cart mobiles"}
                )
            for order in not_purchased_orders:
                check_order_quantity(order)
                total_price += order.quantity * order.mobile.price

        else:
            for idx, mobile_id in enumerate(serializer.validated_data["mobiles"]):
                mobile = get_object_or_404(Mobile, id=mobile_id)
                try:
                    order = Order.objects.get(mobile=mobile, user=user)
                except ObjectDoesNotExist:
                    order = Order(
                        user=user,
                        mobile=mobile,
                        quantity=serializer.validated_data["quantities"][idx],
                    )
                order.quantity = serializer.validated_data["quantities"][idx]
                check_order_quantity(order)
                total_price += (
                    order.mobile.price * serializer.validated_data["quantities"][idx]
                )
                not_purchased_orders.append(order)

        user_transactions = Transaction.objects.filter(user=user)
        user_credit = 0
        for transaction in user_transactions:
            user_credit += transaction.amount
        if total_price > user_credit:
            raise serializers.ValidationError(
                {"message": "Not enough credit", "amount": total_price - user_credit}
            )

        purchased_order = PurchasedOrder.objects.create(user=user, amount=total_price)
        for order in not_purchased_orders:
            order.mobile.quantity -= order.quantity
            order.mobile.save()
            Item.objects.create(
                purchased_order=purchased_order,
                mobile=order.mobile,
                quantity=order.quantity,
            )
            if "mobiles" not in serializer.validated_data:
                order.delete()
        mobiles_names = ", ".join(item.mobile.name for item in not_purchased_orders)
        withdraw_transaction = Transaction.objects.create(
            user=user, amount=-total_price, comment=f"buying {mobiles_names}"
        )
        withdraw_transaction.save()
