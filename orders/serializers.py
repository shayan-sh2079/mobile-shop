from rest_framework import serializers

from mobiles.serializers import MobileSerializer

from .models import Item, Order, PurchasedOrder


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "user", "mobile", "quantity")
        extra_kwargs = {"user": {"read_only": True}}


class PurchasedItemSerializer(serializers.ModelSerializer):
    mobile = MobileSerializer(read_only=True)

    class Meta:
        model = Item
        fields = "__all__"


class PurchasedSerializer(serializers.ModelSerializer):
    items = PurchasedItemSerializer(many=True, read_only=True)
    mobiles = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        required=False,
        write_only=True,
    )
    quantities = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        required=False,
        write_only=True,
    )
    user = serializers.IntegerField(source="user.id", read_only=True)
    transaction_amount = serializers.IntegerField(
        source="transaction.amount", read_only=True
    )

    def validate(self, attrs):
        if (attrs.get("mobiles") and not attrs.get("quantities")) or (
            not attrs.get("mobiles") and attrs.get("quantities")
        ):
            raise serializers.ValidationError(
                {
                    "message": "Both quantities and mobiles fields should be provided or none of them"
                }
            )

        if (
            attrs.get("mobiles")
            and attrs.get("quantities")
            and len(attrs.get("mobiles")) != len(attrs.get("quantities"))
        ):
            raise serializers.ValidationError(
                {"message": "quantities and mobiles should have equal length"}
            )
        return attrs

    class Meta:
        model = PurchasedOrder
        fields = (
            "mobiles",
            "quantities",
            "user",
            "items",
            "created_at",
            "transaction_amount",
        )
        extra_kwargs = {"created_at": {"read_only": True}}
