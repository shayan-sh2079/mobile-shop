from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "user", "mobile", "quantity")
        extra_kwargs = {"user": {"read_only": True}}


class BuySerializer(serializers.Serializer):
    mobiles = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False, required=False
    )
    quantities = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False, required=False
    )
    user = serializers.IntegerField(source="user.id", read_only=True)

    def validate(self, attrs):
        if (attrs.get("mobiles") and not attrs.get("quantities")) or (
            attrs.get("mobiles") and not attrs.get("quantities")
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
        fields = "__all__"
