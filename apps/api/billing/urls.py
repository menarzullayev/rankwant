from django.urls import path
from rest_framework.routers import DefaultRouter

from billing.views import BillingOverviewView, ClickWebhookView, OrderViewSet, PaymeWebhookView

router = DefaultRouter()
router.register("billing/orders", OrderViewSet, basename="billing-order")

urlpatterns = [
    path("billing/plans/", BillingOverviewView.as_view(), name="billing-plans"),
    # Provider callbacks: the URLs given to Payme and Click in their cabinets.
    path("billing/payme/", PaymeWebhookView.as_view(), name="billing-payme"),
    path("billing/click/", ClickWebhookView.as_view(), name="billing-click"),
    *router.urls,
]
