"""Test helper: change plan limits the way the admin would."""

from __future__ import annotations


def set_free_quota(**values: int) -> None:
    """Change the free plan's limits for one test (the admin's `PlanQuota` row)."""
    from core.models import PlanQuota
    from core.quotas import DEFAULTS

    PlanQuota.objects.update_or_create(plan="free", defaults={**DEFAULTS["free"], **values})
