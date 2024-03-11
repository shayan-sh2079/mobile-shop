from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("user", "mobile", "quantity")
        extra_kwargs = {"user": {"read_only": True}}
