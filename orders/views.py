from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from orders.models import Item, Order, PurchasedOrder
from orders.serializers import OrderSerializer, PurchasedSerializer

Transaction = apps.get_model("wallets", "Transaction")
Mobile = apps.get_model("mobiles", "Mobile")


class OrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_object_or_404(Order, user=self.request.user)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(OrderSerializer(queryset, many=False).data)

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobiles = []
        for mobile in serializer.validated_data["mobiles"]:
            mobiles.append(get_object_or_404(Mobile, pk=mobile))

        try:
            order = Order.objects.get(user=request.user)
            order.items.all().delete()
        except ObjectDoesNotExist:
            order = Order.objects.create(user=request.user)

        for idx, mobile in enumerate(mobiles):
            Item.objects.create(
                mobile=mobile,
                order=order,
                quantity=serializer.validated_data["quantities"][idx],
            )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = get_object_or_404(Order, user=request.user)
        items = []
        for mobile in serializer.validated_data["mobiles"]:
            items.append(get_object_or_404(order.items.all(), mobile=mobile))
        for idx, item in enumerate(items):
            item.quantity = serializer.validated_data["quantities"][idx]
            item.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


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
        total_price = 0
        try:
            not_purchased_orders = Order.objects.get(user=user)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {"message": "there are no in cart mobiles"}
            )
        for order in not_purchased_orders:
            check_order_quantity(order)
            total_price += order.quantity * order.mobile.price

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
            order.delete()
        mobiles_names = ", ".join(item.mobile.name for item in not_purchased_orders)
        withdraw_transaction = Transaction.objects.create(
            user=user, amount=-total_price, comment=f"buying {mobiles_names}"
        )
        withdraw_transaction.save()
