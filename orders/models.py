from django.conf import settings
from django.db import models


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user"
    )
    mobile = models.ForeignKey(
        "mobiles.Mobile", on_delete=models.PROTECT, related_name="mobile"
    )
    is_purchased = models.BooleanField(default=False)
    is_in_cart = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("user", "mobile")
