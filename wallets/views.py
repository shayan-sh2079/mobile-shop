from django.db.models import Sum
from rest_framework import mixins, permissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from wallets.models import Transaction
from wallets.permissions import IsOwner
from wallets.serializers import TransactionSerializer


class TransactionsViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet
):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        total_credit = self.get_queryset().aggregate(Sum("amount")).get("amount__sum")

        return Response(
            {
                "history": response.data,
                "credit": total_credit,
            }
        )

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if (
            "comment" not in serializer.validated_data
            or serializer.validated_data["comment"] is None
        ):
            serializer.validated_data["comment"] = "Deposit into the wallet"
        serializer.save(user=self.request.user)
