from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from .filters import MobileFilter
from .models import Mobile
from .permissions import IsOwnerOrReadOnly
from .serializers import MobileSerializer


class MobileViewSet(viewsets.ModelViewSet):
    queryset = Mobile.objects.all()
    serializer_class = MobileSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        permissions.IsAdminUser | IsOwnerOrReadOnly,
    ]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MobileFilter

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        ordered_by_price = Mobile.objects.all().order_by("price")

        lowest_price = ordered_by_price.first().price
        highest_price = ordered_by_price.last().price

        return Response(
            {
                "result": response.data,
                "lowest_price": lowest_price,
                "highest_price": highest_price,
            }
        )

    def filter_queryset(self, queryset):
        if self.action == "retrieve":
            return queryset
        return super().filter_queryset(queryset)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
