from rest_framework import serializers

from mobiles.serializers import MobileSerializer

from .models import Item, Order, PurchasedOrder


class ItemSerializer(serializers.ModelSerializer):
    mobile = MobileSerializer(read_only=True)

    class Meta:
        model = Item
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)
    mobiles = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        write_only=True,
    )
    quantities = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        write_only=True,
    )

    def validate(self, attrs):
        if len(attrs.get("mobiles")) != len(attrs.get("quantities")):
            raise serializers.ValidationError(
                {"message": "quantities and mobiles should have equal length"}
            )

        return attrs

    class Meta:
        model = Order
        fields = ("id", "user", "items", "mobiles", "quantities")
        extra_kwargs = {"user": {"read_only": True}}


class PurchasedSerializer(serializers.ModelSerializer):
    purchased_items = ItemSerializer(many=True, read_only=True)
    user = serializers.IntegerField(source="user.id", read_only=True)
    transaction_amount = serializers.IntegerField(
        source="transaction.amount", read_only=True
    )

    class Meta:
        model = PurchasedOrder
        fields = (
            "user",
            "purchased_items",
            "created_at",
            "transaction_amount",
        )
        extra_kwargs = {"created_at": {"read_only": True}}
