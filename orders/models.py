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
    created_at = models.DateTimeField(auto_now=True)
    quantity = models.PositiveIntegerField()
