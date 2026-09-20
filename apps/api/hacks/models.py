"""Hack entitylari — ADR-0020 (dvigatel) va ADR-0021 (etalon yechim).

Hack natijasi va urinish verdicti — IKKI XIL narsa (ADR-0020, 4-qaror):
hack o'z holatini oladi (`SUCCESSFUL`, `UNSUCCESSFUL`, …), himoyachining
urinishi esa `Verdict.HACKED` ni. Shuning uchun bu yerdagi `Status`
`judging.verdicts.Verdict` bilan aralashtirilmaydi.
"""

from __future__ import annotations

from typing import ClassVar

from django.db import models

from core.bases import CreatedModel, TimeStampedModel
from hacks import policies


class Hack(TimeStampedModel):
    """Bitta hack urinishi: kim, kimning yechimini, qaysi test bilan."""

    class Status(models.TextChoices):
        #: Judge hali javob bermagan
        TESTING = "TESTING", "Tekshirilmoqda"
        #: Himoyachining yechimi hack testida yiqildi
        SUCCESSFUL = "SUCCESSFUL", "Muvaffaqiyatli"
        #: Yechim testdan o'tdi — hack ishlamadi
        UNSUCCESSFUL = "UNSUCCESSFUL", "Muvaffaqiyatsiz"
        #: Kiritma validatordan o'tmadi. JAZOLANMAYDI (ADR-0020, 3-qaror):
        #: noto'g'ri test arzon bo'lishi kerak.
        INVALID_INPUT = "INVALID_INPUT", "Kiritma yaroqsiz"
        #: Generator dasturi yiqildi yoki chegaradan oshdi
        GENERATOR_CRASHED = "GENERATOR_CRASHED", "Generator yiqildi"
        #: Hisobga olinmadi: etalon yechim yoki judge ishlamadi — hacker
        #: aybi emas, shuning uchun ball ham, jarima ham yo'q.
        IGNORED = "IGNORED", "Hisobga olinmadi"
        #: Tezlik chegarasi urildi. `RATE_LIMITED` urinish pretsedenti
        #: (ADR-0020 § Cheklov): jim 429 emas, ko'rinadigan yozuv.
        RATE_LIMITED = "RATE_LIMITED", "Tezlik chegarasi"

    class Stage(models.TextChoices):
        """Judge bilan suhbat qaysi bosqichda."""

        #: Generator dasturi ishga tushmoqda (kiritma hosil qilinmoqda)
        GENERATE = "generate", "Generator"
        #: Etalon yechim javobni hisoblamoqda (validator shu bosqichda)
        REFERENCE = "reference", "Etalon yechim"
        #: Himoyachining kodi hack testida ishlamoqda
        DEFEND = "defend", "Himoyachi"
        DONE = "done", "Tugadi"

    hacker = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="hacks_made")
    #: Nishon — `AC` bo'lgan urinish. Faqat qabul qilingan yechimni
    #: sindirish mumkin, shuning uchun bog'lanish urinishga.
    defender_attempt = models.ForeignKey(
        "judging.Attempt", on_delete=models.CASCADE, related_name="hacks"
    )
    #: Denormalizatsiya: masala bo'yicha ro'yxat va indeks uchun —
    #: urinish orqali join qilish har sahifada qimmatga tushardi.
    problem = models.ForeignKey("problems.Problem", on_delete=models.CASCADE, related_name="hacks")
    contest = models.ForeignKey(
        "contests.Contest", null=True, blank=True, on_delete=models.SET_NULL, related_name="hacks"
    )
    policy = models.CharField(max_length=16, choices=policies.CHOICES)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.TESTING, db_index=True
    )
    stage = models.CharField(max_length=12, choices=Stage.choices, default=Stage.REFERENCE)

    #: Test ma'lumoti DB da emas, S3/R2 da (05-domain-model): kiritma ham,
    #: etalon yechim bergan javob ham obyekt xotirasida yotadi.
    input_ref = models.CharField(max_length=500, blank=True)
    output_ref = models.CharField(max_length=500, blank=True)
    input_size = models.PositiveIntegerField(default=0)

    #: Generator bilan yuborilgan hack: kiritmani dastur hosil qiladi.
    #: Dastur ISHONCHSIZ — sandbox ichida ishlaydi.
    generator_language = models.ForeignKey(
        "problems.Language", null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    generator_source = models.TextField(blank=True)

    #: Himoyachining kodi hack testida qanday verdikt oldi. `HACKED` EMAS:
    #: bu judge bergan haqiqiy natija (`WA`, `TLE`, …) va hackerga aynan
    #: shu ko'rsatiladi.
    defender_verdict = models.CharField(max_length=24, blank=True)
    #: Sabab matni: validator xabari, generator xatosi yoki nega hisobga
    #: olinmagani. Foydalanuvchiga ko'rsatiladi.
    detail = models.TextField(blank=True)
    #: Siyosat bergan ball (`contest_room`: +100 / −50). Jadval shu
    #: ustundan yig'adi — qayta hisoblashda siyosatga qayta murojaat
    #: qilinmaydi, chunki siyosat keyinchalik o'zgarishi mumkin.
    points = models.IntegerField(default=0)
    #: Muvaffaqiyatli hack asosiy to'plamga qo'shilgan bo'lsa — o'sha test.
    #: FK shu tomonda: teskarisi `problems` → `hacks` migratsiya halqasini
    #: yasardi.
    added_test = models.OneToOneField(
        "problems.TestCase",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hack_source",
    )

    #: ⚠️ `created_at` INDEKSLI — `TimeStampedModel` dan farq qiladi.
    #: Indeksni birxillashtirish DDL, ya'ni alohida qaror: `core/bases.py`.
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    judged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ["-created_at", "-pk"]
        constraints: ClassVar = [
            # Bitta nishonga bir vaqtda bitta tekshiruv: takroriy yuborish
            # judge navbatini uch baravar yuklardi va natija poygasi
            # bo'lardi.
            models.UniqueConstraint(
                fields=["hacker", "defender_attempt"],
                condition=models.Q(status="TESTING"),
                name="uniq_hack_in_flight",
            )
        ]
        indexes: ClassVar = [
            models.Index(fields=["problem", "-created_at"], name="hack_problem_feed"),
            models.Index(fields=["contest", "status"], name="hack_contest_status"),
            models.Index(fields=["hacker", "-created_at"], name="hack_by_user"),
        ]

    def __str__(self) -> str:
        return f"hack #{self.pk} {self.policy} {self.status}"


class HackRoom(models.Model):
    """Musobaqa xonasi — `contest_room` siyosati uchun (~40 kishi).

    Codeforces modeli: raund davomida ishtirokchi faqat O'Z xonasidagi
    yechimlarni ko'radi va hack qiladi. Xonasiz bu siyosat butun
    musobaqani ochib yuborardi.
    """

    contest = models.ForeignKey("contests.Contest", on_delete=models.CASCADE, related_name="rooms")
    number = models.PositiveIntegerField()

    class Meta:
        ordering: ClassVar = ["number"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["contest", "number"], name="uniq_room_number")
        ]

    def __str__(self) -> str:
        return f"{self.contest_id} xona #{self.number}"


class HackRoomMember(models.Model):
    """Kim qaysi xonada. `contest` alohida: uniqlik musobaqa bo'yicha."""

    room = models.ForeignKey(HackRoom, on_delete=models.CASCADE, related_name="members")
    contest = models.ForeignKey(
        "contests.Contest", on_delete=models.CASCADE, related_name="room_members"
    )
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="hack_rooms")

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["contest", "user"], name="uniq_room_member")
        ]

    def __str__(self) -> str:
        return f"{self.room_id}/{self.user_id}"


class HackLock(CreatedModel):
    """Masalani «lock» qilish — `contest_room` uchun shart.

    Codeforces qoidasi: lock qilgandan keyin o'sha masalaga QAYTA yuborib
    bo'lmaydi, evaziga xonadagi yechimlarni ko'rish va hack qilish
    ochiladi. Ya'ni hack huquqi tekin emas — u xatarga qo'yilgan ball.
    """

    contest = models.ForeignKey("contests.Contest", on_delete=models.CASCADE, related_name="locks")
    problem = models.ForeignKey("problems.Problem", on_delete=models.CASCADE, related_name="locks")
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="hack_locks")

    class Meta:
        ordering: ClassVar = ["-created_at"]
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["contest", "problem", "user"], name="uniq_hack_lock")
        ]

    def __str__(self) -> str:
        return f"{self.contest_id}/{self.problem_id}/{self.user_id}"
