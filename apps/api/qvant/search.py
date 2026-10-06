"""Shop items in the site search (see `core.search`)."""

from core.search import Source, register
from qvant.models import ShopItem

register(
    Source(
        type="shop",
        kind="shop_item",
        queryset=lambda: ShopItem.objects.filter(is_active=True),
        primary="title_uz",
        secondary=("title_ru", "title_en", "code"),
        order=("price", "pk"),
        hit=lambda item: {
            "key": item.code,
            "title": item.title_uz,
            "title_ru": item.title_ru,
            "title_en": item.title_en,
            "meta": item.price,
        },
    )
)
