"""Core entitylar — 05-domain-model 🔒."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

#: Ommaviy profilda foydalanuvchi o'zi yashira oladigan maydonlar.
PRIVACY_FIELDS: tuple[str, ...] = (
    "email",
    "birth_date",
    "country",
    "school",
    "grade",
    "website",
    #: Onlayn holat va oxirgi faollik — ijtimoiy havolalardan alohida.
    "online",
    #: Murabbiy — o'quvchi a'zo bo'lgan auditoriya egasi; o'quvchi yashira oladi.
    "coach",
    #: Ijtimoiy va tashqi profil havolalari.
    "social",
    #: Profil banneri — foydalanuvchi yuklagan rasm (ADR-0026).
    #: `avatar_url` dan farqli: avatar brend belgisi kabi turadi, banner
    #: esa shaxsiy tanlov, ya'ni yashirish mumkin bo'lishi kerak.
    "title_photo",
    "gender",
    #: Faoliyat lentasi (`/users/<u>/activity/`).
    "activity",
    #: Faollik xaritasi (`/users/<u>/calendar/`).
    "heatmap",
    #: Yechilgan masalalar xaritasi (`/users/<u>/problem-map/`).
    "recent_ac",
)

#: Bepul veb-sayt havolalari — birinchisi `User.website` da ham yotadi.
MAX_WEBSITES = 5

#: Codeforces yetkazib berish anketasidagi EU o'lchamlar (juft 40–60).
SHIRT_EU_SIZES: tuple[str, ...] = tuple(str(n) for n in range(40, 62, 2))


def default_hidden_fields() -> list[str]:
    """Pochta standart holatda yashirin, qolgan maydonlar ochiq.

    Ochiq standart — foydalanuvchi tanlovi. Pochta bundan mustasno: mavjud
    hisoblar uni «ommaviy profilda ko'rinmaydi» sharti bilan bergan, uni
    ochish egasining ongli qarori bo'lishi kerak.
    """
    return ["email"]


class User(AbstractUser):
    """Foydalanuvchi va uning 4 reytingi.

    4 reyting boshidanoq modellashtiriladi, UI da fazali ochiladi — ADR-0006.
    """

    class Locale(models.TextChoices):
        UZ = "uz", "O'zbekcha"
        KAA = "kaa", "Qaraqalpaqsha"
        RU = "ru", "Русский"
        EN = "en", "English"
        KK = "kk", "Қазақша"
        KY = "ky", "Кыргызча"
        TG = "tg", "Тоҷикӣ"
        TR = "tr", "Türkçe"
        ZH = "zh", "中文"
        ES = "es", "Español"

    #: Taqlidga qarshi shakl — `core.handles.skeleton`. `save()` da
    #: to'ldiriladi, ya'ni admin, staff API va seed'da bir xil ishlaydi.
    #: Yagonalik ikki darajada: registrsiz (`uniq_username_ci`) VA skelet
    #: bo'yicha — ADR-0016.
    username_skeleton = models.CharField(max_length=150, blank=True, db_index=True)
    #: Taxallus ASCII, ISM esa cheklovsiz — kirill, lotin, har qanday
    #: yozuv shu yerda turadi (ADR-0016).
    display_name = models.CharField(max_length=100, blank=True)
    #: Tasdiqlash MAJBURIY EMAS: tasdiqlanmagan hisob ham to'liq ishlaydi,
    #: faqat yuqorida eslatma turadi. Sabab — ro'yxatdan o'tishni to'sish
    #: xat kelmagan odamni butunlay yo'qotadi, tasdiq esa asosan bizga
    #: kerak: pochtasi ishlamaydigan hisob parolini tiklay olmaydi.
    email_verified_at = models.DateTimeField(null=True, blank=True)

    @property
    def email_verified(self) -> bool:
        return self.email_verified_at is not None

    avatar_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    # ADR-0006 — formulalar: 04-prd § Reyting formulalari
    rating_skills = models.IntegerField(default=0, db_index=True)
    rating_contest = models.IntegerField(default=1200, db_index=True)  # ADR-0027
    rating_activity = models.IntegerField(default=0)
    rating_challenges = models.IntegerField(default=1400)

    # Elo volatilligi uchun — birinchi 6 rated contest
    rated_contest_count = models.PositiveIntegerField(default=0)

    locale = models.CharField(max_length=8, choices=Locale.choices, default=Locale.UZ)
    theme = models.CharField(max_length=16, default="system")

    streak_count = models.PositiveIntegerField(default=0)
    streak_freeze_until = models.DateField(null=True, blank=True)
    last_active_date = models.DateField(null=True, blank=True)

    # ── Profil ma'lumotlari ──────────────────────────────────────────
    #: ISO 3166-1 alpha-2. Platforma global, ya'ni ro'yxat butun dunyo.
    country = models.CharField(max_length=2, blank=True)
    #: `UZ` da `profiles.catalog.UZ_REGIONS` dan kod, boshqa joyda erkin matn.
    region = models.CharField(max_length=80, blank=True)
    #: `UZ` da `profiles.catalog.UZ_DISTRICTS` dan tuman yoki shahar kodi.
    district = models.CharField(max_length=40, blank=True)
    #: Boshqa mamlakatlarda shahar — erkin matn.
    city = models.CharField(max_length=100, blank=True)
    school = models.CharField(max_length=150, blank=True)
    #: Katalogdagi maktab; bo'lmasa `school` erkin matni ko'rsatiladi.
    school_ref = models.ForeignKey(
        "core.School", null=True, blank=True, on_delete=models.SET_NULL, related_name="students"
    )
    grade = models.CharField(max_length=40, blank=True)
    website = models.URLField(blank=True)
    #: Qo'shimcha havolalar (0–5). `website` — birinchisi, maxfiylik kaliti
    #: ham shu; JSON manba, `website` esa moslashuv uchun nusxa.
    websites = models.JSONField(default=list, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    #: Aloqa uchun telefon — IXTIYORIY va ommaviy profilga HECH QACHON
    #: chiqmaydi (pochtadan ham maxfiyroq: u shaxsni to'g'ridan-to'g'ri
    #: bog'laydi). Maqsad — hisobni tiklash va musobaqa bildirishnomalari.
    #:
    #: SMS tasdiqlash hozircha YO'Q, ya'ni raqam tekshirilmagan. Shu
    #: sababli unga tayanib biror huquq berilmasligi kerak (masalan,
    #: parolni tiklash faqat pochta orqali qoladi) — aks holda begona
    #: raqam yozib hisobni egallash yo'li ochilardi.
    phone = models.CharField(max_length=20, blank=True)
    #: Ommaviy profilda YASHIRILGAN maydonlar. Bo'sh ro'yxat — hammasi
    #: ochiq: foydalanuvchi shuni tanladi, yashirish uning o'z qo'lida.
    hidden_fields = models.JSONField(default=default_hidden_fields, blank=True)
    #: Profil kartasida ko'rsatiladigan uchta yutuq (`profiles.achievements`).
    pinned_achievements = models.JSONField(default=list, blank=True)
    #: Ko'rinish — uslub, ovoz, mavzu almashish effekti (til va mavzu
    #: yuqoridagi alohida maydonlarda).
    ui_prefs = models.JSONField(default=dict, blank=True)
    #: Bildirishnoma turi → kanallar. Kalit yo'q bo'lsa — standart.
    notify_prefs = models.JSONField(default=dict, blank=True)

    # ── Rozilik (huquqiy) ────────────────────────────────────────────
    #: Shartlar va maxfiylik siyosatiga rozilik VAQTI. `null` — eski
    #: hisoblar (import qilinganlar ham shu yerda): ular ro'yxatdan
    #: yangi oqim bilan o'tmagan, ya'ni rozilik so'ralmagan. Bo'sh
    #: qoldirish ularni «rozilik bermagan» deb belgilab, keyingi
    #: kirishda qayta so'rashga yo'l ochadi.
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    #: Marketing xatlari uchun ALOHIDA rozilik (GDPR 7-modda): shartlar
    #: roziligi bilan birlashtirib bo'lmaydi. Standart — `False`, ya'ni
    #: ro'yxatdan o'tgan odamga xat yuborilmaydi.
    marketing_opt_in = models.BooleanField(default=False)

    #: Bepul almashtirish yiliga bir marta — shu sana bo'yicha sanaladi.
    username_changed_at = models.DateTimeField(null=True, blank=True)

    # ── Competitor parity: stored caches (ADR-0024) ──────────────────
    # Values that used to be computed on every read. Their sources stay
    # authoritative, and `recount_user_stats` rebuilds these columns.
    #: Latest activity on any device; written together with `UserSession.last_seen`.
    last_seen_at = models.DateTimeField(null=True, blank=True, db_index=True)
    #: Highest `RatingHistory.value_after` per rating; `None` until the first row.
    max_rating_skills = models.IntegerField(null=True, blank=True)
    max_rating_contest = models.IntegerField(null=True, blank=True)
    max_rating_activity = models.IntegerField(null=True, blank=True)
    max_rating_challenges = models.IntegerField(null=True, blank=True)
    #: Longest streak reached; `streak_count` is the current one.
    streak_max = models.PositiveIntegerField(default=0)
    #: Solved public problems: the figure the profile shows. A solved problem
    #: that is not public yet (a contest's, say) counts once it is published.
    solved_count = models.PositiveIntegerField(default=0, db_index=True)

    # ── Rating tier and social fields (ADR-0026) ─────────────────────
    # Dormant columns, like the P3 group of ADR-0024: they exist before the
    # features that read them. `sync_codeforces` is their only writer today.
    #
    # NAMES ARE DELIBERATELY NEUTRAL. A Codeforces field is a competitor's
    # name, and ADR-0014 refused to let one reach the schema: every request,
    # serializer and migration would then depend on it, and removing it
    # later would be expensive. ADR-0024 opened this path with
    # `contribution` — a Codeforces field under a neutral name — and these
    # four continue it. The source is recorded in the writer and in
    # `core/migrations/0022`, not in the column name.
    #: Tier name for `rating_contest` ("expert", "legendary grandmaster").
    #: NOT a number — that live value stays in `rating_contest`.
    rank_title = models.CharField(max_length=40, blank=True)
    #: Highest tier ever reached; `max_rating_contest` is its numeric twin.
    max_rank_title = models.CharField(max_length=40, blank=True)
    #: Friends on the source profile. Zero until our own follow system
    #: writes it, so a synced row and a local row mean the same thing.
    friend_count = models.IntegerField(default=0)
    #: Profile banner. Distinct from `avatar_url`, which is the small
    #: circular image shown next to the handle.
    title_photo_url = models.URLField(max_length=200, blank=True)

    class ShirtSize(models.TextChoices):
        XS = "XS", "XS"
        S = "S", "S"
        M = "M", "M"
        L = "L", "L"
        XL = "XL", "XL"
        XXL = "XXL", "XXL"
        XXXL = "3XL", "3XL"

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        NON_BINARY = "non_binary", "Non-binary"
        PREFER_NOT = "prefer_not", "Prefer not to say"

    #: For olympiad prizes. Owner-only and never public, like `phone`.
    shirt_size = models.CharField(max_length=4, choices=ShirtSize.choices, blank=True)
    #: EU numeric twin of `shirt_size` (Codeforces delivery form). Owner-only.
    shirt_size_eu = models.CharField(
        max_length=4, blank=True, choices=[(n, n) for n in SHIRT_EU_SIZES]
    )
    #: Optional; public only when `gender` is not in `hidden_fields`.
    gender = models.CharField(max_length=16, choices=Gender.choices, blank=True)
    #: English names for certificates and delivery. Native names stay in
    #: `first_name` / `last_name` (AbstractUser) and are never public.
    first_name_en = models.CharField(max_length=150, blank=True)
    last_name_en = models.CharField(max_length=150, blank=True)

    # ── Competitor-parity columns (ADR-0024) ─────────────────────────
    # The owner chose on 2026-09-18 to add these columns before the features
    # that use them. `postal_*` are now owner-only on `/me/` (delivery
    # settings). `plan`, `device_fingerprint` and `coach_can_view_attempts`
    # stay internal. Do not remove them as unused: `tools/check_decisions.py`
    # guards the list.

    class Plan(models.TextChoices):
        # PRD P2-3; prices and limits come with the monetization ADR.
        FREE = "free", "Free"
        PLUS = "plus", "Plus"
        PRO = "pro", "Pro"

    #: Subscription plan. Set only by the future payment flow, never by the user.
    plan = models.CharField(max_length=16, choices=Plan.choices, default=Plan.FREE)
    plan_expires_at = models.DateTimeField(null=True, blank=True)
    #: Delivery address for physical prizes. Owner-only, never public.
    #: English block (`postal_*`) plus native-script twin (`*_native`).
    postal_recipient = models.CharField(max_length=150, blank=True)
    postal_country = models.CharField(max_length=2, blank=True)
    postal_region = models.CharField(max_length=80, blank=True)
    postal_city = models.CharField(max_length=100, blank=True)
    postal_address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=16, blank=True)
    postal_recipient_native = models.CharField(max_length=150, blank=True)
    postal_region_native = models.CharField(max_length=80, blank=True)
    postal_city_native = models.CharField(max_length=100, blank=True)
    postal_address_native = models.CharField(max_length=255, blank=True)
    #: Required when any postal field is filled; cleared when the address is erased.
    postal_consent = models.BooleanField(default=False)
    #: Consent for coaches to open this user's attempts.
    coach_can_view_attempts = models.BooleanField(default=False)
    #: Minimum rating a sender needs to start private messages; `None` means anyone.
    message_min_rating = models.IntegerField(null=True, blank=True)
    #: Sum of votes on the user's posts and comments; may be negative.
    contribution = models.IntegerField(default=0)
    #: Hash of the last device fingerprint, for olympiad integrity. Internal only.
    device_fingerprint = models.CharField(max_length=64, blank=True)
    #: Open for random duel matchmaking until this moment.
    duel_ready_until = models.DateTimeField(null=True, blank=True)

    class Meta(AbstractUser.Meta):  # type: ignore[name-defined,misc]
        indexes: ClassVar = [
            models.Index(fields=["-rating_skills"], name="user_skills_desc"),
            models.Index(fields=["-rating_contest"], name="user_contest_desc"),
        ]
        constraints: ClassVar = [
            # `Aziz` va `aziz` bir xil nom. Serializerdagi tekshiruv
            # parallel so'rovda o'tkazib yuborishi mumkin — kafolat
            # bazada bo'lishi shart.
            models.UniqueConstraint(Lower("username"), name="uniq_username_ci"),
            # Email parolni tiklash kanali — ya'ni ikki hisob bitta
            # pochtaga bog'lansa, tiklash havolasi qaysi hisobniki
            # ekani noaniq bo'ladi. Registr ham ahamiyatsiz: pochta
            # xizmatlari uchun `Aziz@` va `aziz@` bitta quti.
            #
            # Shart BO'SHNI chetlab o'tadi: import qilingan mualliflar va
            # stress foydalanuvchilarida pochta yo'q (10 068 ta), ular
            # bir-biriga xalaqit bermasligi kerak.
            models.UniqueConstraint(
                Lower("email"),
                condition=~models.Q(email=""),
                name="uniq_email_ci",
            ),
            # Taqlid: kirill va lotinda ko'zga bir xil ko'rinadigan harflar
            # bor, ya'ni registrsiz yagonalik yetmaydi — ADR-0016.
            models.UniqueConstraint(
                "username_skeleton",
                condition=~models.Q(username_skeleton=""),
                name="uniq_username_skeleton",
            ),
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        from core.handles import skeleton

        self.username_skeleton = skeleton(self.username)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.username


class ApiToken(models.Model):
    """Personal Access Token — ADR-0008.

    Ochiq token FAQAT bir marta, yaratilganda ko'rsatiladi; bazada
    SHA-256 hash saqlanadi.
    """

    PREFIX = "rw_"

    class Scope(models.TextChoices):
        READ = "read", "O'qish"
        SUBMIT = "submit", "Yechim yuborish"
        CONTEST_MANAGE = "contest:manage", "Contest boshqaruvi"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_tokens")
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=16)
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    scopes = models.JSONField(default=list)
    expires_at = models.DateTimeField()
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    MAX_ACTIVE_PER_USER = 10

    class Meta:
        indexes: ClassVar = [models.Index(fields=["user", "revoked_at"])]

    def __str__(self) -> str:
        return f"{self.name} ({self.prefix}…)"

    @staticmethod
    def hash_token(raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    @classmethod
    def issue(
        cls, user: User, name: str, scopes: list[str], expires_at: datetime
    ) -> tuple[ApiToken, str]:
        """Yangi token yaratadi. Qaytaradi: (obyekt, OCHIQ token).

        Ochiq token hech qayerda saqlanmaydi — chaqiruvchi uni bir marta
        foydalanuvchiga ko'rsatadi va unutadi.
        """
        raw = cls.PREFIX + secrets.token_urlsafe(32)
        token = cls.objects.create(
            user=user,
            name=name,
            prefix=raw[:10],
            token_hash=cls.hash_token(raw),
            scopes=scopes,
            expires_at=expires_at,
        )
        return token, raw

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and self.expires_at > timezone.now()

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes


class EmailDelivery(models.Model):
    """Har bir yuborilgan xat — bitta qator.

    Bu audit emas, DIAGNOSTIKA. Zanjir bepul planlar ustiga qurilgan
    (`core.mail_providers`), ya'ni «kvota tugadi» kundalik hodisa. Qaysi
    provayder ishlagani va qolganlari NEGA tushib qolgani ko'rinmasa,
    «email kelmadi» shikoyatini tekshirib bo'lmaydi.

    Xat TANASI ataylab saqlanmaydi: parol tiklash havolasi — token, uni
    bazaga yozish tokenni ikkinchi joyga ko'chirish demak.
    """

    class Purpose(models.TextChoices):
        PASSWORD_RESET = "password_reset", "Parolni tiklash"
        EMAIL_VERIFY = "email_verify", "Emailni tasdiqlash"
        #: Eski manzilga ogohlantirish — egasi o'zi qilmagan bo'lsa bilsin.
        EMAIL_CHANGED = "email_changed", "Pochta almashtirildi"
        OTHER = "other", "Boshqa"

    class Status(models.TextChoices):
        SENT = "sent", "Yuborildi"
        FAILED = "failed", "Yuborilmadi"
        #: Zaxira domen (RFC 2606/6761) — provayderga UMUMAN murojaat
        #: qilinmadi. `usage()` faqat `SENT` ni sanaydi, ya'ni bu qatorlar
        #: kunlik kvotaga tushmaydi, lekin iz qoladi.
        #:
        #: Nega alohida holat kerak: 2026-09-17 da load test 301 ta
        #: `@example.invalid` manzilga xat yubordi va ular `sent` bo'lib
        #: yozildi — ya'ni Brevo'ning 300/kun bepul shiftini 85 soniyada
        #: yoqib yubordi. Panel «311 yuborildi» derdi, aslida 10 tasi
        #: haqiqiy edi.
        SKIPPED = "skipped", "Yuborilmadi (zaxira domen)"

    to_email = models.EmailField()
    purpose = models.CharField(max_length=24, choices=Purpose.choices, default=Purpose.OTHER)
    subject = models.CharField(max_length=200)
    #: Muvaffaqiyatli provayder nomi; yuborilmagan bo'lsa bo'sh.
    provider = models.CharField(max_length=24, blank=True)
    status = models.CharField(max_length=8, choices=Status.choices)
    #: Tushib qolgan urinishlar: [{"provider": "brevo", "error": "HTTP 429: …"}]
    attempts = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [models.Index(fields=["to_email", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.to_email}: {self.subject}"


class EmailVerifyToken(models.Model):
    """Pochtani tasdiqlash havolasi.

    `PasswordResetToken` dan alohida, chunki qoidalari boshqa: muddati
    uzunroq (odam xatni ertaga ham ochishi mumkin va yo'qotadigan narsa
    yo'q), urinishlar chegarasi esa keraksiz — havola o'sha pochtaning
    o'zidan bosiladi.

    MANZIL yozib qo'yiladi. Usiz eski havola yangi manzilni tasdiqlab
    yuborardi: odam `a@x.uz` ga xat oldi, keyin manzilni `b@y.uz` ga
    almashtirdi va eski havolani bosib `b@y.uz` ni «tasdiqlangan» qildi —
    holbuki u manzilga hech qanday xat bormagan.
    """

    TTL = timedelta(hours=24)
    PER_USER_HOUR = 3

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verify_tokens")
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    code_hash = models.CharField(max_length=64)

    class Purpose(models.TextChoices):
        VERIFY = "verify", "Tasdiqlash"
        #: Yangi manzil — tasdiqlanmaguncha `User.email` o'zgarmaydi.
        CHANGE = "change", "Almashtirish"

    #: Token chiqarilgan manzil. `VERIFY` da joriy manzil, `CHANGE` da yangisi.
    email = models.EmailField()
    purpose = models.CharField(max_length=8, choices=Purpose.choices, default=Purpose.VERIFY)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes: ClassVar = [models.Index(fields=["user", "-created_at"])]

    def __str__(self) -> str:
        return f"verify:{self.user_id}"

    @staticmethod
    def hash_value(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    @property
    def is_live(self) -> bool:
        return self.used_at is None and self.expires_at > timezone.now()


class PasswordResetToken(models.Model):
    """Parolni tiklash — havola va 6 xonali kod bitta yozuvda (ADR-0015).

    Ikki yo'l bir sababga ko'ra: havola telefondagi pochtadan kompyuterdagi
    brauzerga o'tmaydi, kod esa o'tadi. Korporativ filtr havolani oldindan
    "bosib ko'rsa" u kuchini yo'qotardi — kod esa qoladi.

    Ochiq qiymat saqlanmaydi, `ApiToken` dagi kabi SHA-256 hash yoziladi.
    Xat tanasi ham hech qayerda saqlanmaydi (`EmailDelivery`), ya'ni
    tokenning ikkinchi nusxasi qolmaydi.
    """

    #: Havola ham, kod ham shuncha yashaydi. Uzunroq muddat o'g'irlangan
    #: pochta bilan hisobni egallash oynasini kengaytirardi.
    TTL = timedelta(hours=1)
    #: Kod atigi 6 xonali — cheksiz urinish uni bir necha daqiqada topardi.
    MAX_ATTEMPTS = 5
    PER_USER_HOUR = 3
    #: IP chegarasi kengroq: maktab sinfi bitta tashqi IP ortida bo'ladi.
    PER_IP_HOUR = 10

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_tokens")
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    code_hash = models.CharField(max_length=64)
    #: Xatda ko'rsatiladi, «bu men emasman» degan xulosa uchun (ADR-0015).
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    request_ua = models.CharField(max_length=200, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [models.Index(fields=["user", "-created_at"], name="reset_by_user")]

    def __str__(self) -> str:
        return f"{self.user_id} @ {self.created_at:%Y-%m-%d %H:%M}"

    @staticmethod
    def hash_value(raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    @property
    def is_live(self) -> bool:
        return self.used_at is None and self.expires_at > timezone.now()


class SocialAccount(models.Model):
    """Ijtimoiy kirish bog'lanishi — ADR-0016.

    Bir foydalanuvchida har provayderdan bittadan bo'lishi mumkin, va
    bitta provayder identifikatori faqat bitta hisobga tegishli.

    Bog'lash HECH QACHON avtomatik emas: provayder bergan email allaqachon
    parolli hisobda bo'lsa, avval parol so'raladi. Emailni tasdiqlash
    majburiy emas, ya'ni tasdiqlanmagan begona manzil bilan ochilgan hisob
    o'sha manzilning haqiqiy egasiga ochib berilardi.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_accounts")
    provider = models.CharField(max_length=16)
    uid = models.CharField(max_length=64)
    #: Provayder bergan manzil — audit uchun; hisobning o'z pochtasi
    #: `User.email` da qoladi va bu uni almashtirmaydi.
    email = models.EmailField(blank=True)
    #: Provayder bergan rasm manzili — «avatarni ulangan hisobdan olish».
    picture = models.URLField(max_length=500, blank=True)
    #: Provayderdagi taxallus (GitHub login, Telegram @username) — profil
    #: havolasini ulangan hisobdan bir bosishda olish uchun.
    username = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints: ClassVar = [
            models.UniqueConstraint(fields=["provider", "uid"], name="uniq_social_uid"),
            models.UniqueConstraint(fields=["user", "provider"], name="uniq_social_per_user"),
        ]

    def __str__(self) -> str:
        return f"{self.provider}:{self.uid} → {self.user_id}"


class UsernameHistory(models.Model):
    """Eski taxallus. Ikki vazifa: eski havolani yangi profilga yo'naltirish
    va nomni 90 kun boshqaga bermaslik — aks holda yangi egasi eski
    egasining obro'si bilan standings'da tura olardi."""

    RESERVE = timedelta(days=90)

    # `null=True` + `SET_NULL` ATAYLAB. Ilgari `CASCADE` edi va
    # `account.anonymize()` qatorlarni butunlay O'CHIRARDI — `reserved()`
    # aynan shu jadvaldan o'qiydi, ya'ni 90 kunlik himoya ishlamasdi va
    # odam o'z taxallusini darhol qayta olib, eski obro' bilan
    # standings'da turardi. Endi qator SAQLANADI, faqat egasidan
    # uziladi (`user=None`): `reserved()` ishlaydi, havola esa
    # `user__is_active=True` filtri tufayli yetim qolmaydi
    # (`core/views.py` — eski nomdan yangi profilga yo'naltirish).
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="username_history",
    )
    old_username = models.CharField(max_length=150, db_index=True)
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering: ClassVar = ["-changed_at"]

    def __str__(self) -> str:
        return f"{self.old_username} → {self.user_id}"


class UserSession(models.Model):
    """Kirilgan qurilma — sozlamalardagi «Sessiyalar» ro'yxati.

    Haqiqat manbai Django sessiyasi: bu jadval faqat unga ko'rinish
    beradi (qurilma, IP, oxirgi faollik). Sessiya o'chgan qator ro'yxatda
    ko'rsatilmaydi.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=40, unique=True)
    user_agent = models.CharField(max_length=200, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering: ClassVar = ["-last_seen"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.session_key[:6]}"


class AnalyticsEvent(models.Model):
    """Funnel hodisasi — auth oqimini o'lchash uchun (qaror 17).

    Nega alohida jadval: qaysi qadamda odam ketayotganini bilmasdan
    formani optimallashtirib bo'lmaydi — "mamlakat dropdown'ida 40%
    ketadi" kabi xulosa faqat shu yerdan chiqadi.

    IP ATAYLAB saqlanmaydi: joylashuv ma'lumoti shaxsiy ma'lumot
    (GDPR), funnel uchun esa kerak emas. `session_key` Django
    sessiyasidan olinadi — u allaqachon mavjud va IP'siz.
    """

    #: `auth.form_started`, `auth.form_error`, `auth.register_done`,
    #: `auth.step2_saved` kabi nomlar.
    name = models.CharField(max_length=48, db_index=True)
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )
    session_key = models.CharField(max_length=40, blank=True)
    path = models.CharField(max_length=200, blank=True)
    locale = models.CharField(max_length=8, blank=True)
    #: Erkin qo'shimcha maydonlar (`field`, `step`, `reason`).
    props = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["-created_at"]
        indexes: ClassVar = [
            models.Index(fields=["name", "-created_at"], name="event_name_time"),
        ]

    def __str__(self) -> str:
        return self.name


class School(models.Model):
    """Maktab katalogi (ADR-0017) — moderator admin paneldan to'ldiradi.

    Katalogda yo'q maktab `User.school` erkin matnida qoladi. Maktab
    reytingi va sinfdoshlar katalog bo'yicha quriladi: erkin matnda bitta
    maktab o'n xil yozilardi.
    """

    class Kind(models.TextChoices):
        SCHOOL = "school", "Maktab"
        LYCEUM = "lyceum", "Litsey"
        UNIVERSITY = "university", "Universitet"
        OTHER = "other", "Boshqa"

    name = models.CharField(max_length=200)
    kind = models.CharField(max_length=12, choices=Kind.choices, default=Kind.SCHOOL)
    country = models.CharField(max_length=2, default="UZ")
    region = models.CharField(max_length=40, blank=True)
    district = models.CharField(max_length=40, blank=True)
    city = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar = ["name"]
        indexes: ClassVar = [models.Index(fields=["region", "district"], name="school_place")]

    def __str__(self) -> str:
        return self.name


class SiteAppearance(models.Model):
    """Saytning standart ko'rinishi — jamoa belgilaydi (D37).

    **Singleton** (`pk=1`): bitta standart bo'ladi, ro'yxat emas.

    Yangi foydalanuvchi shuni ko'radi; **mavjudlarga TEGILMAYDI** — ular
    allaqachon o'z tanlovini qilgan, majburlash "mening sozlamamni
    kimdir o'zgartirdi" degan ishonchsizlik tug'diradi.

    Bu FAQAT boshlang'ich qiymat: foydalanuvchi o'zi tanlagach, uning
    tanlovi har doim ustun turadi.
    """

    #: `ui_prefs.appearance` bilan AYNI shakl (`core/prefs.py` validatoriga
    #: bo'ysunadi) — ya'ni qo'shimcha o'girish kerak emas.
    appearance = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Default appearance"
        verbose_name_plural = "Default appearance"

    def __str__(self) -> str:
        return "Default appearance"

    @classmethod
    def load(cls) -> SiteAppearance:
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
