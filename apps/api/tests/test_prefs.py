"""`ui_prefs` sxemasi — v2, migratsiya va validatsiya (D33–D36).

Bu testlar **qarorlarni** tekshiradi: noma'lum versiya saqlanadimi,
eski shakl o'qiladimi, noto'g'ri qiymat rad etiladimi.
"""

from __future__ import annotations

import pytest

from core import prefs


class TestMigrate:
    def test_v1_yassi_shakl_guruhga_otadi(self) -> None:
        out = prefs.migrate({"style": "terminal", "sound": True, "effect": "fade"})
        assert out["version"] == 2
        assert out["appearance"]["style"] == "terminal"
        assert out["sound"] is True
        assert out["effect"] == "fade"

    def test_v1_bolsh_style_qoshilmaydi(self) -> None:
        """`style` yo'q bo'lsa `appearance` bo'sh qoladi — standart qo'llanadi."""
        out = prefs.migrate({"sound": False})
        assert out["appearance"] == {}

    def test_v2_ozgarmaydi(self) -> None:
        raw = {"version": 2, "appearance": {"style": "clay"}}
        assert prefs.migrate(raw) == raw

    def test_nomalum_versiya_tegilmaydi(self) -> None:
        """D36: kelajakdagi klient yozgan sozlama o'chirilmasin."""
        raw = {"version": 9, "appearance": {"style": "kelajak"}, "yangi": True}
        assert prefs.migrate(raw) == raw
        assert prefs.applies(raw) is False

    def test_buzilgan_qiymat_qollanmaydi(self) -> None:
        assert prefs.applies("matn") is False
        assert prefs.applies(None) is False

    def test_v1_qollanadi(self) -> None:
        assert prefs.applies({"style": "clay"}) is True


class TestValidate:
    def test_toliq_sxema_qabul_qilinadi(self) -> None:
        out = prefs.validate(
            {
                "appearance": {
                    "style": "clay",
                    "accent": {"hue": 262, "sat": 80},
                    "font": "inter",
                    "size": 110,
                    "density": "compact",
                },
                "a11y": {
                    "vision": "protan",
                    "motion": "reduce",
                    "bigTargets": True,
                    "strongFocus": False,
                },
                "templates": [
                    {"name": "Mening", "appearance": {"style": "swiss"}, "a11y": {}},
                ],
                "sound": True,
                "effect": "circle",
            }
        )
        assert out["version"] == 2
        assert out["appearance"]["accent"] == {"hue": 262, "sat": 80}
        assert out["templates"][0]["name"] == "Mening"

    def test_yassi_kalit_rad_etiladi(self) -> None:
        """v1 shakli endi noto'g'ri — `style` guruhga o'tdi."""
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"style": "clay"})

    def test_nomalum_guruh_kaliti_rad_etiladi(self) -> None:
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"appearance": {"yangi": 1}})

    @pytest.mark.parametrize(
        "accent",
        [
            {"hue": 360, "sat": 50},
            {"hue": -1, "sat": 50},
            {"hue": 10, "sat": 101},
            {"hue": "10", "sat": 50},
            {"hue": 10},
        ],
    )
    def test_accent_chegaralari(self, accent: dict[str, object]) -> None:
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"appearance": {"accent": accent}})

    def test_theme_appearance_ichida_bolmaydi(self) -> None:
        """Mavzu `User.theme` da — bir ma'no ikki joyda saqlanmasin."""
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"appearance": {"theme": "system"}})

    def test_font_null_bolishi_mumkin(self) -> None:
        """`null` — uslubning o'z shrifti (D14)."""
        out = prefs.validate({"appearance": {"font": None}})
        assert out["appearance"]["font"] is None

    def test_size_faqat_qadamlar(self) -> None:
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"appearance": {"size": 115}})

    def test_shablon_soni_cheklangan(self) -> None:
        rows = [
            {"name": f"S{i}", "appearance": {}, "a11y": {}} for i in range(prefs.TEMPLATE_MAX + 1)
        ]
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"templates": rows})

    def test_shablon_nomi_takrorlanmaydi(self) -> None:
        rows = [
            {"name": "Bir", "appearance": {}, "a11y": {}},
            {"name": "bir", "appearance": {}, "a11y": {}},
        ]
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"templates": rows})

    def test_token_qiymati_satr_bolmaydi(self) -> None:
        """Kuchli rejim tokeni faqat rang yoki son — matn emas."""
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"tokens": {"--rw-ground": "url(evil)"}})

    def test_token_qiymati_rang_qabul_qilinadi(self) -> None:
        out = prefs.validate({"tokens": {"--rw-ground": "#101010"}})
        assert out["tokens"] == {"--rw-ground": "#101010"}

    def test_token_soni_cheklangan(self) -> None:
        tokens = {f"--rw-x{i}": "#000" for i in range(prefs.TOKEN_MAX + 1)}
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"tokens": tokens})

    def test_sound_mantiqiy_bolsin(self) -> None:
        with pytest.raises(prefs.PrefsError):
            prefs.validate({"sound": "ha"})


@pytest.mark.django_db
class TestApi:
    def test_api_eski_shaklni_qabul_qilmaydi(self, client) -> None:
        """v1 yuborilsa 400 — o'qishda moslash klientda, yozishda emas."""
        from core.models import User

        user = User.objects.create_user("prefs-api", password="Parol!12345")
        client.force_login(user)
        res = client.patch(
            "/api/v1/me/",
            {"ui_prefs": {"style": "clay"}},
            content_type="application/json",
        )
        assert res.status_code == 400

    def test_api_v2_qabul_qiladi(self, client) -> None:
        from core.models import User

        user = User.objects.create_user("prefs-api2", password="Parol!12345")
        client.force_login(user)
        res = client.patch(
            "/api/v1/me/",
            {"ui_prefs": {"appearance": {"style": "swiss"}}},
            content_type="application/json",
        )
        assert res.status_code == 200
        user.refresh_from_db()
        assert user.ui_prefs["appearance"]["style"] == "swiss"
        assert user.ui_prefs["version"] == 2


@pytest.mark.django_db
class TestSiteAppearance:
    """D37 — jamoa belgilagan standart ko'rinish."""

    def test_bosh_bolsa_bosh_obyekt_qaytadi(self, client) -> None:
        res = client.get("/api/v1/appearance/")
        assert res.status_code == 200
        assert res.json() == {"appearance": {}}

    def test_belgilangan_qiymat_mehmonga_korinadi(self, client) -> None:
        from core.models import SiteAppearance

        row = SiteAppearance.load()
        row.appearance = {"style": "terminal", "size": 110}
        row.save(update_fields=["appearance"])

        res = client.get("/api/v1/appearance/")
        assert res.status_code == 200
        assert res.json()["appearance"]["style"] == "terminal"

    def test_singleton_bitta_qator(self) -> None:
        """Ikkinchi qator bo'lmasin: qaysi biri qo'llanishi noaniq bo'lardi."""
        from core.models import SiteAppearance

        SiteAppearance.load()
        SiteAppearance.load()
        assert SiteAppearance.objects.count() == 1
