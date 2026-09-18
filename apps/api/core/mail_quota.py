"""Email kvota hisoblagichi — qaysi provayder qancha sarflagani.

NEGA KERAK: zanjir bepul planlar ustiga qurilgan (`core.mail_providers`),
ya'ni «kvota tugadi» kundalik hodisa. 2026-09-17 da o'lchandi: 1000 ta
ro'yxatdan o'tish uchun kunlik shift yetmaydi va qolgani keyingi kunga
o'tadi — lekin buni HECH KIM ko'rmaydi. Provayder jimgina `SendError`
beradi, zanjir keyingisiga o'tadi va faqat `EmailDelivery.attempts` da
iz qoladi (uni ham hech kim o'qimaydi).

Yagona haqiqat manbai — `EmailDelivery` jadvali: har yuborish bitta qator
bo'lib tushadi, `provider` va `status` bilan. Ya'ni hisoblagich YANGI
holat saqlamaydi, faqat mavjudini o'qiydi — bu ataylab: ikki joyda
haqiqat bo'lsa ular ajralib ketadi.

Kun chegarasi — **UTC kalendar kuni**. Sabab: Resend hujjati kunlik
kvotani «UTC calendar day (00:00–24:00 UTC), not a rolling window» deb
belgilaydi; Brevo/Mailjet ham kunlik reset qiladi. Rolling 24 soat
ishlatilsa, haqiqiy kvotadan ko'proq «sarflangan» ko'rinardi.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from django.utils import timezone

from core.models import EmailDelivery

#: Bepul reja kunlik shiftlari — rasmiy hujjatlardan (2026-09-17 tekshirildi).
#: `queue` — kunlik limitdan KEYIN navbatga olinadigan qo'shimcha hajm
#: (faqat Brevo'da bor: hujjat «up to 1,000 additional emails are held in a
#: retry queue» deydi). Navbat xatni yo'qotmaydi, lekin kechiktiradi.
DAILY_QUOTA: dict[str, int] = {
    "brevo": 300,
    "mailjet": 200,
    "resend": 100,
    "mailersend": 100,
    "console": 0,  # konsolga yozadi, kvota yo'q
}

#: Navbat hajmi — kunlik limitdan tashqari.
QUEUE_QUOTA: dict[str, int] = {
    "brevo": 1000,
}

#: Ogohlantirish chegarasi: shu ulushdan keyin «tugayapti» deb hisoblanadi.
WARN_AT = 0.8


@dataclass(frozen=True)
class ProviderUsage:
    """Bitta provayderning bugungi holati."""

    name: str
    sent: int
    quota: int
    queue: int = 0

    @property
    def configured(self) -> bool:
        """Kvotasi belgilangan provayder (noma'lum nom — kvota yo'q)."""
        return self.quota > 0

    @property
    def remaining(self) -> int:
        return max(0, self.quota - self.sent)

    @property
    def used_ratio(self) -> float:
        """0.0–1.0+. 1.0 dan oshsa — kvota tugagan, navbat ishlayapti."""
        if self.quota <= 0:
            return 0.0
        return self.sent / self.quota

    @property
    def exhausted(self) -> bool:
        return self.configured and self.sent >= self.quota

    @property
    def warning(self) -> bool:
        return self.configured and not self.exhausted and self.used_ratio >= WARN_AT

    @property
    def in_queue(self) -> bool:
        """Kvotadan oshgan, lekin navbatga sig'adigan qism."""
        if not self.exhausted or self.queue <= 0:
            return False
        return self.sent < self.quota + self.queue

    @property
    def lost(self) -> int:
        """Navbatdan ham oshib ketgan — bu xatlar YETKAZILMAYDI."""
        if not self.exhausted:
            return 0
        ceiling = self.quota + self.queue
        return max(0, self.sent - ceiling)


def day_start(when: datetime | None = None) -> datetime:
    """UTC kalendar kunining boshi.

    ⚠️ `when` qaysi mintaqada berilsa ham natija UTC chegarasi bo'ladi.
    Bu ataylab: `replace()` mintaqani SAQLAB qoladi, ya'ni
    `Asia/Tashkent` (UTC+5) dagi yarim tun UTC bo'yicha 19:00 ga to'g'ri
    keladi va `created_at__gte` filtri 5 soatga siljib ketardi
    (o'lchandi 2026-09-17: `?when=` mahalliy vaqt bilan 698 qaytardi,
    299 o'rniga). Shuning uchun avval UTC ga o'giriladi.
    """
    now = when or timezone.now()
    return timezone.localtime(now, UTC).replace(hour=0, minute=0, second=0, microsecond=0)


def day_end(when: datetime | None = None) -> datetime:
    """UTC kalendar kunining oxiri (keyingi kunning boshi).

    Filtr faqat pastki chegarani bilgani uchun kerak: `created_at__gte`
    bilan `when=` o'tgan kun bo'lsa ham bugungi qatorlar sanalardi va
    «kecha 300 ta ketdi» degan javob aslida «kecha + bugun» bo'lardi.
    """
    return day_start(when) + timedelta(days=1)


def usage(when: datetime | None = None) -> list[ProviderUsage]:
    """Shu UTC kunidagi sarfni provayder bo'yicha qaytaradi.

    Tartib `DAILY_QUOTA` bo'yicha — zanjir tartibi bilan bir xil, ya'ni
    «birinchi tugaydigan» provayder yuqorida turadi.

    Diapazon ikki tomonlama: `when` o'tgan kun bo'lsa ham bugungi
    qatorlar sanalmasligi kerak.
    """
    from django.db.models import Count

    counts = (
        EmailDelivery.objects.filter(
            status=EmailDelivery.Status.SENT,
            created_at__gte=day_start(when),
            created_at__lt=day_end(when),
        )
        .values("provider")
        .annotate(n=Count("id"))
    )
    by_name = {row["provider"]: row["n"] for row in counts}

    rows = [
        ProviderUsage(
            name=name,
            sent=by_name.get(name, 0),
            quota=quota,
            queue=QUEUE_QUOTA.get(name, 0),
        )
        for name, quota in DAILY_QUOTA.items()
    ]
    # Ro'yxatda yo'q provayder (masalan yangi qo'shilgan) ham ko'rinsin —
    # aks holda uning sarfi jimgina ko'rinmasdan qolardi.
    known = set(DAILY_QUOTA)
    rows.extend(
        ProviderUsage(name=name, sent=n, quota=0)
        for name, n in sorted(by_name.items())
        if name not in known and name
    )
    return rows


def total_remaining(when: datetime | None = None) -> int:
    """Shu kunda yana nechta xat yuborish mumkin (navbatdan tashqari)."""
    return sum(row.remaining for row in usage(when))


def total_remaining_with_queue(when: datetime | None = None) -> int:
    """Navbatni ham hisobga olgan imkoniyat.

    ⚠️ Bu «hozir qancha yuborish mumkin» EMAS. Navbat faqat kunlik
    shift tugagach ochiladi, ya'ni kun boshida bu raqam `total_remaining`
    bilan bir xil bo'ladi. Ma'nosi: «kunlik shift tugasa, yana qancha
    ochiladi». Paneldagi «navbat bilan birga N gacha» shu sababdan
    shartli — u va'da emas, yuqori chegara.
    """
    return sum(row.remaining + (row.queue if row.exhausted else 0) for row in usage(when))


def failures(when: datetime | None = None) -> int:
    """Shu kunda yuborilmagan xatlar soni — zanjir butunlay tugagan holat."""
    return EmailDelivery.objects.filter(
        status=EmailDelivery.Status.FAILED,
        created_at__gte=day_start(when),
        created_at__lt=day_end(when),
    ).count()


#: Bildirishnoma sarlavhasi. `tasks.py` da qattiq yozilgan edi, matn esa
#: `summary()` dan kelardi — ya'ni bitta xabar ikki joyda. Endi ikkisi ham
#: shu yerda, chunki `summary()` ham, sarlavha ham AYNAN shu modulning
#: tushunchasi (kvota holati), `core.tasks` esa faqat yetkazuvchi.
#:
#: ⚠️ Tarjima qilinmaydi — `Notification` modeli shuni talab qiladi
#: ("matn hodisa yuz berganda yoziladi"): xabar yozilgan paytdagi holatni
#: qotib qoladi, foydalanuvchi keyin tilini almashtirsa ham o'zgarmaydi.
#: Boshqa 5 ta ishlab chiqaruvchi (duels, ratings, hacks, qvant,
#: hackathons) ham xuddi shunday qiladi.
ALERT_TITLE = "Email kvotasi tugayapti"


def warning_rows(when: datetime | None = None) -> list[ProviderUsage]:
    """E'tibor talab qiladigan qatorlar: tugagan, tugayotgan yoki yo'qolgan.

    Nega alohida funksiya: ogohlantirish shartini ikki joyda yozish
    (vazifa va panel) ularning vaqt o'tib ajralib ketishiga olib keladi.
    Shart bir joyda — shu yerda.
    """
    return [
        row for row in usage(when) if row.configured and (row.exhausted or row.warning or row.lost)
    ]


def summary(when: datetime | None = None) -> str:
    """Ogohlantirish matni — odam o'qiy oladigan bir qator.

    Ataylab qisqa: bildirishnoma qo'ng'irog'i faqat sarlavhani ko'rsatadi,
    shuning uchun eng muhim raqamlar shu matnga sig'ishi kerak.
    """
    rows = warning_rows(when)
    if not rows:
        return ""
    parts = []
    for row in rows:
        if row.lost:
            parts.append(f"{row.name}: {row.lost} xat YETKAZILMAYDI")
        elif row.exhausted:
            parts.append(f"{row.name}: kunlik shift tugadi, navbatda")
        elif row.warning:
            parts.append(f"{row.name}: {round(row.used_ratio * 100)}% sarflandi")
    left = total_remaining(when)
    parts.append(f"bugun yana {left} xat")
    return "; ".join(parts)
