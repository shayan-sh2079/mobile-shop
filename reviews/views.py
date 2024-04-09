from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from reviews.models import Review
from reviews.serializers import ReviewSerializer


class ReviewsView(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(phone_id=self.request.query_params.get("phone_id"))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
