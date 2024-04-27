from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from orders.models import Item, Order, PurchasedOrder
from orders.serializers import (
    OrderDetailSerializer,
    OrderSerializer,
    PurchasedSerializer,
)

Transaction = apps.get_model("wallets", "Transaction")
Mobile = apps.get_model("mobiles", "Mobile")


class OrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return get_object_or_404(Order, user=self.request.user)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        kwargs.setdefault(
            "context",
            {
                "request": self.request,
            },
        )
        return Response(OrderSerializer(queryset, many=False, *args, **kwargs).data)

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


class OrderDetailView(APIView):
    def patch(self, request, pk, *args, **kwargs):
        serializer = OrderDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = get_object_or_404(Order, user=request.user)
        item = get_object_or_404(order.items.all(), mobile=pk)
        item.quantity = serializer.validated_data["count"]
        item.save()
        kwargs.setdefault(
            "context",
            {
                "request": self.request,
            },
        )
        return Response(
            OrderSerializer(order, *args, **kwargs).data, status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        order = get_object_or_404(Order, user=request.user)
        item = get_object_or_404(order.items.all(), mobile=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BuyView(CreateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = PurchasedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PurchasedOrder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        total_price = 0
        try:
            not_purchased_order = Order.objects.get(user=user)
            items = not_purchased_order.items.all()
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {"message": "there are no in cart mobiles"}
            )
        for item in items:
            if item.quantity > item.mobile.quantity:
                raise serializers.ValidationError(
                    {"message": f"not enough quantity for mobile {item.mobile.name}"}
                )
            total_price += item.quantity * item.mobile.price

        user_transactions = Transaction.objects.filter(user=user)
        user_credit = 0
        for transaction in user_transactions:
            user_credit += transaction.amount
        if total_price > user_credit:
            raise serializers.ValidationError(
                {"message": "Not enough credit", "amount": total_price - user_credit}
            )

        mobiles_names = ", ".join(item.mobile.name for item in items)
        withdraw_transaction = Transaction.objects.create(
            user=user, amount=-total_price, comment=f"buying {mobiles_names}"
        )

        purchased_order = PurchasedOrder.objects.create(
            user=user, transaction=withdraw_transaction
        )
        for item in items:
            item.mobile.quantity -= item.quantity
            item.mobile.save()

        items.update(order=None, purchased_order=purchased_order)
        not_purchased_order.delete()
