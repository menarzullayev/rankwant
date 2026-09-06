from __future__ import annotations

from celery import shared_task

from ratings.services import recalc_skills_for_problem


@shared_task(name="ratings.recalc_skills_for_problem")
def recalc_skills_for_problem_task(problem_id: int) -> int:
    """Masala qiyinligi o'zgarganda — ADR-0007.

    Partiyada ishlaydi; `UserSolvedProblem(problem_id)` indeksi shart.
    """
    return recalc_skills_for_problem(problem_id)


@shared_task(name="ratings.refresh_activity")
def refresh_activity(batch: int = 500) -> int:
    """Activity reytingini yangilaydi — PRD P1-7.

    Activity 30 kunlik SILJUVCHI oynada hisoblanadi: foydalanuvchi
    hech narsa qilmasa ham qiymat pasayishi kerak. Hodisaga bog'liq
    qayta hisoblash buni qila olmaydi — faol bo'lmagan odamda hodisa
    ham yo'q. Shuning uchun davriy o'tish.

    Faqat nolga teng bo'lmagan Activity li foydalanuvchilar ko'riladi:
    noldan nolga o'tish hech narsani o'zgartirmaydi.
    """
    from core.models import User
    from qvant.services import recalc_activity

    changed = 0
    users = User.objects.filter(is_active=True).exclude(rating_activity=0)[:batch]
    for user in users:
        before = user.rating_activity
        if recalc_activity(user) != before:
            changed += 1
    return changed
