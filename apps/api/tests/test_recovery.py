"""Parolni tiklash tokeni — ADR-0015 dagi qoidalar.

Bu yerda xat ham, HTTP ham yo'q: `core.recovery` faqat tokenning hayotini
boshqaradi va uchala kanal (email, staff, keyinchalik Telegram) uni bir xil
ishlatadi. Qoidalarni shu qatlamda sinash — ularni bir joyda ushlab turish.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from core import recovery
from core.models import PasswordResetToken, User


@pytest.fixture
def odam(db) -> User:
    return User.objects.create_user(
        username="odam", email="odam@example.com", password="Parol!12345"
    )


@pytest.mark.django_db
class TestChiqarish:
    def test_havola_ham_kod_ham_beriladi(self, odam: User) -> None:
        issued = recovery.issue(odam, ip="1.2.3.4", user_agent="Chrome")

        assert len(issued.code) == 6 and issued.code.isdigit()
        assert len(issued.raw) > 20
        # Ochiq qiymat bazada YO'Q — faqat hash.
        assert issued.raw not in str(issued.row.token_hash)
        assert issued.code not in str(issued.row.code_hash)

    def test_kontekst_yoziladi(self, odam: User) -> None:
        """IP va brauzer xatda ko'rsatiladi (ADR-0015)."""
        issued = recovery.issue(odam, ip="9.9.9.9", user_agent="Firefox/1.0")

        assert issued.row.request_ip == "9.9.9.9"
        assert issued.row.request_ua == "Firefox/1.0"

    def test_yangi_token_eskisini_yopadi(self, odam: User) -> None:
        """Aks holda «yana yuboring» uch marta bosilgach uchta amaldagi
        havola qolardi va ikkitasi pochtada kutib turardi."""
        birinchi = recovery.issue(odam)

        recovery.issue(odam)

        assert recovery.consume(raw=birinchi.raw) is None


@pytest.mark.django_db
class TestChegara:
    def test_hisobga_soatiga_uchta(self, odam: User) -> None:
        for _ in range(PasswordResetToken.PER_USER_HOUR):
            recovery.issue(odam)

        with pytest.raises(recovery.TooManyRequests):
            recovery.issue(odam)

    def test_ip_chegarasi_hisobdan_kengroq(self, db) -> None:
        """Maktab sinfi bitta tashqi IP ortida bo'ladi — shuning uchun IP
        chegarasi hisob chegarasidan yuqori."""
        for i in range(PasswordResetToken.PER_IP_HOUR):
            u = User.objects.create_user(username=f"u{i}", password="Parol!12345")
            recovery.issue(u, ip="5.5.5.5")

        oxirgi = User.objects.create_user(username="oxirgi", password="Parol!12345")
        with pytest.raises(recovery.TooManyRequests):
            recovery.issue(oxirgi, ip="5.5.5.5")

    def test_staff_chegarani_yemaydi(self, odam: User) -> None:
        """Staff aynan chegaraga urilgan odamga yordam berish uchun chaqiriladi."""
        for _ in range(PasswordResetToken.PER_USER_HOUR):
            recovery.issue(odam)

        issued = recovery.issue(odam, enforce_limit=False)

        assert recovery.consume(raw=issued.raw) == odam

    def test_yopilgan_token_chegarada_qoladi(self, odam: User) -> None:
        """Eski tokenlar o'chirilmaydi, yopiladi — o'chirish cheklovni
        chetlab o'tish yo'li bo'lardi."""
        for _ in range(PasswordResetToken.PER_USER_HOUR):
            recovery.issue(odam)

        assert PasswordResetToken.objects.filter(user=odam).count() == 3
        with pytest.raises(recovery.TooManyRequests):
            recovery.issue(odam)


@pytest.mark.django_db
class TestIstemol:
    def test_havola_ishlaydi_va_bir_martalik(self, odam: User) -> None:
        issued = recovery.issue(odam)

        assert recovery.consume(raw=issued.raw) == odam
        assert recovery.consume(raw=issued.raw) is None

    def test_kod_ishlaydi_va_bir_martalik(self, odam: User) -> None:
        issued = recovery.issue(odam)

        assert recovery.consume(code=issued.code, username="odam") == odam
        assert recovery.consume(code=issued.code, username="odam") is None

    def test_kod_boshqa_odamga_tegishli_emas(self, odam: User) -> None:
        """6 xonali kod baza bo'ylab yagona emas — shuning uchun foydalanuvchi
        ham talab qilinadi."""
        boshqa = User.objects.create_user(username="boshqa", password="Parol!12345")
        issued = recovery.issue(odam)

        assert recovery.consume(code=issued.code, username=boshqa.username) is None

    def test_muddati_tugagan_token_ishlamaydi(self, odam: User) -> None:
        issued = recovery.issue(odam)
        PasswordResetToken.objects.filter(pk=issued.row.pk).update(
            expires_at=timezone.now() - timedelta(minutes=1)
        )

        assert recovery.consume(raw=issued.raw) is None

    def test_notogri_kod_urinishni_sanaydi(self, odam: User) -> None:
        issued = recovery.issue(odam)

        assert recovery.consume(code="000000", username="odam") is None
        issued.row.refresh_from_db()
        assert issued.row.attempts == 1
        # To'g'ri kod hali ishlaydi — bitta xato tokenni o'ldirmaydi.
        assert recovery.consume(code=issued.code, username="odam") == odam

    def test_urinishlar_tugasa_token_yopiladi(self, odam: User) -> None:
        """6 xonali kodni cheksiz sinash uni bir necha daqiqada topardi."""
        issued = recovery.issue(odam)

        for _ in range(PasswordResetToken.MAX_ATTEMPTS):
            recovery.consume(code="000000", username="odam")

        # Endi TO'G'RI kod ham ishlamaydi.
        assert recovery.consume(code=issued.code, username="odam") is None
        issued.row.refresh_from_db()
        assert issued.row.used_at is not None

    def test_bosh_sorov_hech_narsa_qaytarmaydi(self, odam: User) -> None:
        recovery.issue(odam)

        assert recovery.consume() is None
        assert recovery.consume(code="123456") is None
        assert recovery.consume(raw="") is None
