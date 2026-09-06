from django.contrib import admin

from qvant.models import (
    QvantQuest,
    QvantTransaction,
    QvantWallet,
    ShopItem,
    UserInventory,
    UserQuestCompletion,
)


@admin.register(QvantWallet)
class QvantWalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "updated_at")
    search_fields = ("user__username",)
    # Balans ledgerdan chiqadi — admin'dan qo'lda o'zgartirilmaydi (ADR-0002)
    readonly_fields = ("balance", "updated_at")


@admin.register(QvantTransaction)
class QvantTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "reason", "ref_type", "ref_id", "balance_after", "created_at")
    list_filter = ("reason",)
    search_fields = ("user__username", "ref_id")
    # Ledger o'zgarmas: yozuvlar tuzatilmaydi, faqat qarama-qarshi yozuv
    readonly_fields = tuple(f.name for f in QvantTransaction._meta.fields)

    def has_add_permission(self, request) -> bool:  # type: ignore[no-untyped-def]
        return False

    def has_delete_permission(self, request, obj=None) -> bool:  # type: ignore[no-untyped-def]
        return False


@admin.register(QvantQuest)
class QvantQuestAdmin(admin.ModelAdmin):
    list_display = ("code", "type", "reward", "is_active")
    list_filter = ("type", "is_active")


@admin.register(UserQuestCompletion)
class UserQuestCompletionAdmin(admin.ModelAdmin):
    list_display = ("user", "quest", "period_key", "awarded", "completed_at")
    list_filter = ("quest",)
    search_fields = ("user__username", "period_key")


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ("code", "category", "price", "is_consumable", "is_active")
    list_filter = ("category", "is_active")


@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ("user", "item", "purchased_at", "is_equipped")
    search_fields = ("user__username", "item__code")
