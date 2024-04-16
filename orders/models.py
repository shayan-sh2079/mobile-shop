from django.conf import settings
from django.db import models


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mobile = models.ForeignKey("mobiles.Mobile", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()


class PurchasedOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey("wallets.Transaction", on_delete=models.PROTECT)


class Item(models.Model):
    mobile = models.ForeignKey("mobiles.Mobile", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    purchased_order = models.ForeignKey(
        PurchasedOrder, on_delete=models.CASCADE, related_name="items"
    )
