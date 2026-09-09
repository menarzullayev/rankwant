from django.urls import include, path
from rest_framework.routers import DefaultRouter

from qvant import staff_views, views

router = DefaultRouter()
router.register("qvant/transactions", views.TransactionViewSet, basename="qvant-tx")
router.register("qvant/shop", views.ShopViewSet, basename="qvant-shop")
router.register("qvant/inventory", views.InventoryViewSet, basename="qvant-inventory")
router.register("staff/quests", staff_views.StaffQuestViewSet, basename="staff-quest")
router.register("staff/shop-items", staff_views.StaffShopItemViewSet, basename="staff-shop-item")

urlpatterns = [
    path("qvant/wallet/", views.WalletView.as_view(), name="qvant-wallet"),
    path("qvant/quests/", views.QuestListView.as_view(), name="qvant-quests"),
    path("qvant/marathon/", views.MarathonView.as_view(), name="qvant-marathon"),
    path("", include(router.urls)),
]
