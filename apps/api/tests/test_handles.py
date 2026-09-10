"""Taxallus qoidalari va taqlidga qarshi skelet — ADR-0016.

Taxallus standings'da va profil manzilida ko'rinadi, ya'ni u kimlik.
Shu sababli tekshiruvlar ikki xil: qaysi belgilar ruxsat etiladi va
ikkita nom bir-biriga o'xshab qolmasligi.
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient

from core import handles
from core.models import User


def register(username: str):
    return APIClient().post(
        reverse("register"),
        {
            "username": username,
            "email": f"{abs(hash(username))}@example.com",
            "password": "Parol!12345",
        },
        format="json",
    )


class TestQoidalar:
    @pytest.mark.parametrize(
        "nom",
        ["ali", "meNarzullayev", "ali_2007", "ali.valiyev", "ali-valiyev", "a" * 30, "user123"],
    )
    def test_ruxsat_etilgan(self, nom: str) -> None:
        handles.validate(nom)

    @pytest.mark.parametrize(
        ("nom", "sabab"),
        [
            ("ab", "juda qisqa"),
            ("a" * 31, "juda uzun"),
            ("ali valiyev", "bo'sh joy"),
            ("Абдужаббор", "kirill"),
            ("oʻktam", "o'zbekcha U+02BB"),
            ("ўктам", "kirill U+045E"),
            ("қодир", "kirill U+049B"),
            ("ali@uz", "belgi"),
            ("", "bo'sh"),
        ],
    )
    def test_rad_etiladi(self, nom: str, sabab: str) -> None:
        with pytest.raises(ValidationError):
            handles.validate(nom)


class TestSkelet:
    def test_registr_ahamiyatsiz(self) -> None:
        assert handles.skeleton("Admin") == handles.skeleton("admin")

    def test_kirill_taqlidi_bir_skeletga_tushadi(self) -> None:
        """`admin` ning birinchi harfi kirill `U+0430` bo'lsa, ekranda farq
        yo'q — skelet ularni birlashtiradi."""
        taqlid = "аdmin"  # kirill а + dmin

        assert taqlid != "admin"
        assert handles.skeleton(taqlid) == handles.skeleton("admin")

    def test_katta_harfdagi_taqlid_ham_tutiladi(self) -> None:
        """`U+0412` (kirill Ve) va lotin `B` bosh harfda farqsiz."""
        taqlid = "Вasil"

        assert handles.skeleton(taqlid) == handles.skeleton("Basil")

    def test_haqiqiy_kirill_ism_ozgacha_qoladi(self) -> None:
        """Fold taqlidni tutadi, lekin haqiqiy kirillcha ismni lotinnikiga
        aylantirib yubormasligi kerak."""
        assert handles.skeleton("Абдужаббор") != handles.skeleton("abdujabbor")

    def test_nuqta_va_chiziq_tegilmaydi(self) -> None:
        """`ali.2007` va `ali_2007` ko'zga yetarlicha farq qiladi."""
        assert handles.skeleton("ali.2007") != handles.skeleton("ali_2007")


@pytest.mark.django_db
class TestRoyxatdanOtish:
    def test_qoidaga_mos_nom_qabul_qilinadi(self) -> None:
        assert register("meNarzullayev").status_code == 201

    def test_bosh_joyli_nom_rad_etiladi(self) -> None:
        r = register("ali valiyev")

        assert r.status_code == 400
        assert "username" in str(r.data)

    def test_ozbekcha_harf_rad_etiladi(self) -> None:
        assert register("oʻktam").status_code == 400

    def test_kirill_nom_rad_etiladi(self) -> None:
        """Kirill `display_name` ga o'tdi. O'lchov: O'zbekistondagi ikkala
        yirik platformaning 379 ta taxallusida ASCII bo'lmagan belgi yo'q."""
        assert register("Абдужаббор").status_code == 400

    def test_kirill_ism_qabul_qilinadi(self) -> None:
        """Taxallus toraydi, ISM esa toraymaydi — bo'linishning butun mazmuni
        shu. Aks holda kirill yozadigan odam o'z ismini yoza olmasdi."""
        r = APIClient().post(
            reverse("register"),
            {
                "username": "abdujabbor",
                "email": "a@example.com",
                "password": "Parol!12345",
                "display_name": "Абдужаббор Каримов",
            },
            format="json",
        )

        assert r.status_code == 201
        assert User.objects.get(username="abdujabbor").display_name == "Абдужаббор Каримов"

    def test_taqlid_rad_etiladi(self) -> None:
        """`admin` ochilgach, uning kirill harfli nusxasi standings'da
        yonma-yon tura olmasligi kerak. Kirill endi belgilar darvozasidan
        ham o'tmaydi, ya'ni himoya ikki qavat."""
        assert register("admin").status_code == 201

        r = register("аdmin")

        assert r.status_code == 400
        assert User.objects.filter(username="аdmin").count() == 0

    def test_skelet_saqlanadi(self) -> None:
        register("meNarzullayev")

        user = User.objects.get(username="meNarzullayev")
        assert user.username_skeleton == handles.skeleton("meNarzullayev")


@pytest.mark.django_db
class TestBandlikTekshiruvi:
    """Yozayotgandagi tekshiruv — ro'yxatdan o'tishdagi qoidalar bilan
    BIR XIL javob berishi kerak. Aks holda «bo'sh» deb ko'rsatilgan nom
    yuborilganda 400 qaytadi va odam nimaga ishonishni bilmaydi."""

    def tekshir(self, nom: str):
        return APIClient().get(reverse("username-check"), {"u": nom})

    def test_bosh_nom(self) -> None:
        r = self.tekshir("yangiodam")

        assert r.status_code == 200
        assert r.data["available"] is True

    def test_band_nom(self) -> None:
        register("meNarzullayev")

        r = self.tekshir("menarzullayev")

        assert r.data["available"] is False, "registr farqi nomni bo'shatmaydi"

    def test_taqlid_ham_band_deb_ko_rsatiladi(self) -> None:
        register("admin")

        assert self.tekshir("Admin").data["available"] is False

    def test_qoidaga_mos_kelmagan_nom(self) -> None:
        r = self.tekshir("ali valiyev")

        assert r.data["available"] is False
        assert r.data["reason"], "sabab aytilishi kerak"

    @pytest.mark.parametrize("nom", ["yangiodam", "ali valiyev", ""])
    def test_javob_bir_xil_shaklda(self, nom: str) -> None:
        """Frontend bitta shaklga tayanadi — bo'sh so'rovda ham."""
        r = self.tekshir(nom)

        assert set(r.data) == {"available", "reason"}
