#!/usr/bin/env python3
"""Tekshiruvlarning O'ZLARINI sinaydi — salbiy testlar.

Nega kerak: bu loyihada «yashil, lekin yolg'on» natija bir kunda to'rt
marta uchradi. Har birining ildizi bir xil — tekshiruv **qiymatni o'qib
bo'lmay qolgan**, lekin baribir muvaffaqiyat qaytargan:

  * `pathlib.glob("**/*.{ts,tsx}")` — qavs kengaytmasini qo'llamaydi,
    glob bo'sh qaytdi, tekshiruv esa «to'liq ✓» dedi;
  * `parse("transparent")` → `None`, taqqoslash `None > 0.5` → `False`,
    ya'ni «muammo yo'q»;
  * `date -u -d ""` → exit 0;
  * `color(srgb .61 …)` kanallarini 0–255 deb o'qish → 6.91:1 o'rniga
    **1.12:1**.

Shuning uchun har bir tekshiruv uchun shu yerda **ataylab buzilgan
holat** yasaladi va tekshiruv `exit 1` qaytarishi TALAB qilinadi.
Tekshiruv buzuq holatni o'tkazib yuborsa — u o'lik, va bu skript
yiqiladi.

Ishlatish:
    python tools/check_negative.py          # hammasi
    python tools/check_negative.py contrast # bittasi
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


@dataclass
class Case:
    """Bitta salbiy test: buzilgan holatni yasash → tekshiruv yiqilishi."""

    name: str
    target: str
    """Qaysi tekshiruv: `i18n`, `contrast`, `docs`, `contract`."""

    describe: str
    """Buzilish nima qilingani — hisobotda ko'rinadi."""


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def run_check(checker: str, *extra: str) -> tuple[int, str]:
    return run([PY, f"tools/check_{checker}.py", *extra])


class Mutation:
    """Fayl matnini vaqtincha o'zgartiradi, chiqishda ASL holiga qaytaradi.

    `__enter__` paytida asl matn xotirada saqlanadi; `__exit__` da
    yoziladi. Xato bo'lsa ham tiklanishi shart — `finally` bilan.
    """

    def __init__(self, path: Path, old: str, new: str) -> None:
        self.path = path
        self.old = old
        self.new = new
        self.original: str | None = None

    def __enter__(self) -> "Mutation":
        self.original = self.path.read_text(encoding="utf-8")
        if self.old not in self.original:
            raise AssertionError(
                f"salbiy test yasalmadi: {self.old!r} {self.path.name} da topilmadi"
            )
        self.path.write_text(self.original.replace(self.old, self.new, 1), encoding="utf-8")
        return self

    def __exit__(self, *_exc: object) -> None:
        assert self.original is not None
        self.path.write_text(self.original, encoding="utf-8")


def expect_fail(checker: str, label: str) -> tuple[bool, str]:
    """Tekshiruv `exit 1` berishini talab qiladi."""
    code, out = run_check(checker)
    if code == 0:
        return False, f"{label}: tekshiruv buzuq holatni O'TKAZDI (exit 0) — u o'lik"
    return True, f"{label}: buzuq holatni tutdi (exit {code})"


# ── i18n ─────────────────────────────────────────────────────────────────


def neg_i18n_blank_value() -> tuple[bool, str]:
    """Bitta tarjima bo'sh qolsa — tutilsinmi?"""
    path = ROOT / "apps/web/src/i18n/locales/zh.ts"
    text = path.read_text(encoding="utf-8")
    m = re.search(r'^(\s*)((?:"([a-zA-Z0-9_.]+)"|([A-Za-z_$][\w$]*))):\s*"((?:[^"\\]|\\.)*)",\s*$', text, re.M)
    if m is None:
        return False, "i18n/bo'sh: sinov uchun kalit topilmadi"
    indent, key, quoted, _bare, value = m.groups()
    old = f'{indent}{key}: "{value}",'
    new = f'{indent}{key}: "",'
    with Mutation(path, old, new):
        return expect_fail("i18n", "i18n/bo'sh qiymat")


def neg_i18n_missing_key() -> tuple[bool, str]:
    """Bitta kalit butunlay o'chirilsa — tutilsinmi?"""
    path = ROOT / "apps/web/src/i18n/locales/kk.ts"
    text = path.read_text(encoding="utf-8")
    m = re.search(r'^\s*(?:"[a-zA-Z0-9_.]+"|[A-Za-z_$][\w$]*):\s*"(?:[^"\\]|\\.)*",\s*$', text, re.M)
    if m is None:
        return False, "i18n/yetishmaydi: sinov uchun kalit topilmadi"
    with Mutation(path, m.group(0) + "\n", ""):
        return expect_fail("i18n", "i18n/yetishmayotgan kalit")


def neg_i18n_used_but_absent() -> tuple[bool, str]:
    """Kodda chaqirilgan kalit manbada bo'lmasa — tutilsinmi?

    Aynan shu bo'shliq panelni xom kalit bilan qoldirgan edi.
    """
    path = ROOT / "apps/web/src/layout/LocaleSwitch.tsx"
    text = path.read_text(encoding="utf-8")
    marker = "export function LocaleSwitch() {"
    if marker not in text:
        return False, "i18n/ishlatilgan: marker topilmadi"
    injected = text.replace(
        marker,
        marker
        + '\n  // negative test — key deliberately absent from every dictionary\n'
        + '  const __negativeProbe = t(locale, "negative.test.missing");\n'
        + '  void __negativeProbe;',
        1,
    )
    with Mutation(path, text, injected):
        return expect_fail("i18n", "i18n/kodda chaqirilgan, manbada yo'q")


# ── contrast ─────────────────────────────────────────────────────────────


def neg_contrast_bad_pair() -> tuple[bool, str]:
    """Bitta juftlik yetarli kontrast bermasa — tutilsinmi?"""
    path = ROOT / "apps/web/src/app/globals.css"
    text = path.read_text(encoding="utf-8")
    # `--rw-warn-ink` ni fon bilan bir xil qilib qo'yamiz: 1:1.
    m = re.search(r"(--rw-warn-ink:\s*)([^;]+)(;)", text)
    if m is None:
        return False, "contrast: `--rw-warn-ink` topilmadi"
    with Mutation(path, m.group(0), f"{m.group(1)}#ffffff{m.group(3)}"):
        return expect_fail("contrast", "contrast/buzilgan juftlik")


def neg_contrast_unreadable_token() -> tuple[bool, str]:
    """Token o'qib bo'lmaydigan qiymat olsa — XATO bo'lsinmi?

    «O'qib bo'lmagan qiymat = XATO» qoidasi shundan. Ilgari bunday
    qiymat jimgina o'tkazib yuborilardi.
    """
    path = ROOT / "apps/web/src/app/globals.css"
    text = path.read_text(encoding="utf-8")
    m = re.search(r"(--rw-ground:\s*)([^;]+)(;)", text)
    if m is None:
        return False, "contrast: `--rw-ground` topilmadi"
    with Mutation(path, m.group(0), f"{m.group(1)}oklch(TEST{m.group(3)}"):
        return expect_fail("contrast", "contrast/o'qib bo'lmaydigan qiymat")


# ── docs / contract ──────────────────────────────────────────────────────


def neg_docs_broken_link() -> tuple[bool, str]:
    """Hujjatda mavjud bo'lmagan havola — tutilsinmi?"""
    candidates = sorted((ROOT / "docs").glob("*.md"))
    if not candidates:
        return False, "docs: tekshirish uchun hujjat topilmadi"
    path = candidates[0]
    text = path.read_text(encoding="utf-8")
    marker = text.rstrip() + "\n\n[negative test](./this-file-does-not-exist-42.md)\n"
    original = path.read_text(encoding="utf-8")
    path.write_text(marker, encoding="utf-8")
    try:
        return expect_fail("docs", "docs/buzilgan havola")
    finally:
        path.write_text(original, encoding="utf-8")


def neg_email_missing_locale() -> tuple[bool, str]:
    """Bitta satrdan bitta til olib tashlansa — tutilsinmi?

    Ilgari til jimgina `uz` ga tushardi; bu tekshiruv o'sha holatni CI da
    to'xtatadi.
    """
    path = ROOT / "apps/api/core/email_text.py"
    old = '        "es": "RankWant — restablecer contraseña",'
    if old not in path.read_text(encoding="utf-8"):
        return False, "email/til: sinov uchun qator topilmadi"
    with Mutation(path, old + "\n", ""):
        return expect_fail("email_locales", "email/yetishmayotgan til")


def neg_email_blank_value() -> tuple[bool, str]:
    """Bitta matn bo'sh qolsa — tutilsinmi?"""
    path = ROOT / "apps/api/core/email_text.py"
    old = "        \"en\": \"Sign in\","
    new = "        \"en\": \"   \","
    if old not in path.read_text(encoding="utf-8"):
        return False, "email/bo'sh: sinov uchun qator topilmadi"
    with Mutation(path, old, new):
        return expect_fail("email_locales", "email/bo'sh matn")


def neg_email_undeclared_locale() -> tuple[bool, str]:
    """Ro'yxatda yo'q til qo'shilsa — tutilsinmi?"""
    path = ROOT / "apps/api/core/email_text.py"
    old = '        "es": "RankWant",'
    new = '        "es": "RankWant",\n        "xx": "RankWant",'
    if old not in path.read_text(encoding="utf-8"):
        return False, "email/e'lon qilinmagan: sinov uchun qator topilmadi"
    with Mutation(path, old, new):
        return expect_fail("email_locales", "email/ro'yxatda yo'q til")


# ── locales parity ───────────────────────────────────────────────────────


def neg_parity_missing_locale() -> tuple[bool, str]:
    """`LANGUAGES` dan bitta til olib tashlansa — tutilsinmi?

    Bu AYnan ilgari bo'lgan holat: `LANGUAGES` 3 ta edi, `User.Locale`
    esa 10 ta. Brauzeri `ky` bo'lgan odam jimgina `uz` ko'rardi.
    """
    path = ROOT / "apps/api/config/settings.py"
    old = '    ("ky", "Кыргызча"),\n'
    if old not in path.read_text(encoding="utf-8"):
        return False, "parity/yetishmaydi: sinov uchun qator topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("locales_parity", "parity/LANGUAGES da til yetishmaydi")


def neg_parity_extra_locale() -> tuple[bool, str]:
    """`LOCALES` ga `User.Locale` da yo'q til qo'shilsa — tutilsinmi?"""
    path = ROOT / "apps/api/core/email_text.py"
    old = '"zh", "es")'
    new = '"zh", "es", "xx")'
    if old not in path.read_text(encoding="utf-8"):
        return False, "parity/ortiqcha: sinov uchun qator topilmadi"
    with Mutation(path, old, new):
        return expect_fail("locales_parity", "parity/LOCALES da ortiqcha til")


def neg_i18n_template_family() -> tuple[bool, str]:
    """Shablon oilaning BARCHA kaliti o'chirilsa — tutilsinmi?

    13-band: `t(locale, `customizer.template.${id}`)` — shablon kalit.
    Birortasi yo'q bo'lsa foydalanuvchi xom kalit ko'radi, `CALL_RE`
    esa buni ko'rmaydi (shablon statik emas).
    """
    path = ROOT / "apps/web/src/i18n/locales/uz.ts"
    text = path.read_text(encoding="utf-8")
    removed = 0
    lines = []
    for line in text.split("\n"):
        if re.match(r'^\s*"customizer\.template\.', line):
            removed += 1
            continue
        lines.append(line)
    if removed == 0:
        return False, "i18n/shablon: `customizer.template.*` topilmadi"
    with Mutation(path, text, "\n".join(lines)):
        return expect_fail("i18n", "i18n/shablon oila kalitisiz")


def neg_i18n_server_drops_locales() -> tuple[bool, str]:
    """Server `evict` bersa — tutilsinmi?

    Aynan shu nuqson bo'lgan: `messages.server.ts` dagi tsikl o'nta
    tilni ro'yxatga oladi, lekin chegaralash faqat OXIRGISINI
    qoldirardi → SSR'da o'nlab xom kalit (o'lchandi, brauzerda).
    """
    path = ROOT / "apps/web/src/i18n/messages.server.ts"
    old = "registerMessages(locale as Locale, dict);"
    new = "registerMessages(locale as Locale, dict, true);"
    if old not in path.read_text(encoding="utf-8"):
        return False, "i18n/server evict: langar topilmadi"
    with Mutation(path, old, new):
        return expect_fail("i18n", "i18n/server evict bilan chegaralangan")


def neg_i18n_server_missing_locale() -> tuple[bool, str]:
    """`ALL` dan bitta til olib tashlansa — tutilsinmi?"""
    path = ROOT / "apps/web/src/i18n/messages.server.ts"
    old = "  tg,\n"
    if old not in path.read_text(encoding="utf-8"):
        return False, "i18n/server yetishmaydi: langar topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("i18n", "i18n/server lug'atda til yetishmaydi")


CASES: list[tuple[str, list[tuple[str, object]]]] = [
    ("i18n", [
        ("bo'sh qiymat", neg_i18n_blank_value),
        ("yetishmayotgan kalit", neg_i18n_missing_key),
        ("kodda bor, manbada yo'q", neg_i18n_used_but_absent),
        ("shablon oila kalitisiz", neg_i18n_template_family),
        ("server evict bilan chegaralangan", neg_i18n_server_drops_locales),
        ("server lug'atda til yetishmaydi", neg_i18n_server_missing_locale),
    ]),
    ("contrast", [
        ("buzilgan juftlik", neg_contrast_bad_pair),
        ("o'qib bo'lmaydigan qiymat", neg_contrast_unreadable_token),
    ]),
    ("docs", [
        ("buzilgan havola", neg_docs_broken_link),
    ]),
    ("email_locales", [
        ("yetishmayotgan til", neg_email_missing_locale),
        ("bo'sh matn", neg_email_blank_value),
        ("ro'yxatda yo'q til", neg_email_undeclared_locale),
    ]),
    ("locales_parity", [
        ("LANGUAGES da til yetishmaydi", neg_parity_missing_locale),
        ("LOCALES da ortiqcha til", neg_parity_extra_locale),
    ]),
]


def main(argv: list[str]) -> int:
    only = argv[1] if len(argv) > 1 else None
    failures: list[str] = []
    total = 0

    for checker, cases in CASES:
        if only and only != checker:
            continue
        for label, fn in cases:
            total += 1
            try:
                ok, message = fn()  # type: ignore[operator]
            except AssertionError as exc:
                ok, message = False, f"{checker}/{label}: {exc}"
            except Exception as exc:  # noqa: BLE001 — sinov yiqilishini hisobotga aylantiramiz
                ok, message = False, f"{checker}/{label}: kutilmagan xato — {exc!r}"
            print(f"  {'✓' if ok else '✕'} {message}")
            if not ok:
                failures.append(message)

    print()
    if failures:
        print(f"{len(failures)}/{total} salbiy test YIQILDI — tekshiruv o'lik bo'lishi mumkin:")
        for row in failures:
            print(f"  - {row}")
        return 1
    print(f"Salbiy testlar: {total}/{total} ✓ — har bir tekshiruv buzuq holatni tutdi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
