from rest_framework import permissions, viewsets

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

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
