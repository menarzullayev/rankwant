from __future__ import annotations

import re
from datetime import date
from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import serializers

from core import handles, prefs, turnstile, usernames
from core.models import (
    MAX_WEBSITES,
    PRIVACY_FIELDS,
    SHIRT_EU_SIZES,
    ApiToken,
    School,
    User,
    UserSession,
)
from core.throttling import TrustedClientIdent
from profiles.catalog import GRADES, UZ_DISTRICTS, UZ_REGIONS
from profiles.titles import TitleField


class UserPublicSerializer(serializers.ModelSerializer[User]):
    """Ommaviy profil.

    ADR-0006 fazali ochilish: Skills va Contests — Phase 0, Activity —
    Phase 1, Challenges — Phase 3 (duel qurilgach yoqildi).
    """

    ranks = serializers.SerializerMethodField()
    max_ratings = serializers.SerializerMethodField()
    solved_by_level = serializers.SerializerMethodField()
    title = TitleField()
    #: Codeforces'dagi daraja nomi (`rank_title`, ADR-0026). `title` dan
    #: ALOHIDA, chunki ikkisi boshqa tizim: `title` — RankWant unvoni
    #: (`rating_contest` dan HISOBLANADI, `kvark`…`galaktika`), bu esa
    #: manbadan KELADI (`newbie`…`legendary grandmaster`). Birlashtirilsa
    #: frontend qaysi birini chizishini bilmay qolardi va ism rangi
    #: buzilardi.
    cf_title = serializers.SerializerMethodField()
    #: Manbadagi eng yuqori daraja (`max_rank_title`).
    cf_max_title = serializers.SerializerMethodField()
    #: Banner — `SerializerMethodField` SHART: busiz DRF model
    #: maydonini to'g'ridan-to'g'ri o'qiydi va `get_title_photo_url`
    #: umuman chaqirilmaydi, ya'ni maxfiylik tekshiruvi o'lik kod bo'lib
    #: qoladi (o'lchandi: yashirilganda ham URL qaytdi).
    title_photo_url = serializers.SerializerMethodField()

    def get_cf_title(self, user: User) -> str:
        """Manbada unvon yo'q bo'lsa bo'sh satr — frontend uni chizmaydi."""
        return user.rank_title or ""

    def get_cf_max_title(self, user: User) -> str:
        return user.max_rank_title or ""

    def get_title_photo_url(self, user: User) -> str:
        """Profil banneri. `country` kabi `hidden_fields` ga bo'ysunadi:
        foydalanuvchi yuklagan rasm, ya'ni yashirish huquqi bo'lishi kerak."""
        if "title_photo" in (user.hidden_fields or []):
            return ""
        return user.title_photo_url or ""

    #: Mamlakat — bayroq uchun (ISO 3166-1 alpha-2). `SerializerMethodField`
    #: ATAYIN: reyting jadvali ommaviy, ya'ni `hidden_fields` ni hisobga
    #: olish shart — `profiles/public.py` dagi bilan bir xil qoida.
    country = serializers.SerializerMethodField()

    def get_country(self, user: User) -> str:
        """Yashirilgan bo'lsa bo'sh satr — jadvalda bayroq chizilmaydi."""
        if "country" in (user.hidden_fields or []):
            return ""
        return user.country

    def get_ranks(self, user: User) -> dict[str, int]:
        """Har reyting bo'yicha o'rin.

        Raqamning o'zi «ko'p yoki oz» ekanini aytmaydi — 800 yaxshimi
        yoki yomonmi, faqat boshqalar bilan solishtirganda ma'lum
        bo'ladi. KEP profilida ham har reyting yonida o'rin turadi.

        Faqat detal javobida hisoblanadi: leaderboard'da har qatorga
        to'rtta COUNT qo'shilib ketardi.
        """
        if self.context.get("view") and getattr(self.context["view"], "action", "") != "retrieve":
            return {}
        active = User.objects.filter(is_active=True)
        return {
            name: active.filter(**{f"{field}__gt": getattr(user, field)}).count() + 1
            for name, field in (
                ("skills", "rating_skills"),
                ("contest", "rating_contest"),
                ("activity", "rating_activity"),
                ("challenges", "rating_challenges"),
            )
        }

    def get_max_ratings(self, user: User) -> dict[str, int]:
        """Erishilgan eng yuqori qiymat — hozirgisi tushib ketgan bo'lsa ham."""
        if self.context.get("view") and getattr(self.context["view"], "action", "") != "retrieve":
            return {}
        from core.user_stats import MAX_RATING_FIELDS

        # Stored columns (ADR-0024) instead of a `MAX` over `RatingHistory` per
        # view. A rating without history is left out, as before.
        return {
            rating_type: value
            for rating_type, field in MAX_RATING_FIELDS.items()
            if (value := getattr(user, field)) is not None
        }

    def get_solved_by_level(self, user: User) -> list[dict[str, Any]]:
        """Daraja kesimida yechilganlar — KEP profilidagi taqsimot.

        Bitta Skills raqami «qayerda turibman» degan savolga javob
        beradi, bu esa «nimani mashq qilishim kerak» degan savolga.
        """
        if self.context.get("view") and getattr(self.context["view"], "action", "") != "retrieve":
            return []
        from collections import Counter

        from problems.models import DIFFICULTY_LEVELS, difficulty_level
        from ratings.models import UserSolvedProblem

        counts: Counter[str] = Counter()
        for value in UserSolvedProblem.objects.filter(
            user=user, problem__is_public=True
        ).values_list("problem__difficulty", flat=True):
            counts[difficulty_level(value)[0]] += 1
        return [
            {"code": code, "label": label, "solved": counts[code]}
            for _, code, label in DIFFICULTY_LEVELS
        ]

    class Meta:
        model = User
        fields = [
            "username",
            "display_name",
            "avatar_url",
            "bio",
            "title",
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "rating_challenges",
            "streak_count",
            "streak_max",
            "solved_count",
            "date_joined",
            "country",
            "ranks",
            "max_ratings",
            "solved_by_level",
            # ADR-0026 — manbadan kelgan maydonlar. Uchtasi `hidden_fields`
            # bilan yashirilishi mumkin emas (ular reyting jadvali kabi
            # ommaviy ma'lumot), lekin `title_photo_url` — foydalanuvchi
            # yuklagan rasm, shuning uchun u `get_title_photo_url` orqali
            # o'tadi.
            "cf_title",
            "cf_max_title",
            "friend_count",
            "title_photo_url",
        ]


#: Mavzu almashishdagi animatsiya turlari.
#: Mavzu almashish effektlari. Ta'rif `core/prefs.py` ga ko'chdi (sxema
#: bilan bir joyda tursin) — bu nom tashqi havolalar uchun qoldi.
UI_EFFECTS = prefs.EFFECTS


class MeSerializer(serializers.ModelSerializer[User]):
    school_ref = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.filter(is_active=True), allow_null=True, required=False
    )
    #: Katalog maktabining nomi — sozlamalardagi maydonda ko'rsatish uchun.
    school_name = serializers.SerializerMethodField()
    websites = serializers.ListField(
        child=serializers.URLField(max_length=200),
        required=False,
        max_length=MAX_WEBSITES,
    )

    def get_school_name(self, user: User) -> str:
        return user.school_ref.name if user.school_ref is not None else ""

    #: Ulangan provayderlar — sozlamalar sahifasi shu ro'yxatga qaraydi.
    social = serializers.SerializerMethodField()
    #: Faqat ijtimoiy hisob bilan kirgan odamda parol yo'q — sozlamalar
    #: «almashtirish» o'rniga «o'rnatish» formasini ko'rsatadi.
    has_password = serializers.SerializerMethodField()
    #: Keyingi bepul almashtirish sanasi va pullik narxi.
    username_change = serializers.SerializerMethodField()

    def get_social(self, obj: User) -> list[str]:
        return sorted(obj.social_accounts.values_list("provider", flat=True))

    def get_has_password(self, obj: User) -> bool:
        return obj.has_usable_password()

    def get_username_change(self, obj: User) -> dict[str, Any]:
        free_at = usernames.next_free_at(obj)
        return {"free_at": free_at.isoformat() if free_at else None, "price": usernames.PRICE}

    #: Telefon — IXTIYORIY va faqat o'ziga ko'rinadi. `PRIVACY_FIELDS` ga
    #: ATAYLAB qo'shilmagan: u ro'yxat «ommaviy profilda yashira oladigan»
    #: maydonlar uchun, telefon esa umuman ommaviy emas — yashirish
    #: tushunchasi yo'q.
    def validate_phone(self, value: str) -> str:
        """Bo'shliq va ajratgichlarni tozalab, raqamni tekshiradi.

        Sabab: bir xil raqam «+998 90 123 45 67» va «+998901234567»
        ko'rinishida ikki xil saqlansa, keyinchalik qidirish va
        solishtirish ishlamaydi. Format erkin qoldiriladi — xalqaro
        raqamlar har xil yoziladi.
        """
        cleaned = re.sub(r"[\s()\-]", "", value.strip())
        if not cleaned:
            return ""
        if not re.fullmatch(r"\+?\d{7,15}", cleaned):
            raise serializers.ValidationError(
                "Invalid phone number: digits, spaces, parentheses, hyphens, "
                "and a leading `+` are allowed."
            )
        return cleaned

    class Meta:
        model = User
        fields = [
            "id",
            "is_staff",
            "username",
            "email",
            "display_name",
            "first_name",
            "last_name",
            "first_name_en",
            "last_name_en",
            "email_verified",
            "social",
            "has_password",
            "avatar_url",
            "bio",
            "locale",
            "theme",
            "country",
            "region",
            "district",
            "city",
            "school",
            "school_ref",
            "school_name",
            "grade",
            "website",
            "websites",
            "gender",
            "birth_date",
            "phone",
            "shirt_size",
            "shirt_size_eu",
            "postal_recipient",
            "postal_country",
            "postal_region",
            "postal_city",
            "postal_address",
            "postal_code",
            "postal_recipient_native",
            "postal_region_native",
            "postal_city_native",
            "postal_address_native",
            "postal_consent",
            "hidden_fields",
            "pinned_achievements",
            "ui_prefs",
            "notify_prefs",
            "username_change",
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "streak_count",
            "streak_freeze_until",
            "date_joined",
        ]
        read_only_fields = [
            "is_staff",
            "id",
            # Pochta faqat tasdiqlangan almashtirish orqali (`me/email/`),
            # avatar esa faqat yuklash orqali: ixtiyoriy tashqi manzil har
            # profil ko'rilishini uchinchi tomonga bildirardi.
            "email",
            "avatar_url",
            "rating_skills",
            "rating_contest",
            "rating_activity",
            "streak_count",
            "streak_freeze_until",
            "date_joined",
        ]

    def validate_country(self, value: str) -> str:
        value = value.upper()
        if value and not re.fullmatch(r"[A-Z]{2}", value):
            raise serializers.ValidationError("Country code is invalid")
        return value

    @staticmethod
    def _clean_name(value: str) -> str:
        """A real name in any script: trimmed, one space between words, no control characters.

        These fields go on certificates and olympiad lists (ADR-0024), so a
        stray newline or tab would break the printed layout.
        """
        cleaned = " ".join(value.split())
        if re.search(r"[\x00-\x1f\x7f]", cleaned):
            raise serializers.ValidationError("The name must not contain control characters")
        return cleaned

    def validate_grade(self, value: str) -> str:
        """A code from `profiles.catalog.GRADES` (ADR-0024).

        A value saved before the catalogue existed passes while it is unchanged:
        the settings form sends every field, and rejecting one the person did not
        touch would block saving the rest.
        """
        if not value or value in GRADES:
            return value
        if self.instance is not None and value == self.instance.grade:
            return value
        raise serializers.ValidationError("The grade must be chosen from the list")

    def validate_first_name(self, value: str) -> str:
        return self._clean_name(value)

    def validate_last_name(self, value: str) -> str:
        return self._clean_name(value)

    def validate_first_name_en(self, value: str) -> str:
        return self._clean_name(value)

    def validate_last_name_en(self, value: str) -> str:
        return self._clean_name(value)

    def validate_postal_recipient(self, value: str) -> str:
        return self._clean_name(value)

    def validate_postal_recipient_native(self, value: str) -> str:
        return self._clean_name(value)

    def validate_shirt_size_eu(self, value: str) -> str:
        if value and value not in SHIRT_EU_SIZES:
            raise serializers.ValidationError("EU size must be an even number from 40 to 60")
        return value

    def validate_postal_country(self, value: str) -> str:
        return self.validate_country(value)

    def validate_websites(self, value: list[str]) -> list[str]:
        urls = []
        seen: set[str] = set()
        for raw in value:
            url = raw.strip()
            if not url:
                continue
            key = url.rstrip("/").lower()
            if key in seen:
                continue
            seen.add(key)
            urls.append(url)
        if len(urls) > MAX_WEBSITES:
            raise serializers.ValidationError(f"At most {MAX_WEBSITES} links")
        return urls

    def to_representation(self, instance: User) -> dict[str, Any]:
        data = super().to_representation(instance)
        urls = list(instance.websites or [])
        if not urls and instance.website:
            urls = [instance.website]
        data["websites"] = urls
        return data

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """Save only the fields the client sent.

        `ModelSerializer.update` saves the whole row. The row was read when the
        request began, so a full save would write back ratings, `solved_count`
        and `last_seen_at` over any update the judge worker made in between.
        """
        if "websites" in validated_data:
            urls = list(validated_data["websites"])
            validated_data["website"] = urls[0] if urls else ""
        elif "website" in validated_data:
            site = validated_data["website"] or ""
            urls = list(instance.websites or [])
            if site:
                if urls:
                    urls[0] = site
                else:
                    urls = [site]
            else:
                urls = urls[1:]
            validated_data["websites"] = urls
        for field, value in validated_data.items():
            setattr(instance, field, value)
        fields = set(validated_data)
        if "username" in fields:
            # `User.save` derives the skeleton from the name.
            fields.add("username_skeleton")
        if fields:
            instance.save(update_fields=sorted(fields))
        return instance

    def validate_username(self, value: str) -> str:
        """Foydalanuvchi nomini AYNAN registrdagi qoidalar bilan tekshiradi.

        Sabab: nom endi ro'yxatdan o'tishning 2-qadamida ham
        o'rnatiladi (3-qaror), ya'ni bu yerga ham o'sha tekshiruv
        kerak. Nusxa ko'chirilsa ikki yo'l vaqt o'tib bir-biridan
        uzoqlashardi — shuning uchun mantiq `handles`/`usernames`
        modullaridan chaqiriladi, `RegisterSerializer` esa xuddi shu
        tartibni ishlatadi.

        DIQQAT: `handles.validate` qiymat qaytarmaydi — mos kelmasa
        `ValidationError` TASHAYDI. Bu DRF uchun to'g'ri shakl: u
        xatoni maydonga bog'lab, 400 qaytaradi.

        O'zgarishsiz yuborilgan nom qabul qilinadi: sozlamalar formasi
        butun obyektni PATCH qiladi va nomni tegmagan bo'lsa ham
        yuboradi — «band» deb qaytarish odamni bekorga to'xtatardi.
        """
        if self.instance is not None and value == self.instance.username:
            return value
        handles.validate(value)
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is taken")
        if User.objects.filter(username_skeleton=handles.skeleton(value)).exists():
            raise serializers.ValidationError("This username is too similar to an existing one")
        if usernames.reserved(value):
            raise serializers.ValidationError("This username is reserved")
        return value

    def validate_birth_date(self, value: date | None) -> date | None:
        if value is not None and (value > timezone.localdate() or value.year < 1900):
            raise serializers.ValidationError("Date of birth is invalid")
        return value

    def validate_hidden_fields(self, value: Any) -> list[str]:
        if not isinstance(value, list) or any(v not in PRIVACY_FIELDS for v in value):
            raise serializers.ValidationError("Unknown field")
        return sorted(set(value))

    def validate_pinned_achievements(self, value: Any) -> list[str]:
        from profiles.achievements import PINNED_MAX, achieved

        if not isinstance(value, list) or len(value) > PINNED_MAX or len(set(value)) != len(value):
            raise serializers.ValidationError(f"At most {PINNED_MAX} distinct achievements")
        assert isinstance(self.instance, User)
        have = achieved(self.instance)
        if any(code not in have for code in value):
            raise serializers.ValidationError("This achievement has not been earned yet")
        return value

    def validate_theme(self, value: str) -> str:
        """`light` | `dark` | `system`.

        Maydon `max_length=16` bilan har qanday satrni qabul qilardi, ya'ni
        klient «system » yoki «Dark» yozib qo'ysa jimgina saqlanardi va
        keyin hech qanday mavzu qo'llanmasdi. Sozlagich yozadigan maydon
        uchun bu yetarli emas.
        """
        if value not in prefs.THEMES:
            raise serializers.ValidationError(f"Theme must be one of {', '.join(prefs.THEMES)}")
        return value

    def validate_ui_prefs(self, value: Any) -> dict[str, Any]:
        """Sxema `core/prefs.py` da — guruhlangan va versiyalangan (D33).

        Bu yerga mantiq yozilmaydi: sozlagich paneli ham, migratsiya ham,
        kelajakdagi CLI ham AYNI validatorga tayanishi kerak. Ilgari bu
        yerda uchta yassi kalit tekshirilardi va to'liq token to'plami
        (D9) uchun joy yo'q edi.
        """
        try:
            return prefs.validate(value)
        except prefs.PrefsError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_notify_prefs(self, value: Any) -> dict[str, dict[str, bool]]:
        from notifications.models import Notification

        if not isinstance(value, dict):
            raise serializers.ValidationError("An object was expected")
        kinds = set(Notification.Kind.values)
        clean: dict[str, dict[str, bool]] = {}
        for kind, channels in value.items():
            if kind not in kinds or not isinstance(channels, dict):
                raise serializers.ValidationError(f"Unknown type: {kind}")
            if set(channels) - {"site", "telegram"} or not all(
                isinstance(v, bool) for v in channels.values()
            ):
                raise serializers.ValidationError(f"Invalid channel: {kind}")
            clean[kind] = dict(channels)
        return clean

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        country = attrs.get("country", self.instance.country if self.instance else "")
        region = attrs.get("region", self.instance.region if self.instance else "")
        district = attrs.get("district", self.instance.district if self.instance else "")
        # O'zbekistonda viloyat ro'yxatdan — viloyat bo'yicha reyting shunga tayanadi.
        if country == "UZ" and region and region not in UZ_REGIONS:
            raise serializers.ValidationError({"region": "The region must be chosen from the list"})
        # Tuman — faqat O'zbekistonda va tanlangan viloyat ichidan; shahar — aksincha.
        if country == "UZ":
            if district and district not in UZ_DISTRICTS.get(region, ()):
                if "district" in attrs:
                    raise serializers.ValidationError(
                        {"district": "The district must be chosen from the region's list"}
                    )
                attrs["district"] = ""  # viloyat almashdi — eski tuman endi to'g'ri emas
            attrs["city"] = ""
        else:
            attrs["district"] = ""
        self._validate_delivery(attrs)
        return attrs

    #: English + native blocks must both be complete, or the address is empty.
    _POSTAL_EN = (
        "postal_recipient",
        "postal_country",
        "postal_region",
        "postal_city",
        "postal_address",
        "postal_code",
    )
    _POSTAL_NATIVE = (
        "postal_recipient_native",
        "postal_region_native",
        "postal_city_native",
        "postal_address_native",
    )

    def _validate_delivery(self, attrs: dict[str, Any]) -> None:
        keys = (*self._POSTAL_EN, *self._POSTAL_NATIVE, "postal_consent")
        if self.instance is None or not any(key in attrs for key in keys):
            return
        merged = {
            key: attrs[key] if key in attrs else getattr(self.instance, key) for key in keys
        }

        def filled(key: str) -> bool:
            value = merged[key]
            return bool(value) if isinstance(value, bool) else bool(str(value or "").strip())

        empty = not any(filled(key) for key in (*self._POSTAL_EN, *self._POSTAL_NATIVE))
        if empty:
            attrs["postal_consent"] = False
            return
        missing = {
            key: "Yetkazib berish uchun to'ldiring"
            for key in (*self._POSTAL_EN, *self._POSTAL_NATIVE)
            if not filled(key)
        }
        if not merged["postal_consent"]:
            missing["postal_consent"] = "Yetkazib berish uchun rozilik kerak"
        if missing:
            raise serializers.ValidationError(missing)


def _email_taken(value: str, *, exclude: User | None = None) -> bool:
    """Pochta boshqa hisobda bandmi — registrga qaramay."""
    rows = User.objects.filter(email__iexact=value)
    if exclude is not None:
        rows = rows.exclude(pk=exclude.pk)
    return rows.exists()


class EmailVerifySerializer(serializers.Serializer[None]):
    """Havola yoki `username` + kod. Ikkalasi ham bo'lmasa `consume` rad etadi."""

    token = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)


class UsernameCheckSerializer(serializers.Serializer[None]):
    """Yozayotgandagi javob. `reason` bo'sh bo'lsa nom bo'sh."""

    available = serializers.BooleanField()
    reason = serializers.CharField(allow_blank=True)


class RegisterSerializer(serializers.ModelSerializer[User]):
    password = serializers.CharField(write_only=True, min_length=8)
    #: Shartlar va maxfiylik siyosatiga rozilik — MAJBURIY va `True`
    #: bo'lishi shart. GDPR sukut bo'yicha rozilikni tan olmaydi, ya'ni
    #: belgilanmagan checkbox «rozilik» hisoblanmaydi.
    terms_accepted = serializers.BooleanField(write_only=True)
    #: Marketing xatlari — IXTIYORIY va ALOHIDA (GDPR 7-modda: shartlar
    #: roziligi bilan birlashtirib bo'lmaydi). Standart — `False`.
    marketing_opt_in = serializers.BooleanField(write_only=True, required=False, default=False)
    #: Turnstile tokeni (9-qaror). Vidjet KO'RINADI, lekin token baribir
    #: ixtiyoriy maydon: skript yuklanmasa u bo'sh keladi va qarorni server
    #: qabul qiladi — kalitlar sozlanmagan bo'lsa tekshiruv umuman o'chiq
    #: (`turnstile.enabled()`), sozlangan bo'lsa bo'sh token rad etiladi.
    turnstile_token = serializers.CharField(
        write_only=True, required=False, allow_blank=True, default=""
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "display_name",
            "country",
            "region",
            "terms_accepted",
            "marketing_opt_in",
            "turnstile_token",
        ]
        # Pochtasiz hisobni tiklab bo'lmaydi: parolni unutgan
        # foydalanuvchining boshqa kanali qolmaydi.
        #
        # `username` uchun validatorlar ATAYIN qayta beriladi: model
        # `unique=True` bo'lgani uchun DRF o'zining `UniqueValidator`
        # ini qo'shadi, u esa pastdagi `validate_username` dan OLDIN
        # ishlab, inglizcha «A user with that username already exists»
        # qaytarardi — ya'ni o'zbekcha matn hech qachon ko'rinmasdi va
        # registrni farqlamaydigan tekshiruv ham o'tkazib yuborilardi.
        #
        # ⚠️ `validators: []` YETMAYDI — `required` va `allow_blank` ham
        # SHU YERDA berilishi shart. Model maydonida `unique=True` bor,
        # ya'ni DRF `username` ni `required=True, allow_blank=False` qilib
        # yasaydi. 2026-09-13 da aynan shu sababdan ro'yxatdan o'tish
        # BUTUNLAY ishlamay qolgan edi: veb-forma 1-qadamda `username`
        # yubormaydi (3-qaror), server esa uni talab qilardi va har bir
        # urinish `400 {"username": ["Ushbu maydon to'ldirilishi shart."]}`
        # bilan qaytardi. O'lchandi: `required`/`allow_blank` faqat shu
        # yozuvda turganda `username` ni umuman yubormasdan `201` olinadi.
        extra_kwargs = {
            "email": {"required": True, "allow_blank": False},
            # Django ning standart validatori o'rniga o'zimizniki: u lotin,
            # kirill, raqam, `_` va `.` ga ruxsat beradi va o'zbekcha maxsus
            # harflarni rad etadi — ADR-0016.
            "username": {"required": False, "allow_blank": True, "validators": []},
            # Foydalanuvchi nomi, ism, mamlakat va viloyat IXTIYORIY.
            #
            # Sabab: 3-qarordan keyin frontend ularni ro'yxatdan
            # o'tishning 1-qadamida YUBORMAYDI — ular 2-qadamda
            # to'ldiriladi. Lekin ularni to'liq olib tashlash eski
            # API mijozlarini (mobil ilova, skriptlar) sindirardi:
            # ular hali ham shu maydonlarni yuboradi. Ya'ni
            # `required=False` — «endi so'ralmaydi», «endi qabul
            # qilinmaydi» emas.
            "display_name": {"required": False, "allow_blank": True},
            "country": {"required": False, "allow_blank": True},
            # Viloyat ham shu sababdan qoladi: A/B sinovning `b`
            # variantida u ro'yxatdan o'tishning o'zida so'raladi
            # (8-qaror), ya'ni bu maydon ikki yo'ldan ham keladi va
            # ikkalasi ham qabul qilinishi kerak.
            "region": {"required": False, "allow_blank": True},
        }

    def validate_country(self, value: str) -> str:
        value = value.upper()
        if value and not re.fullmatch(r"[A-Z]{2}", value):
            raise serializers.ValidationError("Country code is invalid")
        return value

    def validate_terms_accepted(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError("Accepting the terms is required")
        return value

    def validate_email(self, value: str) -> str:
        if _email_taken(value):
            raise serializers.ValidationError("This email is taken")
        return value

    def validate_username(self, value: str) -> str:
        # Bo'sh qiymat — «hozir so'ralmadi», 2-qadamda tanlanadi (3-qaror).
        # Bu yerda to'xtatib bo'lmaydi: 1-qadamda maydon umuman
        # ko'rsatilmaydi, ya'ni xato berish odamni boshi berk ko'chaga
        # olib kirardi. Nom `create` da VAQTINCHALIK beriladi va
        # 2-qadamda haqiqiysiga almashtiriladi.
        if not value:
            return ""
        try:
            handles.validate(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages[0]) from None

        # Registr farqi bilan taqlid qilishning oldini oladi: `Aziz` va
        # `aziz` bitta nom hisoblanadi. Reyting va profil obro'ga
        # bog'langan platformada bu xavfsizlik masalasi — o'lchandi,
        # mavjud nomning katta harfli nusxasini olish mumkin edi.
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is taken")

        # Ko'zga o'xshash harflar bilan taqlid: kirill va lotinda bir xil
        # ko'rinadigan harflar bor, ya'ni registrsiz tekshiruv yetmaydi.
        if User.objects.filter(username_skeleton=handles.skeleton(value)).exists():
            raise serializers.ValidationError("This username is too similar to an existing one")
        # Nomini almashtirgan odamning eski nomi 90 kun band — aks holda
        # yangi egasi eski egasining obro'si bilan standings'da tura olardi.
        if usernames.reserved(value):
            raise serializers.ValidationError(
                "This name recently belonged to another user"
            )
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # `validate_password` ga foydalanuvchi BERILISHI shart: usiz
        # `UserAttributeSimilarityValidator` umuman ishlamaydi va parol
        # sifatida username ni kiritish qabul qilinardi (o'lchandi).
        validate_password(
            attrs["password"],
            User(
                username=attrs.get("username", ""),
                email=attrs.get("email", ""),
                display_name=attrs.get("display_name", ""),
            ),
        )

        # Turnstile ENG OXIRIDA: token bir martalik, ya'ni uni parol
        # qoidasi yoki band pochta uchun behuda sarflash odamni qayta
        # yechishga majbur qilardi (9-qaror).
        request = self.context.get("request")
        # IP manbai — `TrustedClientIdent`: u `TRUSTED_CLIENT_IP_HEADER`
        # ni hisobga oladi, xom `X-Forwarded-For` ga esa hech qachon
        # ishonmaydi. Yangi yordamchi yozilsa ikki xil haqiqat paydo
        # bo'lardi.
        remote_ip = TrustedClientIdent().get_ident(request) if request is not None else ""
        try:
            turnstile.verify(attrs.get("turnstile_token", ""), remote_ip=remote_ip)
        except turnstile.TurnstileError as exc:
            raise serializers.ValidationError({"turnstile_token": str(exc)}) from None
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        password = validated_data.pop("password")
        # `terms_accepted` — model maydoni EMAS (modelda sana turadi),
        # ya'ni `User(**...)` ga uzatilsa `TypeError` berardi. Rozilik
        # FAKTI serializerda tekshirildi, VAQTI esa shu yerda yoziladi.
        validated_data.pop("terms_accepted", None)
        # `turnstile_token` — model maydoni EMAS; u `validate()` da
        # sarflandi va `User(**...)` ga tushsa `TypeError` berardi.
        validated_data.pop("turnstile_token", None)
        # Nom berilmagan bo'lsa VAQTINCHALIK nom: model `unique=True`
        # talab qiladi, ya'ni bo'sh satr ikkinchi ro'yxatdan o'tishda
        # `IntegrityError` berardi. Nom 2-qadamda tanlanadi.
        validated_data["username"] = validated_data.get("username") or self._temp_username()
        user = User(**validated_data)
        user.terms_accepted_at = timezone.now()
        user.set_password(password)
        try:
            user.save()
        except IntegrityError:
            # Nom yoki pochta bandligi serializerda, yozuv esa bazada
            # tekshiriladi — oradagi oynada bir vaqtda kelgan so'rovlar
            # 500 berardi.
            field = "email" if _email_taken(validated_data.get("email", "")) else "username"
            raise serializers.ValidationError(
                {field: "This email is taken" if field == "email" else "This username is taken"}
            ) from None
        return user

    @staticmethod
    def _temp_username() -> str:
        """Vaqtinchalik nom — `u` + tasodifiy 12 belgi.

        `u` prefiksi `handles.ALLOWED` ga mos keladi va band bo'lgan
        nomlar orasida ham uchramaydi (ular `usernames.reserved` da).
        To'qnashuv ehtimoli 36^12, ya'ni amalda nol; baribir tsikl
        bilan tekshiriladi — bazada `unique` cheklovi bor, ya'ni
        to'qnashuv `IntegrityError` berardi va odam sababsiz xato
        ko'rardi.
        """
        from secrets import choice
        from string import ascii_lowercase, digits

        alphabet = ascii_lowercase + digits
        while True:
            candidate = "u" + "".join(choice(alphabet) for _ in range(12))
            if not User.objects.filter(username__iexact=candidate).exists():
                return candidate


class LoginSerializer(serializers.Serializer[dict[str, Any]]):
    """Kirish — bitta maydon: foydalanuvchi nomi YOKI email (4-qaror).

    Ilgari maydon `username` edi va faqat nom qabul qilinardi. Emailini
    yoddan bilgan, lekin taxallusini eslay olmaydigan odam «Login yoki
    parol noto'g'ri» olardi — holbuki u to'g'ri ma'lumot kiritgan edi.
    Qaror: maydon BITTA qoladi (ikki maydon kiritishni ikki barobar
    oshiradi), lekin qiymat ikki ustun bo'yicha qidiriladi.

    Maydon nomi ham `identifier` ga o'zgardi: `username` deb qolsa,
    email yuborilishi API shartnomasida ko'rinmasdi va hujjatda
    noto'g'ri taassurot qolardi.
    """

    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)
    #: «Meni eslab qol» — belgilansa sessiya `SESSION_COOKIE_AGE` (30 kun)
    #: yashaydi, aks holda brauzer yopilganda tugaydi. Standart `False`:
    #: umumiy kompyuterda (maktab, kutubxona) hisob ochiq qolmasligi kerak.
    remember = serializers.BooleanField(required=False, default=False)


class AccountDeleteSerializer(serializers.Serializer[dict[str, Any]]):
    password = serializers.CharField(write_only=True)


class AnalyticsEventInSerializer(serializers.Serializer[dict[str, Any]]):
    """Bitta funnel hodisasi (qaror 17)."""

    name = serializers.CharField(max_length=48)
    path = serializers.CharField(max_length=200, required=False, allow_blank=True)
    props = serializers.JSONField(required=False)

    def validate_props(self, value: Any) -> dict[str, Any]:
        # `props` mijozdan keladi, ya'ni unga ishonib bo'lmaydi: dict
        # emasligi bazaga har xil shakl yozib qo'yardi, katta obyekt esa
        # jadvalni shishirardi. Kalitlar soni cheklanadi.
        if value is None:
            return {}
        if not isinstance(value, dict) or len(value) > 12:
            raise serializers.ValidationError("props must be an object with at most 12 keys")
        return value


class AnalyticsBatchSerializer(serializers.Serializer[dict[str, Any]]):
    """Hodisalar partiyasi.

    Bir sahifada bir nechta hodisa yig'iladi va BITTA so'rovda yuboriladi:
    har hodisa uchun alohida so'rov mobil tarmoqda yo'qolardi va sahifa
    yuklanishini sekinlashtirardi.
    """

    events = AnalyticsEventInSerializer(many=True, allow_empty=False)

    def validate_events(self, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if len(value) > 25:
            raise serializers.ValidationError("At most 25 events")
        return value


class ApiTokenSerializer(serializers.ModelSerializer[ApiToken]):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = ApiToken
        fields = [
            "id",
            "name",
            "prefix",
            "scopes",
            "expires_at",
            "last_used_at",
            "revoked_at",
            "created_at",
            "is_active",
        ]
        read_only_fields = ["id", "prefix", "last_used_at", "revoked_at", "created_at"]


class ApiTokenCreateSerializer(serializers.Serializer[dict[str, Any]]):
    name = serializers.CharField(max_length=100)
    scopes = serializers.ListField(
        child=serializers.ChoiceField(choices=ApiToken.Scope.choices),
        allow_empty=False,
    )
    expires_at = serializers.DateTimeField()


class PasswordResetRequestSerializer(serializers.Serializer[dict[str, Any]]):
    """Tiklash so'rovi — email yoki username bo'yicha."""

    login = serializers.CharField(max_length=254)


class PasswordResetConfirmSerializer(serializers.Serializer[dict[str, Any]]):
    """Tasdiqlash — havola tokeni YOKI (username + kod).

    Ikkala yo'l ham qoladi: havola telefondagi pochtadan kompyuterdagi
    brauzerga o'tmaydi, kod esa o'tadi (ADR-0015).
    """

    token = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True, max_length=6)
    password = serializers.CharField(write_only=True)

    # Parol bu yerda TEKSHIRILMAYDI: `validate_password` ga foydalanuvchi
    # berilishi shart, aks holda `UserAttributeSimilarityValidator` ishlamaydi
    # va parol sifatida username qabul qilinardi (yuqorida o'lchangan).
    # Foydalanuvchi esa faqat token yechilgandan keyin ma'lum bo'ladi —
    # shuning uchun tekshiruv `PasswordResetConfirmView` da.

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if not attrs.get("token") and not (attrs.get("username") and attrs.get("code")):
            raise serializers.ValidationError(
                {"token": "A link token, or a username with a code, is required"}
            )
        return attrs


class SocialLinkSerializer(serializers.Serializer[dict[str, Any]]):
    """Ijtimoiy hisobni mavjud hisobga bog'lash — parol bilan tasdiqlanadi."""

    password = serializers.CharField(write_only=True)


class PasswordChangeSerializer(serializers.Serializer[None]):
    #: Paroli yo'q hisobda (faqat ijtimoiy kirish) bo'sh qoladi.
    old_password = serializers.CharField(required=False, allow_blank=True, write_only=True)
    new_password = serializers.CharField(write_only=True)


class EmailChangeSerializer(serializers.Serializer[None]):
    email = serializers.EmailField()
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)


class UsernameChangeSerializer(serializers.Serializer[None]):
    username = serializers.CharField(max_length=150)
    #: Bepul almashtirish ishlatilgan bo'lsa — Qvant bilan to'lashga rozilik.
    pay = serializers.BooleanField(required=False, default=False)


class UserSessionSerializer(serializers.ModelSerializer[UserSession]):
    current = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = ["id", "user_agent", "ip", "created_at", "last_seen", "current"]

    def get_current(self, obj: UserSession) -> bool:
        return obj.session_key == self.context.get("current_key")


class AvatarImportSerializer(serializers.Serializer[None]):
    provider = serializers.ChoiceField(choices=["google", "github", "telegram"])


class SchoolSerializer(serializers.ModelSerializer[School]):
    #: Katalog maktabini tanlagan faol foydalanuvchilar soni.
    members = serializers.IntegerField(read_only=True)

    class Meta:
        model = School
        fields = ["id", "name", "kind", "region", "district", "city", "members"]
