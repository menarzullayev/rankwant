"""Qvant hodisalari va Activity reytingi.

Activity formulasi `ratings.formulas` da (sof funksiya); bu yerda faqat
unga kerakli hisoblar to'planadi.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

from core.models import User
from qvant import ledger, quests, streak
from qvant.models import QvantTransaction as Tx
from qvant.models import ShopItem, UserInventory, UserQuestCompletion
from ratings import formulas
from ratings.models import RatingHistory

log = logging.getLogger(__name__)


class PurchaseError(Exception):
    """Xarid bajarilmadi."""


def _distinct_ac_count(user: User, day: date) -> int:
    from judging.models import Attempt
    from judging.verdicts import Verdict

    return (
        Attempt.objects.filter(user=user, verdict=Verdict.AC, created_at__date=day)
        .values("problem_id")
        .distinct()
        .count()
    )


@transaction.atomic
def on_first_accepted(user: User) -> dict[str, object]:
    """Birinchi AC dan keyin: streak, questlar, Activity reyting.

    `judging.services.on_attempt_judged` dan chaqiriladi. Faqat BIRINCHI
    AC da — ADR-0002 anti-farm: qayta yechish 0 Qvant beradi.
    """
    current, streak_quests = streak.touch(user)
    daily = quests.on_accepted(user, ac_count_today=_distinct_ac_count(user, timezone.localdate()))

    from qvant.marathon import check_completion

    if check_completion(user):
        daily.append("weekly_marathon")

    recalc_activity(user)
    if streak_quests:
        from notifications.models import Notification
        from notifications.services import notify

        notify(
            user,
            Notification.Kind.STREAK_MILESTONE,
            f"{current} kunlik streak!",
            body="Streak yutug'i uchun Qvant qo'shildi.",
            ref_type="streak",
            ref_id=str(current),
        )

    return {"streak": current, "quests": [*daily, *streak_quests]}


@transaction.atomic
def on_contest_finished(user: User, contest_slug: str) -> int:
    granted = quests.on_contest_finished(user, contest_slug)
    if granted:
        recalc_activity(user)
    return granted


@transaction.atomic
def revoke_for_attempt(user: User, day: date) -> int:
    """Rejudge AC ni bekor qilganda — ADR-0002 qaytarish qoidasi.

    AC dan keladigan Qvant urinishga emas, kunlik questga bog'langan,
    shuning uchun havola bo'yicha qaytarish MUMKIN emas — ilgari shu
    yerda `refund_ref(user, "attempt", …)` turardi va hech qachon
    mos yozuv topmasdi: rejudge skills bilan statistikani qaytarib,
    pulni foydalanuvchida qoldirardi. Endi kun sharti qayta o'lchanadi.

    Streak ATAYLAB tegilmaydi: rejudge — bizning testimiz yoki
    checkerimiz xatosi, foydalanuvchining zanjirini orqaga qaytarib
    buzish adolatsiz.
    """
    revoked, taken = quests.revoke_day_quests(user, day, ac_count=_distinct_ac_count(user, day))
    if revoked:
        recalc_activity(user)
    return taken


# ── Activity reyting — ADR-0006, Phase 1 ─────────────────────────────
def activity_inputs(user: User) -> tuple[int, int, int]:
    """(faol_kun, bajarilgan_quest, streak_kun) — 30 kunlik oyna."""
    from judging.models import Attempt

    since = timezone.now() - timedelta(days=formulas.ACTIVITY_WINDOW_DAYS)

    active_days = (
        Attempt.objects.filter(user=user, created_at__gte=since).dates("created_at", "day").count()
    )
    quests_done = UserQuestCompletion.objects.filter(user=user, completed_at__gte=since).count()
    return active_days, quests_done, user.streak_count


@transaction.atomic
def recalc_activity(user: User) -> int:
    """Activity reytingini qayta hisoblaydi va o'zgarishni yozadi."""
    active_days, quests_done, streak_days = activity_inputs(user)
    value = formulas.activity_rating(active_days, quests_done, streak_days)

    before = user.rating_activity
    if value == before:
        return value

    user.rating_activity = value
    user.save(update_fields=["rating_activity"])
    RatingHistory.objects.create(
        user=user,
        rating_type=RatingHistory.Type.ACTIVITY,
        value_before=before,
        value_after=value,
        delta=value - before,
        reason=RatingHistory.Reason.RECALCULATION,
        ref_type="activity",
        ref_id="",
    )
    return value


# ── Do'kon ───────────────────────────────────────────────────────────
@transaction.atomic
def purchase(user: User, item_code: str) -> UserInventory:
    """Do'kondan xarid. Balans yetmasa yoki takrorlansa — xato."""
    try:
        item = ShopItem.objects.get(code=item_code, is_active=True)
    except ShopItem.DoesNotExist:
        raise PurchaseError("Narsa topilmadi") from None

    # `UserInventory` da uniq cheklov YO'Q (streak freeze takroriy
    # sotib olinadi), shuning uchun takrorlanishni faqat shu qulf
    # ushlab turadi. O'lchandi: qulfsiz 6 ta parallel so'rov ramkani
    # 4 marta sotib, 100 o'rniga 400 Qvant yechib yuborardi.
    ledger.lock_wallet(user)

    if not item.is_consumable and UserInventory.objects.filter(user=user, item=item).exists():
        raise PurchaseError("Bu narsa sizda allaqachon bor")

    try:
        ledger.debit(user, item.price, Tx.Reason.PURCHASE, ref_type="shop_item", ref_id=item.code)
    except ledger.InsufficientBalance as exc:
        raise PurchaseError(f"Balans yetarli emas ({exc})") from exc

    entry = UserInventory.objects.create(user=user, item=item)

    # Streak freeze — sotib olinishi bilan darhol yoqiladi
    if item.category == ShopItem.Category.STREAK_FREEZE:
        streak.apply_freeze(user, days=1)

    # DIQQAT: Activity reyting QAYTA HISOBLANMAYDI. Xarid balansni
    # kamaytiradi, lekin formulada balans yo'q (ADR-0002) — aks holda
    # foydalanuvchi Qvant sarflashdan qo'rqardi.
    return entry
