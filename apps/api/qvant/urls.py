from django.urls import include, path
from rest_framework.routers import DefaultRouter

from qvant import views

router = DefaultRouter()
router.register("qvant/transactions", views.TransactionViewSet, basename="qvant-tx")
router.register("qvant/shop", views.ShopViewSet, basename="qvant-shop")
router.register("qvant/inventory", views.InventoryViewSet, basename="qvant-inventory")

urlpatterns = [
    path("qvant/wallet/", views.WalletView.as_view(), name="qvant-wallet"),
    path("qvant/quests/", views.QuestListView.as_view(), name="qvant-quests"),
    path("", include(router.urls)),
]
