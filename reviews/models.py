from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from mobiles.models import Mobile


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="reviews", on_delete=models.CASCADE
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone = models.ForeignKey(Mobile, related_name="reviews", on_delete=models.CASCADE)
    rating = models.FloatField(
        validators=[
            MinValueValidator(
                0.0, message="Value must be greater than or equal to 0.0"
            ),
            MaxValueValidator(5.0, message="Value must be less than or equal to 5.0"),
        ]
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "phone"],
                name="users can only have one review on each phone",
            )
        ]


class Reply(models.Model):
    review = models.ForeignKey(Review, related_name="replies", on_delete=models.CASCADE)
    reply = models.ForeignKey("self", related_name="replies", on_delete=models.CASCADE)
    isLiked = models.BooleanField(default=False)
    isDisliked = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="replies", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
