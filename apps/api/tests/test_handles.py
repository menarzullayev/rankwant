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
        "nom", ["ali", "meNarzullayev", "ali_2007", "ali.valiyev", "Абдужаббор", "user123"]
    )
    def test_ruxsat_etilgan(self, nom: str) -> None:
        handles.validate(nom)

    @pytest.mark.parametrize(
        ("nom", "sabab"),
        [
            ("ab", "juda qisqa"),
            ("a" * 21, "juda uzun"),
            ("ali valiyev", "bo'sh joy"),
            ("ali-valiyev", "chiziqcha"),
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

    def test_kirill_nom_qabul_qilinadi(self) -> None:
        assert register("Абдужаббор").status_code == 201

    def test_taqlid_rad_etiladi(self) -> None:
        """Bu qoidaning butun sababi: `admin` ochilgach, uning kirill
        harfli nusxasi standings'da yonma-yon tura olmasligi kerak."""
        assert register("admin").status_code == 201

        r = register("аdmin")

        assert r.status_code == 400
        assert User.objects.filter(username="аdmin").count() == 0

    def test_skelet_saqlanadi(self) -> None:
        register("meNarzullayev")

        user = User.objects.get(username="meNarzullayev")
        assert user.username_skeleton == handles.skeleton("meNarzullayev")
