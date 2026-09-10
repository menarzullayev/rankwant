"""Parolni tiklash endpointlari — ADR-0015.

Token qatlami `test_recovery.py` da, xat `test_emails.py` da sinalgan.
Bu yerda faqat HTTP yuzasi: hisob mavjudligi oshkor bo'lmasligi, parol
validatorlarining chetlab o'tilmasligi, ikkala kirish yo'li.
"""

from __future__ import annotations

from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core import recovery
from core.models import PasswordResetToken, User


@pytest.fixture
def yuborilgan(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Any, ...]]:
    """Celery ga tegmaymiz — task chaqiruvini ushlab qolamiz."""
    chaqiruvlar: list[tuple[Any, ...]] = []
    monkeypatch.setattr(
        "core.views.send_password_reset.delay", lambda *a, **k: chaqiruvlar.append(a)
    )
    return chaqiruvlar


@pytest.fixture
def odam(db) -> User:
    return User.objects.create_user(
        username="odam", email="odam@example.com", password="Parol!12345"
    )


def sorov(login: str) -> Any:
    return APIClient().post(reverse("password-reset"), {"login": login}, format="json")


def tasdiq(**body: str) -> Any:
    return APIClient().post(reverse("password-reset-confirm"), body, format="json")


@pytest.mark.django_db
class TestSorov:
    def test_email_bilan_xat_yuboriladi(self, odam: User, yuborilgan: list) -> None:
        r = sorov("odam@example.com")

        assert r.status_code == 202
        assert len(yuborilgan) == 1
        assert yuborilgan[0][0] == odam.pk

    def test_username_bilan_ham_ishlaydi(self, odam: User, yuborilgan: list) -> None:
        assert sorov("odam").status_code == 202
        assert len(yuborilgan) == 1

    def test_registri_ahamiyatsiz(self, odam: User, yuborilgan: list) -> None:
        assert sorov("ODAM@Example.COM").status_code == 202
        assert len(yuborilgan) == 1

    def test_yoq_hisob_ham_202_qaytaradi(self, db, yuborilgan: list) -> None:
        """Aks holda bu endpoint hisob mavjudligini tekshirish quroli bo'lardi:
        manzillar ro'yxatini yuborib, qaysilari ro'yxatdan o'tganini bilib
        olish mumkin edi."""
        r = sorov("yoq@example.com")

        assert r.status_code == 202
        assert yuborilgan == []

    def test_faol_bolmagan_hisobga_yuborilmaydi(self, odam: User, yuborilgan: list) -> None:
        User.objects.filter(pk=odam.pk).update(is_active=False)

        assert sorov("odam").status_code == 202
        assert yuborilgan == []

    def test_chegaraga_urilganda_ham_javob_bir_xil(self, odam: User, yuborilgan: list) -> None:
        """Chegaraga urilgani ham SIR — javobdan buni bilib bo'lmaydi."""
        for _ in range(PasswordResetToken.PER_USER_HOUR):
            recovery.issue(odam)

        r = sorov("odam")

        assert r.status_code == 202
        assert yuborilgan == [], "chegara ustidan xat ketmasligi kerak"


@pytest.mark.django_db
class TestTasdiq:
    def test_havola_bilan_parol_ozgaradi(self, odam: User) -> None:
        issued = recovery.issue(odam)

        r = tasdiq(token=issued.raw, password="YangiParol!99")

        assert r.status_code == 204
        odam.refresh_from_db()
        assert odam.check_password("YangiParol!99")

    def test_kod_bilan_parol_ozgaradi(self, odam: User) -> None:
        issued = recovery.issue(odam)

        r = tasdiq(username="odam", code=issued.code, password="YangiParol!99")

        assert r.status_code == 204
        odam.refresh_from_db()
        assert odam.check_password("YangiParol!99")

    def test_token_bir_martalik(self, odam: User) -> None:
        issued = recovery.issue(odam)
        tasdiq(token=issued.raw, password="YangiParol!99")

        r = tasdiq(token=issued.raw, password="BoshqaParol!77")

        assert r.status_code == 400
        odam.refresh_from_db()
        assert odam.check_password("YangiParol!99"), "ikkinchi urinish parolni o'zgartirmasin"

    def test_yaroqsiz_token(self, odam: User) -> None:
        r = tasdiq(token="yoq-bunday-token", password="YangiParol!99")

        assert r.status_code == 400
        assert r.data["error"]["code"] == "invalid_token"

    def test_token_ham_kod_ham_bermasa(self, odam: User) -> None:
        r = tasdiq(password="YangiParol!99")

        assert r.status_code == 400

    def test_username_parol_sifatida_qabul_qilinmaydi(self, odam: User) -> None:
        """`validate_password` ga foydalanuvchi berilishi shart — usiz
        `UserAttributeSimilarityValidator` umuman ishlamaydi va tiklash
        ro'yxatdan o'tish validatorlarini chetlab o'tish yo'li bo'lardi."""
        issued = recovery.issue(odam)

        r = tasdiq(token=issued.raw, password="odam")

        assert r.status_code == 400
        odam.refresh_from_db()
        assert odam.check_password("Parol!12345"), "eski parol saqlanib qolsin"

    def test_qisqa_parol_qabul_qilinmaydi(self, odam: User) -> None:
        issued = recovery.issue(odam)

        r = tasdiq(token=issued.raw, password="qq1")

        assert r.status_code == 400

    def test_muvaffaqiyatsiz_tasdiq_tokenni_kuydirmaydi(self, odam: User) -> None:
        """Parol qoidaga to'g'ri kelmasa, foydalanuvchi qaytadan urinishi
        kerak — havolani qayta so'rashga majbur qilish shafqatsiz bo'lardi."""
        issued = recovery.issue(odam)
        tasdiq(token=issued.raw, password="qq1")

        r = tasdiq(token=issued.raw, password="YangiParol!99")

        assert r.status_code == 204
        odam.refresh_from_db()
        assert odam.check_password("YangiParol!99")
