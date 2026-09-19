from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreConfig(AppConfig):
    name = "core"

    def ready(self) -> None:
        # Guruh permission'lari migrate TUGAGACH paydo bo'ladi
        # (`auth_permission` post_migrate'da yaratiladi), shuning uchun
        # sinxronizatsiya shu signal orqali — idempotent (core/groups.py).
        # Import SIGNAL ICHIDA: `auth.models` ni app yuklanish paytidagina
        # tegish kerak emas (AppRegistryNotReady — o'lchandi).
        def sync_staff_groups_on_migrate(**kwargs: object) -> None:
            from core.groups import sync_staff_groups

            sync_staff_groups()

        # `sender` FILTRSIZ: post_migrate har app uchun alohida fires
        # bo'ladi va `core` boshida turadi — oxirgi appning signalida
        # barcha permission'lar allaqachon mavjud bo'ladi (o'lchandi).
        post_migrate.connect(sync_staff_groups_on_migrate)
