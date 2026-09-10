from __future__ import annotations

import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from blog.models import Post

log = logging.getLogger(__name__)


@shared_task(name="blog.announce_published")
def announce_published() -> int:
    """Nashr qilingan e'lonlar bo'yicha bildirishnoma yuboradi.

    Task sifatida: minglab foydalanuvchiga yozish so'rov ichida
    bajarilmasligi kerak.
    """
    from core.models import User
    from notifications.models import Notification
    from notifications.services import notify_many

    total = 0
    pending = Post.objects.filter(is_published=True, notify_users=True, notified_at__isnull=True)
    for post_id in list(pending.values_list("pk", flat=True)):
        # Qulf ostida qayta tekshiriladi: `notified_at` ni o'qish va yozish
        # orasi ochiq qolsa, ustma-ust tushgan ikkinchi chaqiruv HAMMA faol
        # foydalanuvchiga o'sha e'lonni ikkinchi marta yuboradi. Beat buni
        # har 300 soniyada yuboradi, `notify_many` esa butun bazaga yozadi.
        with transaction.atomic():
            post = (
                Post.objects.select_for_update()
                .filter(pk=post_id, notified_at__isnull=True)
                .first()
            )
            if post is None:
                continue
            sent = notify_many(
                User.objects.filter(is_active=True),
                Notification.Kind.SYSTEM,
                post.title,
                body=post.summary,
                ref_type="post",
                ref_id=post.slug,
            )
            post.notified_at = timezone.now()
            post.save(update_fields=["notified_at"])
        total += sent
        log.info("e'lon %s — %s foydalanuvchiga yuborildi", post.slug, sent)
    return total
