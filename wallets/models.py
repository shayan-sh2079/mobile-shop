from django.db import models


class Transaction(models.Model):
    user = models.ForeignKey(
        "users.User", related_name="transactions", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    comment = models.TextField()

    class Meta:
        ordering = ["-created_at"]
