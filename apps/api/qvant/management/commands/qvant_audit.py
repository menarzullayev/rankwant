"""Hamyon keshi ledgerga mos keladimi — hammasi bo'yicha.

Ishlatish:
    python manage.py qvant_audit
    python manage.py qvant_audit --fix

ADR-0002: haqiqat manbai — `QvantTransaction` ledgeri, `QvantWallet.balance`
esa kesh. `verify_balance()` bitta foydalanuvchini tekshiradi; 10 000
hamyonda esa farqni umuman payqamaslik mumkin. Bu buyruq butun bazani
ikki so'rovda ko'rib chiqadi.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Sum

from qvant.models import QvantTransaction, QvantWallet


class Command(BaseCommand):
    help = "Qvant hamyonlari ledgerga mos kelishini tekshiradi."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Keshni ledgerdan qayta yozadi. Ledger — haqiqat manbai.",
        )
        parser.add_argument("--limit", type=int, default=20, help="Nechtasi ko'rsatilsin")

    def handle(self, *args: Any, **options: Any) -> None:
        # So'rov soni hamyon soniga bog'liq emas.
        ledger = dict(
            QvantTransaction.objects.values("user_id")
            .annotate(total=Sum("amount"))
            .values_list("user_id", "total")
        )
        drifted = [
            (wallet, ledger.get(wallet.user_id, 0))
            for wallet in QvantWallet.objects.only("pk", "user_id", "balance")
            if wallet.balance != ledger.get(wallet.user_id, 0)
        ]

        total = QvantWallet.objects.count()
        if not drifted:
            self.stdout.write(self.style.SUCCESS(f"{total} hamyon — hammasi mos"))
            return

        self.stdout.write(f"{total} hamyondan {len(drifted)} tasida farq bor:")
        for wallet, expected in drifted[: options["limit"]]:
            self.stdout.write(
                f"  user={wallet.user_id:<8} kesh={wallet.balance:<8} ledger={expected}"
            )
        if len(drifted) > options["limit"]:
            self.stdout.write(f"  … yana {len(drifted) - options['limit']} ta")

        if not options["fix"]:
            self.stdout.write(self.style.WARNING("Tuzatish uchun: --fix"))
            return

        for wallet, expected in drifted:
            wallet.balance = expected
        QvantWallet.objects.bulk_update(
            [w for w, _ in drifted], ["balance", "updated_at"], batch_size=500
        )
        self.stdout.write(self.style.SUCCESS(f"{len(drifted)} hamyon ledgerdan tiklandi"))
