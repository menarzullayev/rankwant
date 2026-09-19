"""Email zanjirini HAQIQIY provayderlarga tekshiradi.

Ishlatish:
    python manage.py send_test_email siz@example.com
    python manage.py send_test_email siz@example.com --only resend

Kalit qo'shilgandan keyin birinchi qilinadigan ish shu: payload yoki
jo'natuvchi domen noto'g'ri bo'lsa, provayderning o'z xato matni shu
yerda ko'rinadi. Zanjir jimgina ishlamay turishidan ko'ra shu yaxshi.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.mail_providers import PROVIDERS
from core.mailer import send_email
from core.models import EmailDelivery


class Command(BaseCommand):
    help = "Sozlangan provayderlar orqali sinov xati yuboradi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("to")
        parser.add_argument("--only", help="faqat shu provayder (zanjirni chetlab o'tadi)")

    def handle(self, *args: Any, **options: Any) -> None:
        chain = [options["only"]] if options["only"] else settings.EMAIL_CHAIN
        if options["only"] and options["only"] not in PROVIDERS:
            raise CommandError(f"unknown provider: {options['only']}")

        sozlangan = 0
        for name in chain:
            provider = PROVIDERS.get(name)
            mark = "✓" if provider and provider.configured else "—"
            sozlangan += mark == "✓"
            self.stdout.write(f"  {mark} {name}")
        if not sozlangan:
            # Yiqilish sababini aniq ayt: kalit yo'q — bu «yubora olmadi»
            # emas, «umuman urinmadi».
            raise CommandError("zanjirda sozlangan provayder yo'q — kalit qo'ying")

        delivery = send_email(
            to=options["to"],
            subject="RankWant — sinov xati",
            text="Zanjir ishlayapti. Bu xat send_test_email buyrug'idan.",
            purpose=EmailDelivery.Purpose.OTHER,
            chain=chain,
            # ⚠️ SHART: bu buyruq ataylab zaxira domenga yuboradi
            # (`siz@example.com` — hujjatda shunday yozilgan), chunki
            # maqsad — provayderning javobini ko'rish, xatni yetkazish
            # emas. `False` bo'lsa `send_email` bunday manzilni o'tkazib
            # yuborardi va buyruq hech narsani sinamay qo'yardi.
            allow_placeholder=True,
        )

        for attempt in delivery.attempts:
            self.stdout.write(self.style.WARNING(f"  ✗ {attempt['provider']}: {attempt['error']}"))
        if delivery.status == EmailDelivery.Status.SENT:
            self.stdout.write(self.style.SUCCESS(f"yuborildi — {delivery.provider}"))
        else:
            raise CommandError("hech bir provayder yubora olmadi")
