from __future__ import annotations

from celery import shared_task

from profiles import external
from profiles.models import ExternalProfile


@shared_task(name="profiles.refresh_external")
def refresh_external(profile_id: int) -> bool:
    """Tashqi reytingni yangilaydi — so'rov ichida emas, navbatda."""
    profile = ExternalProfile.objects.filter(pk=profile_id).first()
    return external.refresh(profile) if profile is not None else False
