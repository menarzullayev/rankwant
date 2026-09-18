"""Auth va PAT scope — ADR-0008. DoD: qamrov MAJBURIY."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core import views
from core.models import ApiToken, User
from core.serializers import RegisterSerializer


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestRegistrationLogin:
    def test_royxatdan_otish(self, client: APIClient) -> None:
        r = client.post(
            reverse("register"),
            {
                "username": "yangi",
                "email": "y@a.uz",
                "password": "Parol!12345",
                # Shartlarga rozilik MAJBURIY (qaror 13).
                "terms_accepted": True,
            },
        )
        assert r.status_code == 201

    def test_roziliksiz_royxat_rad_etiladi(self, client: APIClient) -> None:
        """GDPR sukut bo'yicha rozilikni tan olmaydi: belgilanmagan
        checkbox «rozilik» hisoblanmaydi, ya'ni server rad etishi shart."""
        r = client.post(
            reverse("register"),
            {
                "username": "roziliksiz",
                "email": "r@a.uz",
                "password": "Parol!12345",
            },
        )
        assert r.status_code == 400
        assert "terms_accepted" in r.json().get("error", {}).get("details", {})

    def test_rozilik_vaqti_va_marketing_saqlanadi(self, client: APIClient) -> None:
        """Shartlar roziligi — VAQT sifatida, marketing esa alohida
        (GDPR 7-modda: ikkalasini birlashtirib bo'lmaydi)."""

        r = client.post(
            reverse("register"),
            {
                "username": "marketingli",
                "email": "m@a.uz",
                "password": "Parol!12345",
                "country": "uz",
                "terms_accepted": True,
                "marketing_opt_in": True,
            },
        )
        assert r.status_code == 201
        user = User.objects.get(username="marketingli")
        assert user.terms_accepted_at is not None
        assert user.marketing_opt_in is True
        # Mamlakat kodi katta harfga keltiriladi (ISO 3166-1 alpha-2).
        assert user.country == "UZ"

    def test_marketing_standart_ochiq_emas(self, client: APIClient) -> None:
        """Belgi yuborilmasa marketing ROZI emas — aks holda platforma
        roziliksiz xat yuborardi."""

        r = client.post(
            reverse("register"),
            {
                "username": "marketingli2",
                "email": "m2@a.uz",
                "password": "Parol!12345",
                "terms_accepted": True,
            },
        )
        assert r.status_code == 201
        assert User.objects.get(username="marketingli2").marketing_opt_in is False

    def test_qisqa_parol_rad_etiladi(self, client: APIClient) -> None:
        r = client.post(reverse("register"), {"username": "x", "password": "123"})
        assert r.status_code == 400

    def test_band_email_maydon_boyicha_qaytadi(self) -> None:
        """14-qaror shartnomasi: band pochta `email` MAYDONIGA bog'lanadi.

        Bu test SHARTNOMANI qotiradi. Sabab: DRF maydon xatolarida
        `code` HAR DOIM `"invalid"` bo'ladi (`{"error":{"code":"invalid",
        "details":{"email":["Bu email band"]}}}`), ya'ni «band email» ni
        kod bo'yicha ajratib bo'lmaydi — frontend yagona ishonchli belgi
        sifatida `details` kalitidan foydalanadi (`ApiError.field`).

        Test SERIALIZER darajasida, HTTP javobida emas. Sabab
        o'lchandi: HTTP javobida `details` ga DRF O'ZI ham maydon
        qo'shadi (`username` majburiy bo'lsa `email` xatosi ham
        qo'shilib ketardi) va buzuq kod ham testdan o'tib ketardi —
        salbiy test buni ko'rsatdi. Serializerda poyga yo'q.
        """
        band = User.objects.create_user(
            username="band", email="band@example.com", password="Parol!12345"
        )
        serializer = RegisterSerializer(data={"email": band.email, "password": "Parol!12345"})

        assert not serializer.is_valid()
        assert serializer.errors["email"] == ["Bu email band"], serializer.errors

    def test_band_email_username_bilan_ham_aniqlanadi(self) -> None:
        """`username` ham yuborilganda xato baribir `email` da qoladi.

        Ya'ni 14-qaror yo'naltiruvchi xabari TO'LIQ formada ham
        ishlaydi: `username` xatosi o'sha javobga aralashmaydi.
        """
        band = User.objects.create_user(
            username="band2", email="band2@example.com", password="Parol!12345"
        )
        serializer = RegisterSerializer(
            data={
                "username": "boshqa",
                "email": band.email,
                "password": "Parol!12345",
            }
        )

        assert not serializer.is_valid()
        assert serializer.errors["email"] == ["Bu email band"], serializer.errors

    def test_username_siz_royxatdan_otish_ishlaydi(self, client: APIClient) -> None:
        """1-qadam yuki (`username`siz) QABUL QILINISHI shart.

        Regressiya testi. 2026-09-13 gacha veb-forma `username`
        yubormasdi, API esa uni majburiy deb bilardi: `extra_kwargs` da
        faqat `validators: []` turgan, `required`/`allow_blank` esa
        yozilmagan edi. Model maydonida `unique=True` bo'lgani uchun DRF
        uni `required=True, allow_blank=False` qilib yasaydi — ya'ni
        sayt orqali HECH KIM ro'yxatdan o'ta olmasdi.

        Nega eski testlar buni tutmadi: ular faqat `errors["email"]` ni
        tekshirardi (`test_band_email_...`), `username` xatosi esa
        o'sha javobda JIMGINA yonma-yon turardi. Shuning uchun bu test
        `is_valid()` ning O'ZINI va yaratilgan hisobni tekshiradi.

        HTTP darajasida sinaladi: shartnoma aynan shu qatlamda buzilgan
        edi (serializer `is_valid()` bermasa ham view 400 qaytaradi).
        """
        r = client.post(
            reverse("register"),
            {
                "email": "yangi@example.com",
                "password": "Parol!12345",
                "terms_accepted": True,
                "marketing_opt_in": False,
                "turnstile_token": "",
            },
            format="json",
        )

        assert r.status_code == 201, r.data
        user = User.objects.get(email="yangi@example.com")
        # Vaqtinchalik nom berilishi shart: model `unique=True` talab
        # qiladi, ya'ni bo'sh satr ikkinchi hisobda `IntegrityError`
        # berardi. Nom 2-qadamda (`/onboarding`) almashtiriladi.
        assert user.username.startswith("u"), user.username
        assert len(user.username) == 13, user.username
        # Kirish darhol ishlashi kerak: web registrdan keyin shu email
        # bilan login qiladi (ADR-0008 — registr sessiya ochmaydi).
        assert user.check_password("Parol!12345")

    def test_username_bolsh_qiymat_bilan_ham_ishlaydi(self, client: APIClient) -> None:
        """`username: ""` — «hozir so'ralmadi», xato emas (3-qaror).

        Eski API mijozlari maydonni bo'sh yuborishi mumkin; DRF
        modeldan `allow_blank=False` yasagani uchun bu ham
        «This field may not be blank» bilan rad etilardi.
        """
        r = client.post(
            reverse("register"),
            {
                "username": "",
                "email": "bosh@example.com",
                "password": "Parol!12345",
                "terms_accepted": True,
            },
            format="json",
        )

        assert r.status_code == 201, r.data
        assert User.objects.get(email="bosh@example.com").username.startswith("u")

    def test_username_berilsa_saqlanadi(self, client: APIClient) -> None:
        """Eski mijoz `username` yuborsa — u SAQLANADI (orqaga moslik).

        `required=False` «endi qabul qilinmaydi» degani EMAS: mobil
        ilova va skriptlar maydonni hali ham yuboradi.
        """
        r = client.post(
            reverse("register"),
            {
                "username": "tanlangan",
                "email": "tanlangan@example.com",
                "password": "Parol!12345",
                "terms_accepted": True,
            },
            format="json",
        )

        assert r.status_code == 201, r.data
        assert User.objects.get(email="tanlangan@example.com").username == "tanlangan"

    def test_login_va_me(self, client: APIClient, user) -> None:
        r = client.post(reverse("login"), {"identifier": "aziz", "password": "Parol!12345"})
        assert r.status_code == 200
        assert client.get(reverse("me")).status_code == 200

    def test_notogri_parol(self, client: APIClient, user) -> None:
        r = client.post(reverse("login"), {"identifier": "aziz", "password": "notogri"})
        assert r.status_code == 401
        assert r.json()["error"]["code"] == "invalid_credentials"

    def test_anonim_me_ga_kira_olmaydi(self, client: APIClient) -> None:
        assert client.get(reverse("me")).status_code in (401, 403)


@pytest.mark.django_db
class TestApiToken:
    def test_ochiq_token_faqat_bir_marta(self, user) -> None:
        token, raw = ApiToken.issue(user, "ci", ["read"], timezone.now() + timedelta(days=30))
        assert raw.startswith("rw_")
        # Bazada faqat hash
        assert token.token_hash == ApiToken.hash_token(raw)
        assert raw not in str(ApiToken.objects.values().first())

    def test_bearer_bilan_kirish(self, client: APIClient, user) -> None:
        _, raw = ApiToken.issue(user, "ci", ["read"], timezone.now() + timedelta(days=1))
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        assert client.get(reverse("me")).status_code == 200

    def test_muddati_otgan_token(self, client: APIClient, user) -> None:
        _, raw = ApiToken.issue(user, "eski", ["read"], timezone.now() - timedelta(days=1))
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        assert client.get(reverse("me")).status_code == 401

    def test_bekor_qilingan_token(self, client: APIClient, user) -> None:
        token, raw = ApiToken.issue(user, "x", ["read"], timezone.now() + timedelta(days=1))
        token.revoked_at = timezone.now()
        token.save()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        assert client.get(reverse("me")).status_code == 401

    def test_notogri_token(self, client: APIClient, user) -> None:
        client.credentials(HTTP_AUTHORIZATION="Bearer rw_qalbaki")
        assert client.get(reverse("me")).status_code == 401

    def test_read_scope_submit_qila_olmaydi(
        self, client: APIClient, user, problem, language
    ) -> None:
        """ADR-0008 minimal ruxsat: `read` token yechim yubora olmaydi."""
        _, raw = ApiToken.issue(user, "readonly", ["read"], timezone.now() + timedelta(days=1))
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        r = client.post(
            reverse("attempt-list"),
            {"problem": problem.slug, "language": language.code, "source_code": "int main(){}"},
        )
        assert r.status_code == 403

    def test_submit_scope_ishlaydi(self, client: APIClient, user, problem, language) -> None:
        _, raw = ApiToken.issue(user, "bot", ["read", "submit"], timezone.now() + timedelta(days=1))
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {raw}")
        r = client.post(
            reverse("attempt-list"),
            {"problem": problem.slug, "language": language.code, "source_code": "int main(){}"},
        )
        assert r.status_code == 201

    def test_token_limiti(self, client: APIClient, user) -> None:
        client.force_authenticate(user=user)
        expires = (timezone.now() + timedelta(days=30)).isoformat()
        for i in range(ApiToken.MAX_ACTIVE_PER_USER):
            ApiToken.issue(user, f"t{i}", ["read"], timezone.now() + timedelta(days=30))
        r = client.post(
            reverse("apitoken-list"),
            {"name": "ortiqcha", "scopes": ["read"], "expires_at": expires},
            format="json",
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "token_limit"

    def test_muddat_bir_yildan_oshmaydi(self, client: APIClient, user) -> None:
        client.force_authenticate(user=user)
        r = client.post(
            reverse("apitoken-list"),
            {
                "name": "uzoq",
                "scopes": ["read"],
                "expires_at": (timezone.now() + timedelta(days=400)).isoformat(),
            },
            format="json",
        )
        assert r.status_code == 400

    def test_ochirish_bekor_qiladi(self, client: APIClient, user) -> None:
        """Audit izi saqlanishi uchun o'chirilmaydi, bekor qilinadi."""
        token, _ = ApiToken.issue(user, "x", ["read"], timezone.now() + timedelta(days=1))
        client.force_authenticate(user=user)
        assert client.delete(reverse("apitoken-detail", args=[token.pk])).status_code == 204
        token.refresh_from_db()
        assert token.revoked_at is not None


@pytest.mark.django_db
class TestHealth:
    """Readiness bog'liqliklarni haqiqatan tekshirishi kerak.

    Avval endpoint shartsiz `ok` qaytarardi: chaos sinovi Postgres'ni
    o'chirganda ham 200 olardi, ya'ni hech narsa o'lchanmasdi.
    """

    def test_hammasi_ishlaganda_200(self, monkeypatch) -> None:
        monkeypatch.setattr(views, "_check_redis", lambda: "ok")
        r = APIClient().get(reverse("health"))
        assert r.status_code == 200
        assert r.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}

    def test_redis_yiqilganda_503(self, monkeypatch) -> None:
        monkeypatch.setattr(views, "_check_redis", lambda: "ConnectionError")
        r = APIClient().get(reverse("health"))
        assert r.status_code == 503
        assert r.json()["status"] == "degraded"
        assert r.json()["checks"]["redis"] == "ConnectionError"

    def test_db_yiqilganda_503(self, monkeypatch) -> None:
        monkeypatch.setattr(views, "_check_database", lambda: "OperationalError")
        monkeypatch.setattr(views, "_check_redis", lambda: "ok")
        r = APIClient().get(reverse("health"))
        assert r.status_code == 503
        assert r.json()["checks"]["database"] == "OperationalError"

    def test_health_throttle_kesh_ga_tayanmaydi(self) -> None:
        """Redis o'lganda throttle o'zi yiqilib, hisobotni bermay qo'yardi."""
        from core.views import HealthView

        assert HealthView.throttle_classes == []


@pytest.mark.django_db
class TestDependencyErrors:
    """Bog'liqlik uzilishi 500 emas, toza 503 bo'lishi kerak (10-operations)."""

    def test_redis_uzilishi_503(self) -> None:
        import redis as redis_lib

        from core.errors import exception_handler

        r = exception_handler(redis_lib.exceptions.ConnectionError("down"), {})
        assert r is not None
        assert r.status_code == 503
        assert r.data["error"]["code"] == "dependency_unavailable"

    def test_db_uzilishi_503(self) -> None:
        from django.db.utils import OperationalError

        from core.errors import exception_handler

        r = exception_handler(OperationalError("down"), {})
        assert r is not None
        assert r.status_code == 503


@pytest.mark.django_db
class TestPlatformStats:
    """Mehmon bosh sahifasi raqamlari — autentifikatsiyasiz ochiq."""

    def test_stats_ochiq_va_toliq(self, user, problem, contest) -> None:
        r = APIClient().get(reverse("platform-stats"))
        assert r.status_code == 200
        assert set(r.json()) == {
            "users",
            "problems",
            "contests",
            "attempts",
            "statement_locales",
        }
        assert r.json()["problems"] >= 1
        # Arxivdagi til filtri shu ro'yxatga qarab ko'rsatiladi.
        assert r.json()["statement_locales"] == ["uz"]

    def test_urinishlar_sanaladi(self, user, problem, language) -> None:
        from judging.models import Attempt

        cache.delete("platform-stats")
        Attempt.objects.create(user=user, problem=problem, language=language, source_code="x")
        assert APIClient().get(reverse("platform-stats")).json()["attempts"] == 1


def test_profilda_orin_va_daraja_taqsimoti(db, problem, hard_problem) -> None:
    """Reyting raqami yolg'iz o'zi ma'no bermaydi — o'rin bilan birga beriladi."""
    from django.urls import reverse
    from rest_framework.test import APIClient

    from core.models import User
    from ratings.models import RatingHistory, UserSolvedProblem

    birinchi = User.objects.create_user("kuchli", rating_skills=2000)
    ikkinchi = User.objects.create_user("orta", rating_skills=1000)
    UserSolvedProblem.objects.create(
        user=ikkinchi, problem=problem, difficulty_at_solve=problem.difficulty
    )
    RatingHistory.objects.create(
        user=ikkinchi,
        rating_type="skills",
        value_before=0,
        value_after=1500,
        delta=1500,
        reason="problem_solved",
    )
    RatingHistory.objects.create(
        user=ikkinchi,
        rating_type="skills",
        value_before=1500,
        value_after=1000,
        delta=-500,
        reason="recalculation",
    )
    # Every writer of a history row also raises the stored maximum (ADR-0024).
    from ratings.services import bump_max_rating

    bump_max_rating(ikkinchi, "skills", 1500)
    bump_max_rating(ikkinchi, "skills", 1000)

    data = APIClient().get(reverse("user-detail", args=[ikkinchi.username])).data

    assert data["ranks"]["skills"] == 2, f"{birinchi.username} oldinda"
    # Reyting tushgan bo'lsa ham eng yuqori qiymat saqlanadi.
    assert data["max_ratings"]["skills"] == 1500
    levels = {row["code"]: row["solved"] for row in data["solved_by_level"]}
    assert levels["beginner"] == 1
    assert levels["master"] == 0


def test_leaderboardda_orin_hisoblanmaydi(db) -> None:
    """Har qatorga to'rtta COUNT qo'shilsa ro'yxat sekinlashardi."""
    from django.urls import reverse
    from rest_framework.test import APIClient

    from core.models import User

    User.objects.create_user("kimdir", rating_skills=100)

    row = APIClient().get(reverse("user-list")).data["results"][0]

    assert row["ranks"] == {}
    assert row["solved_by_level"] == []


class TestCacheOutage:
    """Redis uzilganda butun API 503 bo'lib qolgan edi — o'lchandi."""

    def raising_cache(self, monkeypatch):
        from django.core.cache import cache

        def boom(*args, **kwargs):
            raise ConnectionError("redis yiqildi")

        monkeypatch.setattr(cache, "get", boom)
        monkeypatch.setattr(cache, "set", boom)
        monkeypatch.setattr(cache, "get_many", boom)

    def test_oqish_kesh_yiqilganda_ham_ishlaydi(self, db, problem, monkeypatch) -> None:
        from django.urls import reverse
        from rest_framework.test import APIClient

        self.raising_cache(monkeypatch)

        assert APIClient().get(reverse("problem-list")).status_code == 200
        assert APIClient().get(reverse("platform-stats")).status_code == 200

    def test_yozish_kesh_yiqilganda_rad_etiladi(self, db, problem, user, monkeypatch) -> None:
        """Limitsiz yozishga ruxsat berish suiiste'molga eshik ochardi."""
        from django.urls import reverse
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user)
        self.raising_cache(monkeypatch)

        with pytest.raises(ConnectionError):
            client.post(reverse("problem-favourite", args=[problem.slug]))


@pytest.mark.django_db
class TestRoyxatdanOtishDarvozasi:
    """O'lchandi: registr farqi bilan taqlid, parol sifatida username."""

    URL = "/api/v1/auth/register/"

    def _post(self, **over):
        data = {
            "username": "aziz",
            "email": "aziz@example.uz",
            "password": "Parol!12345",
            # Rozilik MAJBURIY (qaror 13) — usiz har bir test 400 olardi
            # va bu yerdagi tekshiruvlar (nom bandligi, parol qoidalari)
            # umuman sinalmasdi.
            "terms_accepted": True,
            **over,
        }
        return APIClient().post(self.URL, data, format="json")

    def test_registr_farqi_bilan_taqlid_qilib_bolmaydi(self) -> None:
        assert self._post().status_code == 201
        r = self._post(username="Aziz", email="aziz2@example.uz")
        assert r.status_code == 400
        assert "username" in r.json().get("error", {}).get("details", r.json())

    def test_parol_username_ga_oxshay_olmaydi(self) -> None:
        """`validate_password` ga foydalanuvchi berilmasa,
        `UserAttributeSimilarityValidator` jim qolardi."""
        assert self._post(username="azizbekxon", password="azizbekxon").status_code == 400

    def test_parol_emailga_oxshay_olmaydi(self) -> None:
        assert self._post(password="azizbek@example.uz").status_code == 400

    def test_normal_royxat_otadi(self) -> None:
        assert self._post(username="dilnoza", password="Kuchli!Parol9").status_code == 201


def test_admin_marshruti_productionda_yoq() -> None:
    """Panelni hozir faqat tunnel yo'naltirishi yopib turibdi — o'lchandi:
    API konteynerida `/admin/login/` Django login sahifasini berardi.
    Himoya ingress qoidasida emas, sozlamada bo'lishi kerak."""
    from django.urls import NoReverseMatch, reverse

    from config import settings as conf

    if conf.ADMIN_ENABLED:
        assert reverse("admin:index") == "/admin/"
        return
    with pytest.raises(NoReverseMatch):
        reverse("admin:index")


@pytest.mark.django_db
class TestThrottleKaliti:
    """Cheklov kaliti MIJOZ yozadigan sarlavhadan olinmasligi kerak.

    O'lchandi: `NUM_PROXIES` siz DRF butun `X-Forwarded-For` ni kalit
    qiladi — bitta manzildan 1600 so'rovning 1270 tasi 429 bo'lgan, keyin
    sarlavhani almashtirib yuborilgan 10 so'rovning hammasi o'tgan.
    """

    def _ident(self, settings, header: str, **meta) -> str:
        from django.test import RequestFactory

        from core.throttling import ResilientAnonRateThrottle

        settings.TRUSTED_CLIENT_IP_HEADER = header
        request = RequestFactory().get("/api/v1/problems/", REMOTE_ADDR="10.0.0.1", **meta)
        return ResilientAnonRateThrottle().get_ident(request)

    def test_xom_forwarded_for_ga_ishonilmaydi(self, settings) -> None:
        soxta = {"HTTP_X_FORWARDED_FOR": "1.2.3.4"}
        assert self._ident(settings, "", **soxta) == "10.0.0.1"

    def test_ishonchli_sarlavha_ishlatiladi(self, settings) -> None:
        meta = {"HTTP_CF_CONNECTING_IP": "85.132.1.5", "HTTP_X_FORWARDED_FOR": "1.2.3.4"}
        assert self._ident(settings, "HTTP_CF_CONNECTING_IP", **meta) == "85.132.1.5"

    def test_sarlavha_yoq_bolsa_remote_addr(self, settings) -> None:
        assert self._ident(settings, "HTTP_CF_CONNECTING_IP") == "10.0.0.1"

    def test_har_foydalanuvchi_oz_kalitini_oladi(self, settings) -> None:
        birinchi = self._ident(settings, "HTTP_CF_CONNECTING_IP", HTTP_CF_CONNECTING_IP="85.1.1.1")
        ikkinchi = self._ident(settings, "HTTP_CF_CONNECTING_IP", HTTP_CF_CONNECTING_IP="85.1.1.2")
        assert birinchi != ikkinchi


@pytest.mark.django_db
class TestIchkiRenderChegarasi:
    """SSR chaqiruvlari tashrifchilar bilan bitta idishda turmasligi kerak.

    O'lchandi (2026-09-12): krauler `/users/*` sahifalarini aylanib
    chiqqanda `anon` chegara tugadi, SSR esa 429 ni ushlamay 500 ga
    aylantirdi — sayt hamma uchun ochilmay qoldi.
    """

    def _scope(self, settings, header: str, **meta) -> str | None:
        from django.contrib.auth.models import AnonymousUser
        from django.test import RequestFactory

        from core.throttling import ResilientAnonRateThrottle

        settings.TRUSTED_CLIENT_IP_HEADER = header
        request = RequestFactory().get("/api/v1/problems/", REMOTE_ADDR="172.18.0.7", **meta)
        request.user = AnonymousUser()
        throttle = ResilientAnonRateThrottle()
        throttle.allow_request(request, None)
        return throttle.scope

    def test_ichki_render_alohida_idishda(self, settings) -> None:
        assert self._scope(settings, "HTTP_CF_CONNECTING_IP") == "anon_internal"

    def test_tashrifchi_anon_idishida(self, settings) -> None:
        scope = self._scope(settings, "HTTP_CF_CONNECTING_IP", HTTP_CF_CONNECTING_IP="85.1.1.1")
        assert scope == "anon"

    def test_ichki_render_user_chegarasida_sanalmaydi(self, settings) -> None:
        # DRF `UserRateThrottle` ni autentifikatsiyasiz IP ga tushiradi, ya'ni
        # SSR uchun daqiqalik yana bitta umumiy idish paydo bo'lardi.
        from django.contrib.auth.models import AnonymousUser
        from django.core.cache import cache
        from django.test import RequestFactory

        from core.throttling import ResilientUserRateThrottle

        settings.TRUSTED_CLIENT_IP_HEADER = "HTTP_CF_CONNECTING_IP"
        cache.clear()
        request = RequestFactory().get("/api/v1/problems/", REMOTE_ADDR="172.18.0.7")
        request.user = AnonymousUser()
        assert ResilientUserRateThrottle().allow_request(request, None) is True
        assert cache.get("throttle_user_172.18.0.7") is None

    def test_sozlama_bosh_bolsa_hammasi_anon(self, settings) -> None:
        # Proksi sarlavhasi sozlanmagan joyda hamma so'rov xususiy manzildan
        # keladi — himoya kengayib ketmasligi kerak.
        assert self._scope(settings, "") == "anon"
