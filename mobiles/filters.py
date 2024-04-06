import django_filters

from .constants import BRANDS
from .models import Mobile


class MobileFilter(django_filters.FilterSet):
    brands = django_filters.MultipleChoiceFilter(field_name="brand", choices=BRANDS)

    o = django_filters.OrderingFilter(
        choices=[
            ("rate", "Highest rate"),
            ("newest", "Newest"),
            ("price", "Price low first"),
            ("-price", "Price high first"),
            ("sells", "Most sells"),
        ],
        fields=(
            ("-score", "rate"),
            ("price", "price"),
            ("-created_at", "newest"),
            ("-sells", "sells"),
        ),
    )

    class Meta:
        model = Mobile
        fields = {
            "price": ["lt", "gt"],
        }
