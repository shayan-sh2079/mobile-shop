from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import BRANDS


class Mobile(models.Model):
    brand = models.CharField(max_length=20, choices=BRANDS)
    name = models.CharField(max_length=50, unique=True)
    quantity = models.PositiveIntegerField()
    score = models.FloatField(
        validators=[
            MinValueValidator(
                0.0, message="Value must be greater than or equal to 0.0"
            ),
            MaxValueValidator(5.0, message="Value must be less than or equal to 5.0"),
        ]
    )
    price = models.PositiveBigIntegerField()
