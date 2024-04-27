from rest_framework import serializers

from wallets.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = Transaction
        exclude = ("user",)
        extra_kwargs = {
            "created_at": {"read_only": True},
            "comment": {"read_only": True},
        }
