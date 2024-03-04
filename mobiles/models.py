from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import BRANDS


def mobile_img_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "mobiles/images/mobiles/mobile_{0}/{1}".format(instance.mobile.id, filename)


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


class MobileImage(models.Model):
    img = models.ImageField(upload_to=mobile_img_directory_path)
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="images")
