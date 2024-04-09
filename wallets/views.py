from rest_framework import mixins, permissions, serializers
from rest_framework.viewsets import GenericViewSet

from wallets.models import Transaction
from wallets.permissions import IsOwner
from wallets.serializers import TransactionSerializer


class TransactionsViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        if (
            "comment" not in serializer.validated_data
            or serializer.validated_data["comment"] is None
        ):
            if serializer.validated_data["amount"] > 0:
                serializer.validated_data["comment"] = "Deposit into the wallet"
            elif serializer.validated_data["amount"] < 0:
                serializer.validated_data["comment"] = "Withdraw from the wallet"
            else:
                raise serializers.ValidationError(
                    {"message": "You can't give 0 as the amount"}
                )
        serializer.save(user=self.request.user)
