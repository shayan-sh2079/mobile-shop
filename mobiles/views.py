from rest_framework import viewsets

from .models import Mobile
from .serializers import MobileSerializer


class MobileViewSet(viewsets.ModelViewSet):
    queryset = Mobile.objects.all()
    serializer_class = MobileSerializer
