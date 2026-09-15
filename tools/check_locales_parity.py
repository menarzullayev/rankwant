#!/usr/bin/env python3
"""Uchta til ro'yxati bir xil bo'lishini tekshiradi.

Nega kerak: til kodlari loyihada UCH joyda takrorlanadi va ular
jimgina ajralib ketishi mumkin:

  1. `core/models.py`  -> `User.Locale`        — hisobning saqlangan tili
  2. `config/settings.py` -> `LANGUAGES`       — `LocaleMiddleware`
                                                  `Accept-Language` ni shu
                                                  ro'yxat bo'yicha hal qiladi
  3. `core/email_text.py` -> `LOCALES`         — xat matnlari

Ro'yxatlar ajralsa xato KO'RINMAYDI: `LANGUAGES` da yo'q til jimgina
`LANGUAGE_CODE` ga tushadi, ya'ni brauzeri `ky` bo'lgan odam o'zbekcha
interfeys ko'radi va hech qanday xato yozilmaydi. (Aynan shunday bo'lgan:
`LANGUAGES` 3 ta edi, `User.Locale` esa 10 ta — o'lchandi.)

Bu skript barcha uchtasini AST orqali o'qib, to'plamlarni solishtiradi.

Ishlatish:
    python tools/check_locales_parity.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# Chiqish quvurga yo'naltirilganda Windows uni `cp1252` deb yozadi va
# birinchi `✓` belgisida qulaydi — sabab va o'lchov `tools/_console.py` da.
import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent

MODELS = ROOT / "apps/api/core/models.py"
SETTINGS = ROOT / "apps/api/config/settings.py"
EMAIL_TEXT = ROOT / "apps/api/core/email_text.py"


class Source:
    """Bitta fayldan til kodlari ro'yxatini AST orqali oladi."""

    def __init__(self, path: Path, description: str) -> None:
        self.path = path
        self.description = description

    def parse(self) -> ast.Module:
        if not self.path.exists():
            sys.exit(f"{self.description}: fayl topilmadi — {self.path}")
        return ast.parse(self.path.read_text(encoding="utf-8"))

    def read(self) -> list[str]:
        raise NotImplementedError


class EnumSource(Source):
    """`class <owner>: class <name>(TextChoices)` ichidagi kalitlar."""

    def __init__(self, path: Path, description: str, owner: str, name: str) -> None:
        super().__init__(path, description)
        self.owner = owner
        self.name = name

    def read(self) -> list[str]:
        for node in self.parse().body:
            if isinstance(node, ast.ClassDef) and node.name == self.owner:
                for inner in node.body:
                    if isinstance(inner, ast.ClassDef) and inner.name == self.name:
                        return self._members(inner)
        raise LookupError(f"{self.description}: {self.owner}.{self.name} topilmadi")

    @staticmethod
    def _members(cls: ast.ClassDef) -> list[str]:
        """`UZ = "uz", "O'zbekcha"` — juftlikning birinchi elementi kod."""
        codes: list[str] = []
        for stmt in cls.body:
            if not isinstance(stmt, ast.Assign):
                continue
            # `TextChoices` a'zosi doim juftlik: (kod, nom).
            value = stmt.value
            first: ast.expr | None = None
            if isinstance(value, ast.Tuple) and value.elts:
                first = value.elts[0]
            elif isinstance(value, ast.Constant):
                first = value
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                codes.append(first.value)
        return codes


class SequenceSource(Source):
    """Modul darajasidagi `<NAME>` — tuple yoki list, satrlardan iborat."""

    def __init__(self, path: Path, description: str, name: str) -> None:
        super().__init__(path, description)
        self.name = name

    def read(self) -> list[str]:
        for node in self.parse().body:
            target: ast.expr | None = None
            value: ast.expr | None = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target, value = node.targets[0], node.value
            elif isinstance(node, ast.AnnAssign):
                target, value = node.target, node.value

            if isinstance(target, ast.Name) and target.id == self.name:
                if isinstance(value, (ast.Tuple, ast.List)):
                    return [
                        elt.value
                        for elt in value.elts
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                    ]
                # `LANGUAGES` — (kod, nom) juftliklari. U `PairsSource` da
                # alohida qayta ishlanadi; bu yerda faqat satr ro'yxati
                # kutiladi. Ilgari shu yerda bir xil shartli bo'sh `if`
                # turardi — u yetib bo'lmaydigan edi (yuqoridagi shart
                # ro'yxatni allaqachon qaytaradi), ya'ni o'lik kod.
        raise LookupError(f"{self.description}: {self.name} topilmadi")


class PairsSource(SequenceSource):
    """`LANGUAGES = [("uz", "O'zbekcha"), ...]` — juftliklarning 1-elementi."""

    def read(self) -> list[str]:
        for node in self.parse().body:
            target: ast.expr | None = None
            value: ast.expr | None = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target, value = node.targets[0], node.value
            elif isinstance(node, ast.AnnAssign):
                target, value = node.target, node.value

            if isinstance(target, ast.Name) and target.id == self.name:
                if isinstance(value, (ast.Tuple, ast.List)):
                    codes: list[str] = []
                    for elt in value.elts:
                        if isinstance(elt, (ast.Tuple, ast.List)) and elt.elts:
                            first = elt.elts[0]
                            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                                codes.append(first.value)
                    return codes
        raise LookupError(f"{self.description}: {self.name} topilmadi")


def main() -> int:
    sources: list[Source] = [
        EnumSource(MODELS, "User.Locale", owner="User", name="Locale"),
        PairsSource(SETTINGS, "settings.LANGUAGES", name="LANGUAGES"),
        SequenceSource(EMAIL_TEXT, "email_text.LOCALES", name="LOCALES"),
    ]

    found: dict[str, list[str]] = {}
    for source in sources:
        try:
            found[source.description] = source.read()
        except LookupError as exc:
            print(f"✗ {exc}", file=sys.stderr)
            return 1

    for name, codes in found.items():
        if not codes:
            print(f"✗ {name}: ro'yxat bo'sh — o'qib bo'lmadi", file=sys.stderr)
            return 1
        if len(set(codes)) != len(codes):
            duplicates = sorted({c for c in codes if codes.count(c) > 1})
            print(f"✗ {name}: takroriy kod — {duplicates}", file=sys.stderr)
            return 1

    reference = "User.Locale"
    expected = set(found[reference])
    failed = False

    for name, codes in found.items():
        if name == reference:
            continue
        actual = set(codes)
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing or extra:
            failed = True
            print(f"✗ {name} {reference} bilan mos emas", file=sys.stderr)
            if missing:
                print(f"    yetishmaydi: {', '.join(missing)}", file=sys.stderr)
            if extra:
                print(f"    ortiqcha:    {', '.join(extra)}", file=sys.stderr)

    if failed:
        return 1

    print(f"{len(expected)} til × 3 ro'yxat — mos ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
