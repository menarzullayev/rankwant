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

CI'da bu to'plam `.github/workflows/ci.yml` dagi `web` job'ining «Salbiy
testlar» qadami sifatida ishlaydi. Job `apps/web/**` YOKI `tools/**` /
`.githooks/**` o'zgarganda ko'tariladi — ikkinchisi SHART, chunki bu
to'plam aynan o'sha fayllardagi tekshiruvlarni sinaydi.

⚠️ 2026-09-15 gacha darvoza faqat `apps/web/**` ga bog'langan edi va
oqibati o'lchandi: faqat `tools/` ni o'zgartirgan PR'lar — jumladan shu
faylning o'zini qayta yozgani va unga yangi guruh qo'shgani — job'ni
`skipped` qoldirdi. Ya'ni tekshiruvlarni sinaydigan to'plam aynan o'sha
tekshiruvlar o'zgarganda ishlamagan.
"""

from __future__ import annotations

import contextlib
import gzip
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from xml.dom import minidom

# Chiqish quvurga yo'naltirilganda Windows uni `cp1252` deb yozadi va
# birinchi `✓` belgisida qulaydi — sabab va o'lchov `tools/_console.py` da.
import _console

_console.force_utf8()

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
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def run_check(checker: str, *extra: str) -> tuple[int, str]:
    return run([PY, f"tools/check_{checker}.py", *extra])


NODE_MISSING = "node topilmadi"

NODE_CASES = {"runtime dev throw yo'q", "runtime takroriy jurnal"}
"""Node'da ishlaydigan tekshiruvga tegishli salbiy testlarning yorlig'i."""


def run_node_check(checker: str) -> tuple[int, str]:
    """`*.mjs` tekshiruvlar uchun runner.

    ⚠️ `node` ni PATH'dan emas, `tools/ci-local.sh` bilan bir xil
    qoidada olamiz: muhit `NODE` bilan berilishi mumkin (raw runner'da
    `node` bo'lmasligi mumkin — Windows o'rnatuvchisida u
    `C:/Program Files/nodejs/node.exe`).
    """
    node = os.environ.get("NODE") or shutil.which("node")
    if not node:
        return 127, NODE_MISSING
    return run([node, f"tools/{checker}.mjs"])


class Mutation:
    """Fayl matnini vaqtincha o'zgartiradi, chiqishda ASL holiga qaytaradi.

    `__enter__` paytida asl matn xotirada saqlanadi; `__exit__` da
    yoziladi. Xato bo'lsa ham tiklanishi shart — `finally` bilan.

    ⚠️ O'qish ham, yozish ham BAYT darajasida. `read_text`/`write_text`
    matn rejimida ishlaydi va satr oxirlarini TARJIMA qiladi: o'qishda
    `\\r\\n` → `\\n`, yozishda esa `\\n` → `os.linesep`. Windows'da bu
    shuni anglatadiki, LF bilan yozilgan fayl mutatsiyadan keyin CRLF
    bo'lib qaytariladi — mazmuni bir xil, baytlari boshqa.

    2026-09-15 da o'lchandi: bitta salbiy test yurishidan keyin `git
    status` 19 ta begona faylni «o'zgargan» deb ko'rsatdi (`settings.py`,
    `uz.ts`, `docs/README.md` …). Ular o'zgarmagan edi — faqat satr
    oxirlari almashgan. Bayt darajasidagi qaytarish buni butunlay
    yo'q qiladi.
    """

    def __init__(self, path: Path, old: str, new: str) -> None:
        self.path = path
        self.old = old
        self.new = new
        self.original: str | None = None

    def __enter__(self) -> "Mutation":
        self.original = self.path.read_bytes().decode("utf-8")
        if self.old not in self.original:
            raise AssertionError(
                f"salbiy test yasalmadi: {self.old!r} {self.path.name} da topilmadi"
            )
        self.path.write_bytes(
            self.original.replace(self.old, self.new, 1).encode("utf-8")
        )
        return self

    def __exit__(self, *_exc: object) -> None:
        assert self.original is not None
        self.path.write_bytes(self.original.encode("utf-8"))


def expect_fail(checker: str, label: str) -> tuple[bool, str]:
    """Tekshiruv `exit 1` berishini talab qiladi."""
    code, out = run_check(checker)
    if code == 0:
        return False, f"{label}: tekshiruv buzuq holatni O'TKAZDI (exit 0) — u o'lik"
    return True, f"{label}: buzuq holatni tutdi (exit {code})"


def expect_node_fail(label: str) -> tuple[bool, str]:
    """Node'da ishlaydigan tekshiruv uchun xuddi shu talab.

    Faqat mutatsiyadan KEYINGI holatga qaraydi. «Tekshiruv umuman
    ishlay oladimi?» degan old shart `main()` da BIR MARTA
    tekshiriladi (`node_precondition`) — aks holda `node` topilmasa
    `exit != 0` ni «buzuq holatni tutdi» deb o'qib, yolg'on yashil
    chiqardi. Bu tuzoq o'lchandi.
    """
    code, _ = run_node_check("check_i18n_runtime")
    if code == 0:
        return False, f"{label}: tekshiruv buzuq holatni O'TKAZDI (exit 0) — u o'lik"
    return True, f"{label}: buzuq holatni tutdi (exit {code})"


def node_precondition() -> str | None:
    """Node tekshiruvi o'zgarmagan manbada `exit 0` berishini talab qiladi.

    `None` — hammasi joyida. Aks holda sabab qaytariladi.
    """
    code, out = run_node_check("check_i18n_runtime")
    if code == 127:
        return f"node tekshiruvi ishga tushmadi — {NODE_MISSING}"
    if code != 0:
        first = out.strip().splitlines()[:3]
        return (
            "node tekshiruvi o'zgarmagan manbada ham yiqildi "
            f"(exit {code}): {' | '.join(first)}"
        )
    return None


# ── i18n ─────────────────────────────────────────────────────────────────


def neg_i18n_blank_value() -> tuple[bool, str]:
    """Bitta tarjima bo'sh qolsa — tutilsinmi?"""
    path = ROOT / "apps/web/src/i18n/locales/zh.ts"
    text = path.read_bytes().decode("utf-8")
    m = re.search(
        r'^(\s*)((?:"([a-zA-Z0-9_.]+)"|([A-Za-z_$][\w$]*))):\s*"((?:[^"\\]|\\.)*)",\s*$',
        text,
        re.M,
    )
    if m is None:
        return False, "i18n/bo'sh: sinov uchun kalit topilmadi"
    indent, key, quoted, _bare, value = m.groups()
    old = f'{indent}{key}: "{value}",'
    new = f'{indent}{key}: "",'
    with Mutation(path, old, new):
        return expect_fail("i18n", "i18n/bo'sh qiymat")


def neg_i18n_consent_link_dropped() -> tuple[bool, str]:
    """Rozilik matnidan `{terms}` tushib qolsa — tutilsinmi?

    Tarjimon o'rin egallovchini olib tashlasa jumla o'qiladi, lekin havola
    yo'qoladi va odam nimaga rozilik berayotganini ocholmaydi.
    """
    path = ROOT / "apps/web/src/i18n/locales/zh.ts"
    text = path.read_bytes().decode("utf-8")
    m = re.search(r'^\s*"auth\.termsAccept": "(.*)",\s*$', text, re.M)
    if m is None or "{terms}" not in m.group(1):
        return False, "i18n/rozilik havolasi: `auth.termsAccept` da `{terms}` topilmadi"
    old = m.group(0)
    new = old.replace("{terms}", "服务条款")
    with Mutation(path, old, new):
        return expect_fail("i18n", "i18n/rozilik havolasi")


def neg_i18n_missing_key() -> tuple[bool, str]:
    """Bitta kalit butunlay o'chirilsa — tutilsinmi?"""
    path = ROOT / "apps/web/src/i18n/locales/kk.ts"
    text = path.read_bytes().decode("utf-8")
    m = re.search(
        r'^\s*(?:"[a-zA-Z0-9_.]+"|[A-Za-z_$][\w$]*):\s*"(?:[^"\\]|\\.)*",\s*$',
        text,
        re.M,
    )
    if m is None:
        return False, "i18n/yetishmaydi: sinov uchun kalit topilmadi"
    with Mutation(path, m.group(0) + "\n", ""):
        return expect_fail("i18n", "i18n/yetishmayotgan kalit")


def neg_i18n_used_but_absent() -> tuple[bool, str]:
    """Kodda chaqirilgan kalit manbada bo'lmasa — tutilsinmi?

    Aynan shu bo'shliq panelni xom kalit bilan qoldirgan edi.
    """
    path = ROOT / "apps/web/src/layout/LocaleSwitch.tsx"
    text = path.read_bytes().decode("utf-8")
    marker = "export function LocaleSwitch() {"
    if marker not in text:
        return False, "i18n/ishlatilgan: marker topilmadi"
    injected = text.replace(
        marker,
        marker
        + "\n  // negative test — key deliberately absent from every dictionary\n"
        + '  const __negativeProbe = t(locale, "negative.test.missing");\n'
        + "  void __negativeProbe;",
        1,
    )
    with Mutation(path, text, injected):
        return expect_fail("i18n", "i18n/kodda chaqirilgan, manbada yo'q")


# ── contrast ─────────────────────────────────────────────────────────────


def neg_contrast_bad_pair() -> tuple[bool, str]:
    """Bitta juftlik yetarli kontrast bermasa — tutilsinmi?"""
    path = ROOT / "apps/web/src/app/globals.css"
    text = path.read_bytes().decode("utf-8")
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
    text = path.read_bytes().decode("utf-8")
    m = re.search(r"(--rw-ground:\s*)([^;]+)(;)", text)
    if m is None:
        return False, "contrast: `--rw-ground` topilmadi"
    with Mutation(path, m.group(0), f"{m.group(1)}oklch(TEST{m.group(3)}"):
        return expect_fail("contrast", "contrast/o'qib bo'lmaydigan qiymat")


# ── docs / contract ──────────────────────────────────────────────────────


def neg_docs_missing_adr() -> tuple[bool, str]:
    """Mavjud bo'lmagan `ADR-NNNN` ga havola — tutilsinmi?

    ⚠️ Aynan shu sinf bir marta o'tkazib yuborilgan: `legal.ts` izohi
    `ADR-0016` ga ishora qilardi, u esa boshqa qaror haqida. Havola
    mavjud faylga ishora qilgani uchun uni oddiy havola tekshiruvi
    ko'rmaydi — shuning uchun raqam bo'yicha alohida qoida kerak.
    """
    adr = ROOT / "docs/07-adr/0001-brand-rankwant-qvant.md"
    if not adr.exists():
        return False, "docs/adr: `0001` fayli topilmadi"
    text = adr.read_bytes().decode("utf-8")
    # Marker BO'LAKLAB yig'iladi: qoida `.py` fayllarni ham skanerlaydi, shu
    # faylning o'zi esa manba kodi — to'liq yozilsa qoida O'Z testini tutib,
    # `check_docs.py` doim qizil bo'lib qolardi (bir marta shunday bo'ldi).
    marker = "ADR-" + "9999"
    if marker in text:
        return False, f"docs/adr: `{marker}` allaqachon matnda bor"
    with Mutation(adr, text, text.rstrip() + f"\n\nKo'rsatma: {marker}\n"):
        return expect_fail("docs", "docs/mavjud bo'lmagan ADR havolasi")


def neg_confusable_cyrillic_identifier() -> tuple[bool, str]:
    """Identifikatordagi kirill harf — tutilsinmi?

    2026-09-18 da topilgan haqiqiy holat: test nomida `са` kirill edi,
    ko'rinishi lotin `sa` bilan bir xil. `git grep` ham, IDE ham topa
    olmaydi, pytest chiqishida esa lotinchaga o'xshab ko'rinadi.
    """
    path = ROOT / "apps/api/tests/test_warn_email_quota.py"
    if not path.exists():
        return False, "confusables: namunali fayl topilmadi"
    with Mutation(
        path,
        "def test_bir_kunda_ikki_marta_yursa_ham_bitta_yozuv",
        # lotin `sa` o'rniga kirill `са` (U+0441 U+0430)
        "def test_bir_kunda_ikki_marta_yur\u0441\u0430_ham_bitta_yozuv",
    ):
        return expect_fail("confusables", "confusables/identifikatorda kirill")


def neg_confusable_formula_allowed() -> tuple[bool, str]:
    """Matn ichidagi grek harf XATO BERMASLIGI kerak.

    Tekshiruv butun qatorni olsa, qiymat ichidagi matematik belgi yolg'on
    xato beradi — o'lchandi: `const FORMULA_SKILLS = "Skills = Σ pᵢ × …"`.
    Ya'ni bu salbiy test tekshiruvning QAMROVINI qulflaydi: u faqat
    e'lon qilinayotgan nomga qaraydi, matnga emas.
    """
    path = ROOT / "apps/web/src/app/rating/page.tsx"
    if not path.exists():
        return False, "confusables: rating/page.tsx topilmadi"
    original = path.read_bytes()
    text = original.decode("utf-8")
    if 'const FORMULA_SKILLS = "Skills = \u03a3' not in text:
        return False, "confusables: grek harfli namuna topilmadi"
    # Fayl allaqachon grek harfli matn tutadi — ya'ni hozirgi holat
    # «yashil» bo'lishi shart. Bu oldini tekshiradi.
    code, _ = run_check("confusables")
    if code != 0:
        return False, "confusables: matematik matn yolg'on xato berdi (exit != 0)"
    return True, "confusables/matndagi grek harf xato bermadi"


def neg_docs_broken_link() -> tuple[bool, str]:
    """Hujjatda mavjud bo'lmagan havola — tutilsinmi?"""
    candidates = sorted((ROOT / "docs").glob("*.md"))
    if not candidates:
        return False, "docs: tekshirish uchun hujjat topilmadi"
    path = candidates[0]
    # Bayt darajasida — sabab `Mutation` docstring'ida.
    original = path.read_bytes()
    text = original.decode("utf-8")
    marker = text.rstrip() + "\n\n[negative test](./this-file-does-not-exist-42.md)\n"
    path.write_bytes(marker.encode("utf-8"))
    try:
        return expect_fail("docs", "docs/buzilgan havola")
    finally:
        path.write_bytes(original)


def neg_docs_research_link_still_checked() -> tuple[bool, str]:
    """The `docs/research/` exemption must not switch off link checking."""
    path = ROOT / "docs/research/README.md"
    if not path.exists():
        return False, "docs/research: README.md topilmadi"
    text = path.read_bytes().decode("utf-8")
    broken = text.rstrip() + "\n\n[negative test](./this-record-does-not-exist-42.md)\n"
    with Mutation(path, text, broken):
        code, out = run_check("docs")
    if code == 0:
        return False, "docs/research: buzuq havola O'TKAZILDI (exit 0) — istisno havolani ham o'chirgan"
    if not re.search(r"docs[\\/]research[\\/]README\.md: buzilgan havola", out):
        return False, f"docs/research: exit {code}, lekin sabab tadqiqot havolasi emas — {out.strip()[-160:]}"
    return True, "docs/research: yozuvdagi buzuq havola tutildi (exit 1)"


def neg_docs_research_exemption_is_scoped() -> tuple[bool, str]:
    """Script mixing is allowed in research records only, not in living docs."""
    record = ROOT / "docs/research/README.md"
    living = ROOT / "docs/README.md"
    if not record.exists() or not living.exists():
        return False, "docs/istisno: README fayllari topilmadi"
    line = "\n\nAralash yozuv namunasi: салом dunyo\n"
    record_text = record.read_bytes().decode("utf-8")
    with Mutation(record, record_text, record_text.rstrip() + line):
        code, out = run_check("docs")
    if code != 0:
        return False, f"docs/istisno: tadqiqot yozuvidagi kirill matn qizil qildi — {out.strip()[-160:]}"
    living_text = living.read_bytes().decode("utf-8")
    with Mutation(living, living_text, living_text.rstrip() + line):
        code, out = run_check("docs")
    if code == 0 or "kirill/lotin aralashuvi" not in out:
        return False, "docs/istisno: tirik hujjatdagi aralash yozuv O'TKAZILDI — istisno keng ketgan"
    return True, "docs/istisno: faqat docs/research ozod, tirik hujjat tutildi"


def neg_email_missing_locale() -> tuple[bool, str]:
    """Bitta satrdan bitta til olib tashlansa — tutilsinmi?

    Ilgari til jimgina `uz` ga tushardi; bu tekshiruv o'sha holatni CI da
    to'xtatadi.
    """
    path = ROOT / "apps/api/core/email_text.py"
    old = '        "es": "RankWant — restablecer contraseña",'
    if old not in path.read_bytes().decode("utf-8"):
        return False, "email/til: sinov uchun qator topilmadi"
    with Mutation(path, old + "\n", ""):
        return expect_fail("email_locales", "email/yetishmayotgan til")


def neg_email_blank_value() -> tuple[bool, str]:
    """Bitta matn bo'sh qolsa — tutilsinmi?"""
    path = ROOT / "apps/api/core/email_text.py"
    old = '        "en": "Sign in",'
    new = '        "en": "   ",'
    if old not in path.read_bytes().decode("utf-8"):
        return False, "email/bo'sh: sinov uchun qator topilmadi"
    with Mutation(path, old, new):
        return expect_fail("email_locales", "email/bo'sh matn")


def neg_email_undeclared_locale() -> tuple[bool, str]:
    """Ro'yxatda yo'q til qo'shilsa — tutilsinmi?"""
    path = ROOT / "apps/api/core/email_text.py"
    old = '        "es": "RankWant",'
    new = '        "es": "RankWant",\n        "xx": "RankWant",'
    if old not in path.read_bytes().decode("utf-8"):
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
    if old not in path.read_bytes().decode("utf-8"):
        return False, "parity/yetishmaydi: sinov uchun qator topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("locales_parity", "parity/LANGUAGES da til yetishmaydi")


def neg_parity_extra_locale() -> tuple[bool, str]:
    """`LOCALES` ga `User.Locale` da yo'q til qo'shilsa — tutilsinmi?"""
    path = ROOT / "apps/api/core/email_text.py"
    old = '"zh", "es")'
    new = '"zh", "es", "xx")'
    if old not in path.read_bytes().decode("utf-8"):
        return False, "parity/ortiqcha: sinov uchun qator topilmadi"
    with Mutation(path, old, new):
        return expect_fail("locales_parity", "parity/LOCALES da ortiqcha til")


def neg_i18n_country_locale_dropped() -> tuple[bool, str]:
    """Jadvaldan til olib tashlansa — tutilsinmi?

    ⚠️ Aynan shu nuqson bor edi: `countries.ts` jadvalni faqat uz/ru
    uchun ishlatardi va `kaa`/`kk`/`ky`/`tg` da inglizcha nom chiqardi
    (Chrome'da o'lchandi). Node o'lchovi buni KO'RSATMAGAN — shuning
    uchun tekshiruv manba kodni o'qiydi.
    """
    path = ROOT / "apps/web/src/lib/countries.ts"
    text = path.read_bytes().decode("utf-8")
    old = 'const CYRILLIC: Locale[] = ["ru", "kk", "ky", "tg"];'
    new = 'const CYRILLIC: Locale[] = ["ru"];'
    if old not in text:
        return False, "mamlakat: langar `CYRILLIC` qatori topilmadi"
    with Mutation(path, old, new):
        return expect_fail("i18n", "i18n/mamlakat jadvaldan til tushib qoldi")


def neg_i18n_country_icu_locale_added() -> tuple[bool, str]:
    """ICU bor til jadvalga qo'shilsa — tutilsinmi?

    `tr` ni jadvalga qo'shib ko'rgan edim: turkchada ICU "Almanya" beradi,
    jadval esa "Germaniya" qilib buzdi (o'lchandi). Bu test o'sha
    regressiyani qaytaradi.
    """
    path = ROOT / "apps/web/src/lib/countries.ts"
    text = path.read_bytes().decode("utf-8")
    old = 'const LATIN_UZ: Locale[] = ["uz", "kaa"];'
    new = 'const LATIN_UZ: Locale[] = ["uz", "kaa", "tr"];'
    if old not in text:
        return False, "mamlakat: langar `LATIN_UZ` qatori topilmadi"
    with Mutation(path, old, new):
        return expect_fail("i18n", "i18n/mamlakat ICU tili jadvalga qo'shildi")


def neg_i18n_country_row_missing() -> tuple[bool, str]:
    """Jadvaldan bitta kod olib tashlansa — tutilsinmi?

    ⚠️ `check_country_locales()` faqat til RO'YXATLARINI tekshiradi. Jadval
    o'zi to'liqmi — qo'riqlanmagan edi. Bir kod tushib qolsa `countryName()`
    jimgina ICU ga tushadi va o'sha tillarda **inglizcha** nom chiqadi.
    """
    path = ROOT / "apps/web/src/lib/country-names.ts"
    text = path.read_bytes().decode("utf-8")
    # ⚠️ `^` ISHLATILMAYDI: jadval qatorlari ichkariga surilgan (`  "DE": …`),
    # shuning uchun satr boshiga bog'langan langar hech qachon topilmaydi —
    # test "langar yo'q" deb yiqiladi va qoida tekshirilmagan holda qoladi.
    m = re.search(r'"DE":\s*\[[^\]]*\],', text)
    if m is None:
        return False, "mamlakat: jadvalda `DE` qatori topilmadi"
    with Mutation(path, m.group(0), ""):
        return expect_fail("i18n", "i18n/mamlakat jadvalida kod yetishmaydi")


def neg_i18n_country_row_blank() -> tuple[bool, str]:
    """Jadval qiymati bo'sh qolsa — tutilsinmi?

    Bo'sh satr inglizchaga tushish bilan barobar: jadval topiladi, lekin
    UI da mamlakat nomi umuman ko'rinmaydi.
    """
    path = ROOT / "apps/web/src/lib/country-names.ts"
    text = path.read_bytes().decode("utf-8")
    m = re.search(r'"DE":\s*\["([^"]*)",\s*"([^"]*)"\],', text)
    if m is None:
        return False, "mamlakat: jadvalda `DE` qatori topilmadi"
    # O'zbekcha qiymatni bo'sh qilib qo'yamiz.
    broken = m.group(0).replace(f'"{m.group(1)}"', '""', 1)
    with Mutation(path, m.group(0), broken):
        return expect_fail("i18n", "i18n/mamlakat jadvalida bo'sh qiymat")


def neg_i18n_review_sheet_stale() -> tuple[bool, str]:
    """Ko'rib chiqish varaqasi lug'atdan orqada qolsa — tutilsinmi?

    ⚠️ Varaqni ona tilida so'zlashuvchi odam qo'lda o'qiydi. Eskirgan varaq
    o'zgargan matnni ko'rsatadi va tasdiqlanmagan matn "tekshirilgan" degan
    taassurot qoldiradi — bu jimgina o'tkazishning eng qimmat turi.
    """
    path = ROOT / "docs/08-technical-spec/i18n-review/kk.md"
    if not path.exists():
        return False, "i18n-review: `kk.md` topilmadi"
    text = path.read_bytes().decode("utf-8")
    lines = text.splitlines(keepends=True)
    idx = next((i for i, l in enumerate(lines) if l.startswith("| `")), None)
    if idx is None:
        return False, "i18n-review: `kk.md` da jadval qatori topilmadi"
    # Bitta qatorni olib tashlaymiz -> son lug'atga mos kelmay qoladi.
    broken = "".join(lines[:idx] + lines[idx + 1 :])
    with Mutation(path, text, broken):
        return expect_fail("i18n", "i18n/ko'rib chiqish varaqasi eskirgan")


def neg_i18n_review_sheet_old_key() -> tuple[bool, str]:
    """Varaqda ko'chirilgan eski kalit qolsa — tutilsinmi?

    `empty` bir vaqtlar prefikssiz edi va `common.empty` ga ko'chirildi.
    Varaqda eski nom qolsa, odam mavjud bo'lmagan kalitni ko'rib chiqadi.
    """
    path = ROOT / "docs/08-technical-spec/i18n-review/kk.md"
    if not path.exists():
        return False, "i18n-review: `kk.md` topilmadi"
    text = path.read_bytes().decode("utf-8")
    line = next(
        (l for l in text.splitlines() if l.startswith("| `common.empty`")), None
    )
    if line is None:
        return False, "i18n-review: `common.empty` qatori topilmadi"
    broken = text.replace(line, "| `empty` | x | y |  |", 1)
    with Mutation(path, text, broken):
        return expect_fail("i18n", "i18n/varaqda eski kalit qolgan")


def neg_i18n_parity_does_not_mask() -> tuple[bool, str]:
    """Paritet buzilganda KEYINGI qoidalar ham xabar bersinmi?

    ⚠️ `main()` da erta `return 1` bor edi: paritet yiqilsa qolgan
    qoidalar umuman ishlamasdi. Bitta uzilish ikki bosqichda ochilardi —
    avval paritet tuzatiladi, keyin navbatdagi qoida qizaradi. Bu test
    o'sha erta chiqish qaytib kelmasligini qo'riqlaydi: buzuq holatda
    chiqishda **ham** paritet, **ham** varaq xabari bo'lishi shart.
    """
    src = ROOT / "apps/web/src/i18n/locales/uz.ts"
    text = src.read_bytes().decode("utf-8")
    m = re.search(r'^(  "common\.empty":.*)$', text, re.M)
    if m is None:
        return False, "i18n: `common.empty` langari topilmadi"
    broken = text.replace(m.group(1), m.group(1) + '\n  "common.probe": "Probe",', 1)
    with Mutation(src, text, broken):
        code, out = run_check("i18n")
        if code == 0:
            return False, "i18n/paritet erta chiqishi: buzuq holat o'tkazildi"
        has_parity = "common.probe" in out
        has_sheet = "eskirgan" in out
        if not (has_parity and has_sheet):
            return False, (
                "i18n/paritet keyingi qoidani to'sdi — "
                f"paritet={has_parity}, varaq={has_sheet}"
            )
        return True, "i18n/paritet keyingi qoidalarni to'smaydi (exit 1)"


def neg_i18n_bare_key() -> tuple[bool, str]:
    """Prefikssiz kalit qo'shilsa — tutilsinmi?

    ⚠️ `empty` bir vaqtlar yagona prefikssiz kalit edi va tekshiruv uni
    istisno qilardi. Endi u `common.empty` ga ko'chirilgan, istisno esa
    olib tashlangan — qoida istisnosiz. Bu test o'sha holatni saqlab
    turadi: yangi prefikssiz nom qo'shilsa, tekshiruv qizarishi shart.
    """
    path = ROOT / "apps/web/src/i18n/locales/uz.ts"
    text = path.read_bytes().decode("utf-8")
    anchor = '  "team.intro":'
    if anchor not in text:
        return False, 'i18n/prefiks: langar `"team.intro":` topilmadi'
    injected = '  empty2: "Sinov",\n' + anchor
    with Mutation(path, anchor, injected):
        return expect_fail("i18n", "i18n/prefikssiz kalit")


def neg_i18n_template_family() -> tuple[bool, str]:
    """Shablon oilaning BARCHA kaliti o'chirilsa — tutilsinmi?

    13-band: `t(locale, `customizer.template.${id}`)` — shablon kalit.
    Birortasi yo'q bo'lsa foydalanuvchi xom kalit ko'radi, `CALL_RE`
    esa buni ko'rmaydi (shablon statik emas).
    """
    path = ROOT / "apps/web/src/i18n/locales/uz.ts"
    text = path.read_bytes().decode("utf-8")
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
    if old not in path.read_bytes().decode("utf-8"):
        return False, "i18n/server evict: langar topilmadi"
    with Mutation(path, old, new):
        return expect_fail("i18n", "i18n/server evict bilan chegaralangan")


def neg_i18n_registry_module_local() -> tuple[bool, str]:
    """A module-local registry again: SSR client components lose the text."""
    path = ROOT / "apps/web/src/i18n/messages.ts"
    old = "const registry: Registry = (realm.__rwMessages ??= new Map());"
    new = "const registry: Registry = new Map();"
    if old not in path.read_bytes().decode("utf-8"):
        return False, "i18n/reyestr globalThis: langar topilmadi"
    with Mutation(path, old, new):
        return expect_fail("i18n", "i18n/reyestr modul ichida")


def neg_i18n_registry_cleared() -> tuple[bool, str]:
    """`registerMessages` clearing the shared registry again."""
    path = ROOT / "apps/web/src/i18n/messages.ts"
    old = "  registry.set(locale, dict);\n"
    new = "  registry.clear();\n  registry.set(locale, dict);\n"
    if old not in path.read_bytes().decode("utf-8"):
        return False, "i18n/reyestr tozalash: langar topilmadi"
    with Mutation(path, old, new):
        return expect_fail("i18n", "i18n/reyestr to'liq tozalanadi")


def neg_i18n_server_missing_locale() -> tuple[bool, str]:
    """`ALL` dan bitta til olib tashlansa — tutilsinmi?"""
    path = ROOT / "apps/web/src/i18n/messages.server.ts"
    old = "  tg,\n"
    if old not in path.read_bytes().decode("utf-8"):
        return False, "i18n/server yetishmaydi: langar topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("i18n", "i18n/server lug'atda til yetishmaydi")


def neg_i18n_runtime_dev_throw() -> tuple[bool, str]:
    """Dev'dagi `throw` olib tashlansa — runtime tekshiruvi tutsinmi?

    Nega kerak: `tools/check_i18n.py` faqat MATNNI o'qiydi, ya'ni
    `throw` o'rniga `console.error` qo'yilsa u baribir yashil qoladi.
    Bu salbiy test aynan shu bo'shliqni yopadi.
    """
    path = ROOT / "apps/web/src/i18n/messages.ts"
    old = "    throw new Error(`i18n: ${detail}`);"
    if old not in path.read_bytes().decode("utf-8"):
        return False, "i18n/runtime dev throw: langar topilmadi"
    new = "    void detail; // dev throw removed by negative test"
    with Mutation(path, old, new):
        return expect_node_fail("i18n/runtime dev throw yo'q")


def neg_i18n_runtime_dedup() -> tuple[bool, str]:
    """«Bir marta jurnalga yozish» olib tashlansa — tutilsinmi?

    Prod shartnomasining ikkinchi yarmi: bir xil kalit yuzlab marta
    chaqiriladi, `console.error` esa haqiqiy xatoni ko'mib tashlamasligi
    uchun BIR MARTA yozilishi kerak.
    """
    path = ROOT / "apps/web/src/i18n/messages.ts"
    old = """  if (!reported.has(tag)) {
    reported.add(tag);"""
    if old not in path.read_bytes().decode("utf-8"):
        return False, "i18n/runtime dedup: langar topilmadi"
    new = """  if (true) {
    reported.add(tag);"""
    with Mutation(path, old, new):
        return expect_node_fail("i18n/runtime takroriy jurnal")


def neg_hardcoded_prose() -> tuple[bool, str]:
    """Admin faylga qattiq yozilgan matn qo'yilsa — tekshiruv tutsin.

    ⚠️ Bu tekshiruv `tools/check_i18n.py` KO'RMAYDIGAN sinf uchun: u faqat
    kod → lug'at yo'nalishini tekshiradi, ya'ni jadval sarlavhasidagi
    `label: "Sana"` unga ko'rinmaydi. 274 ta shunday satr «toza ✓» ostida
    turgan edi.

    Anchor — `CrudPage.tsx` dagi `ColumnDef` maydoni. U o'zgarsa test
    shovqin bilan yiqiladi, jimgina o'lmaydi.

    ⚠️ Langar `label:`/`title:` kabi HAQIQIY matn pozitsiyasi bo'lishi
    shart. `type?: FieldType;` yoki `align?: …` tip pozitsiyasi — u yerga
    qo'yilgan satr hech qachon ko'rinmaydi (checker uni matn deb
    hisoblamaydi), va test «tekshiruv o'lik» degan yolg'on xulosa beradi.
    """
    path = ROOT / "apps/web/src/components/admin/CrudPage.tsx"
    with Mutation(
        path,
        '  align?: "left" | "right";',
        '  align?: "left" | "right";\n  label: "Sana";',
    ):
        return expect_fail("hardcoded", "qattiq yozilgan `label:`")


def neg_hardcoded_locale_less_date() -> tuple[bool, str]:
    """`toLocaleString()` tilni bermasa — tekshiruv tutsin.

    Brauzer tilni O'ZI tanlaydi, ilova tili emas: rus tilida ishlaydigan
    admin operatsion tizim tanlagan formatda sana ko'radi. To'rt joyda
    shu xato topilgan edi.
    """
    path = ROOT / "apps/web/src/components/admin/CrudPage.tsx"
    with Mutation(
        path,
        '  align?: "left" | "right";',
        '  align?: "left" | "right";\n  x: new Date().toLocaleDateString();',
    ):
        return expect_fail("hardcoded", "tilsiz sana formati")


# --- the four rules that were narrowed today ------------------------------
#
# Each of these guards a filter that had swallowed real prose or flagged a
# measurement. The test is written the other way round from the first two:
# it plants a string that LOOKS like the code shape the filter accepts, and
# asserts the checker still reports it. A filter that is too eager is
# invisible without a test like this — the checker simply says "toza ✓".


def neg_hardcoded_number_in_prose() -> tuple[bool, str]:
    """Raqam bilan boshlangan MATN rang deb hisoblanmasin.

    `COLORY` avval `\\d` bilan boshlanadigan har qanday satrni rang deb
    olardi, ya'ni `"45 masala"` (haqiqiy interfeys matni) ko'rinmas edi.
    Bu soxta salbiy edi va u `"2-qadam (joy va maktab)"` hamda
    `"1-bosqich"` ni yashirgan — ikkalasi bugun topildi.

    Anchor — `CrudPage` dagi `label:` maydoni: o'sha pozitsiya qattiq
    yozilgan matnni HAQIQATAN ushlaydi (`neg_hardcoded_prose` shuni
    isbotlaydi). `align?: "left" | "right";` tip pozitsiyasi edi va u
    hech qachon matn hisoblanmaydi — birinchi urinish shuning uchun
    yolg'on «o'lik» natija berdi.
    """
    path = ROOT / "apps/web/src/components/admin/CrudPage.tsx"
    with Mutation(
        path,
        '  align?: "left" | "right";',
        '  align?: "left" | "right";\n  label: "45 masala yechildi";',
    ):
        return expect_fail("hardcoded", "raqam bilan boshlangan matn")


def neg_hardcoded_actual_colour_passes() -> tuple[bool, str]:
    """`COLORY` ning qarama-qarshi tomoni: haqiqiy rang O'TISHI kerak.

    ⚠️ Bu test ham shart. `COLORY` ni toraytirib, `#fff` yoki `12px` ni
    «matn» deb e'lon qilish oson — o'shanda tekshiruv 40 ta soxta musbat
    beradi va odamlar uni `# noqa` bilan o'chira boshlaydi.
    """
    path = ROOT / "apps/web/src/components/admin/CrudPage.tsx"
    with Mutation(
        path,
        '  align?: "left" | "right";',
        '  align?: "left" | "right";\n  a: "#fff";\n  b: "12px";\n  c: "var(--bg)";',
    ):
        code, _ = run_check("hardcoded")
        if code == 0:
            return True, "hardcoded/haqiqiy rang: rang qiymatlari matn deb topilmadi"
        return False, "haqiqiy rang qiymatlari matn deb topildi"


def neg_hardcoded_number_unit_passes() -> tuple[bool, str]:
    """O'lchov birligi (`12 MB`, `8 AC`) matn hisoblanmasin, lekin
    `45 masala` matn bo'lib QOLsin — ikkisi bir testda.

    Farq birlik ro'yxatida: `MB`/`AC` — o'lchov belgisi, `masala` — so'z.
    Langar — `TD` komponentining `label=` atributi: matn pozitsiyasi.
    """
    path = ROOT / "apps/web/src/app/problems/page.tsx"
    with Mutation(
        path,
        '<TH>{t(locale, "problems.name")}</TH>',
        '<TH label="12 MB">8 AC 45 masala</TH>',
    ):
        code, _ = run_check("hardcoded")
        if code == 1:
            return (
                True,
                "hardcoded/o'lchov birligi: `45 masala` matn bo'lib qoldi (exit 1)",
            )
        return False, "`45 masala` o'lchov birligi deb o'tkazib yuborildi"


def neg_hardcoded_wide_scope() -> tuple[bool, str]:
    """Kengaytirilgan doira HAQIQATAN o'qilishini tasdiqlasin.

    `target_files()` bugun `apps/web/src` ning hammasiga ochildi. Doira
    jimgina adminda qolib ketsa, 247 fayl haqidagi xabar yolg'on bo'lardi.
    Langar — admin panelda BO'LMAGAN fayldagi JSX matni.
    """
    path = ROOT / "apps/web/src/app/rating/page.tsx"
    with Mutation(
        path,
        '<Section title="Skills"',
        '<p>Kengaytirilgan doira sinovi</p>\n      <Section title="Skills"',
    ):
        return expect_fail("hardcoded", "admin tashqarisidagi fayl")


def neg_hardcoded_single_word_label() -> tuple[bool, str]:
    """Bosh harf bilan boshlangan BIR SO'ZLI JSX yorlig'i matn hisoblansin.

    ⚠️ Bu teshik edi va u qimmatga tushdi: `PASCAL_TOKEN` filtri `>Vaqt<`
    ni «komponent yoki tip nomi» deb o'tkazib yuborardi. Filtr STRING
    literal uchun to'g'ri (`type: "Checkbox"`), lekin JSX MATNI uchun
    noto'g'ri — u ekranga chiqadi.

    O'lchandi: filtr olib tashlanganda 49 ta haqiqiy yorliq ko'rindi
    (`<TH>Vaqt</TH>`, `<TH>Xotira</TH>`, `Saqlash`, `Yuborildi`, `Rol` …),
    ya'ni jadval sarlavhalari va admin tugmalari 9 tilda o'zbekcha
    qolgan edi. O'zbek tili agglyutinativ — bir so'zli yorliqlar ko'p,
    shuning uchun bu teshik ayniqsa keng edi.

    `neg_hardcoded_viewbox_passes` bilan bir juft: u yolg'on musbatni
    to'sadi, bu esa yolg'on manfiyni.
    """
    path = ROOT / "apps/web/src/components/profile/RatingChart.tsx"
    with Mutation(
        path,
        '<p className="text-theme-sm rw-faint">{t(locale, "profile.chartEmpty")}</p>;',
        '<p className="text-theme-sm rw-faint">{t(locale, "profile.chartEmpty")}<span>Vaqt</span></p>;',
    ):
        return expect_fail("hardcoded", "hardcoded/bir so'zli JSX yorlig'i")


def neg_hardcoded_viewbox_passes() -> tuple[bool, str]:
    """SVG `viewBox` koordinatalari matn hisoblanmasin.

    `0 0 ${W} ${H}` JSX matni emas — SVG geometriyasi. Usiz tekshiruv
    har bir grafik komponentda yiqilardi.
    """
    path = ROOT / "apps/web/src/components/profile/RatingChart.tsx"
    with Mutation(
        path,
        "viewBox={`0 0 ${W} ${H}`}",
        "viewBox={`0 0 ${W} ${H}`}\n          data-probe={`0 0 ${1} ${2}`}",
    ):
        code, _ = run_check("hardcoded")
        if code == 0:
            return True, "hardcoded/viewBox: SVG koordinatalari matn deb topilmadi"
        return False, "viewBox koordinatalari matn deb topildi"


def neg_workers_fail_open_false() -> tuple[bool, str]:
    """`fail_open` yopiq bo'lsa tekshiruv yiqiladimi?

    ⚠️ Cloudflare'da bu maydonning standarti `false`. Ya'ni route qayta
    yaratilsa himoya **jimgina** yo'qoladi va sayt keyingi limit
    tugaganda Error 1027 bilan yopiladi. Skript shuni tutishi shart.

    ⚠️ Maydon ochiq API hujjatida yo'q va `GET` uni faqat haqiqiy
    route'da qaytaradi — shuning uchun tarmoqqa chiqmaymiz: audit
    skriptining chiqishini `CF_ROUTE_STUB` bilan almashtiramiz.
    """
    stub = (
        "rankwant.uz\trankwant.uz/*\tTrue\n"
        "rankwant.uz\twww.rankwant.uz/*\tFalse\n"
        "bugvector.uz\trankwant.bugvector.uz/*\tTrue\n"
    )
    code, out = _run_workers(stub)
    if code == 0:
        return (
            False,
            "workers/fail_open: yopiq route O'TKAZILDI (exit 0) — tekshiruv o'lik",
        )
    if "YOQ" not in out:
        return (
            False,
            f"workers/fail_open: yiqildi, lekin sabab ko'rinmadi — {out.strip()[:120]}",
        )
    return True, "workers/fail_open: yopiq route tutildi (exit 1)"


def neg_workers_unreadable_is_not_green() -> tuple[bool, str]:
    """O'qib bo'lmasa — «yaxshi» emas, «o'lchab bo'lmadi» bo'lsinmi?

    ⚠️ Bu eng qimmat tuzoq: token yo'q bo'lsa skript `exit 1` bersa,
    CI «himoya yo'q» deb qichqiradi va odam o'zgarmagan narsani
    tuzatishga urinadi. `exit 0` bersa — yashil yolg'on. Shuning uchun
    alohida `exit 2` bo'lishi SHART va chiqishda sayt haqida xulosa
    chiqmasligi kerak.
    """
    code, out = _run_workers(None)
    if code != 2:
        return False, f"workers/o'qilmadi: exit {code} (2 bo'lishi kerak edi)"
    if "xulosa YOQ" not in out:
        return False, "workers/o'qilmadi: `xulosa YOQ` ogohlantirishi yo'q"
    return True, "workers/o'qilmadi: exit 2 va sayt haqida xulosa chiqmaydi"


def neg_workers_crlf_stub_passes() -> tuple[bool, str]:
    """CRLF bilan kelgan `True` ham «ha» deb o'qilsinmi?

    ⚠️ HAQIQIY xato shu yerda yashiringan edi (2026-09-14 da o'lchandi).
    Windows'da Python `print()` CRLF yozadi; `read` esa faqat `\\n` ni
    ajratadi, shuning uchun qiymat `True\\r` bo'lib qoladi va
    `[ "$failopen" = "True" ]` HECH QACHON mos kelmaydi. Natijada
    **himoyalangan route «himoyasiz» deb ko'rinadi** — ya'ni skript
    yolg'on XATO beradi.

    Avvalgi ikkita test buni tutmadi, chunki ular stub'ni `\\n` bilan
    uzatardi: test o'lchov muhitini takrorlamagan edi. Shuning uchun bu
    test stub'ga ATAYLAB `\\r` qo'shadi.
    """
    stub = (
        "rankwant.uz\trankwant.uz/*\tTrue\r\n"
        "rankwant.uz\twww.rankwant.uz/*\tTrue\r\n"
        "bugvector.uz\trankwant.bugvector.uz/*\tTrue\r\n"
    )
    code, out = _run_workers(stub)
    if code != 0:
        return False, (
            "workers/CRLF: himoyalangan route «himoyasiz» deb o'qildi "
            f"(exit {code}) — `\\r` tozalanmayapti"
        )
    if out.count("ha") < 3:
        return False, f"workers/CRLF: 3 ta «ha» kutilgan edi — {out.strip()[:120]}"
    return True, "workers/CRLF: `\\r` tozalanadi, 3 ta route «ha» (exit 0)"


def neg_workers_restored_gate() -> tuple[bool, str]:
    """Himoyalangan holat YASHIL bo'lishini talab qiladi (ijobiy nazorat).

    Negativ testlar faqat «yiqiladimi?» ni so'raydi. Skript hamma narsani
    «himoyasiz» deb qichqirsa, ularning BARCHASI yashil bo'lardi — va
    skript foydasiz bo'lardi. Bu test teskari tomonni qo'riqlaydi.
    """
    stub = (
        "rankwant.uz\trankwant.uz/*\tTrue\n"
        "rankwant.uz\twww.rankwant.uz/*\tTrue\n"
        "bugvector.uz\trankwant.bugvector.uz/*\tTrue\n"
    )
    code, out = _run_workers(stub)
    if code != 0:
        return False, f"workers/yashil: himoyalangan holat exit {code} berdi (0 kerak)"
    if "himoyalangan" not in out:
        return False, "workers/yashil: muvaffaqiyat xabari ko'rinmadi"
    return True, "workers/yashil: 3 ta route himoyalangan (exit 0)"


def _bash() -> str:
    """`bash` ning to'liq yo'li.

    ⚠️ Windows'da yalang'och `bash` WSL relay'iga tushadi va
    `execvpe(/bin/bash) failed: No such file or directory` beradi —
    ya'ni skript umuman ishga tushmaydi va chiqish kodi 1 bo'ladi, uni
    esa «buzuq holatni tutdi» deb o'qish oson. Shu sabab Git Bash'ning
    to'liq yo'lini qidiramiz.
    """
    for candidate in (
        os.environ.get("BASH"),
        r"C:\Program Files\Git\bin\bash.exe",
        shutil.which("bash"),
    ):
        if candidate and Path(candidate).exists():
            return str(candidate)
    return "bash"


def _run_workers(stub: str | None) -> tuple[int, str]:
    """`check_workers.sh` ni soxta audit chiqishi bilan ishga tushiradi.

    `stub=None` — audit skripti `exit 2` beradi (token yo'q holati).
    """
    env = dict(os.environ)
    if stub is None:
        env["CF_ROUTE_STUB"] = ""
        env["CF_ROUTE_FORCE_UNREADABLE"] = "1"
    else:
        env["CF_ROUTE_STUB"] = stub
        env.pop("CF_ROUTE_FORCE_UNREADABLE", None)
    proc = subprocess.run(
        [_bash(), "tools/check_workers.sh"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _run_ci(runners: str | None, runs: str) -> tuple[int, str]:
    """`check_ci.sh` ni soxta runner/run ro'yxati bilan ishga tushiradi.

    `runners=None` — «`gh` yo'q» holatini taqlid qiladi: stub berilmaydi
    va `PATH` bo'shatiladi, ya'ni skript o'lchay olmaydi va 2 qaytarishi
    kerak. 0 EMAS: o'lchanmagan holat «yaxshi» degani emas.
    """
    env = dict(os.environ)
    env["CI_RUNS_STUB"] = runs
    if runners is None:
        env.pop("CI_RUNNERS_STUB", None)
        env["PATH"] = "/nonexistent"
    else:
        env["CI_RUNNERS_STUB"] = runners
    proc = subprocess.run(
        [_bash(), "tools/check_ci.sh"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def neg_ci_offline_runner_is_red() -> tuple[bool, str]:
    """Runner oflayn bo'lsa skript QIZIL bo'lishi shart.

    Bu — 2026-09-13 dagi haqiqiy holat: ikki runner ham `offline`, hamma
    run `queued`. Skript buni «hammasi joyida» deb o'qisa, butun maqsadi
    yo'qoladi.
    """
    code, out = _run_ci(
        "nsn-pc-rankwant|Linux|offline\nnsn-pc-rankwant-2|Linux|offline",
        "CI|queued|—|abc1234|2026-09-14T08:30:00Z",
    )
    if code == 0:
        return False, "ci/offline: runner oflayn, lekin exit 0 — tekshiruv o'lik"
    if code != 1:
        return False, f"ci/offline: exit {code} (1 kerak edi)"
    if "JONSIZ" not in out:
        return False, "ci/offline: sabab matni ko'rinmadi"
    return True, "ci/offline: runner yo'qligi tutildi (exit 1)"


def neg_ci_stuck_run_is_red() -> tuple[bool, str]:
    """Runner TIRIK bo`lganda ham qotib qolgan run qizil bo`lsin.

    2026-09-16: runner `online, busy=False`, run esa 22 daqiqa
    `queued`/`in progress` bo`lib turdi — GitHub job`ni boshlangan deb
    hisoblaydi, uni bajaradigan `Runner.Worker` esa yo`q (assignment
    eskirgan). Faqat runner holatiga qaraydigan tekshiruv buni «yashil»
    deb o`qirdi va kodda bo`lmagan xatoni qidirishga olib keldi.

    Uch holat ketma-ket o`lchanadi va uchtasi ham shart:
      1) YANGI `in_progress` run → 0 — aks holda oddiy ishlab turgan CI
         ham «qotgan» bo`lib ko`rinardi va signal ma`nosiz bo`lardi;
      2) 40 daqiqalik `in_progress` run → 1;
      3) matnda sabab va `cancel`+`rerun` retsepti ko`rinishi shart.
    """
    from datetime import datetime, timedelta, timezone

    fresh = (datetime.now(timezone.utc) - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    stale = (datetime.now(timezone.utc) - timedelta(minutes=40)).strftime("%Y-%m-%dT%H:%M:%SZ")
    runners = "nsn-pc-rankwant|Linux|online"

    code, out = _run_ci(runners, f"CI|in_progress|—|abc1234|{fresh}")
    if code != 0:
        return False, f"ci/stuck: yangi run qizil bo`ldi (exit {code}) — signal ma`nosiz"

    code, out = _run_ci(runners, f"CI|in_progress|—|abc1234|{stale}")
    if code == 0:
        return False, "ci/stuck: qotgan run O`TKAZDI (exit 0) — tekshiruv o`lik"
    if "QOTISH" not in out:
        return False, "ci/stuck: qotish sababi matnda ko`rinmadi"
    if "gh run cancel" not in out:
        return False, "ci/stuck: yechim (cancel + rerun) ko`rsatilmadi"
    return True, "ci/stuck: qotish tutildi, retsept ko`rsatildi (exit 1)"


def neg_ci_startup_failure_is_red() -> tuple[bool, str]:
    """`startup_failure` runner holatidan MUSTAQIL ravishda qizil bo'lsin.

    Runner tirik bo'lsa ham bu run hech qachon boshlamaydi — ruxsat
    xatosi. Agar skript faqat runner'ga qarasa, bu holat ko'rinmay
    qolardi va noto'g'ri joy tuzatilardi.
    """
    code, out = _run_ci(
        "nsn-pc-rankwant|Linux|online",
        "Deploy|completed|startup_failure|abc1234|2026-09-13T21:55:00Z",
    )
    if code != 1:
        return False, f"ci/startup: exit {code} (1 kerak edi)"
    if "startup_failure" not in out:
        return False, "ci/startup: sabab matni ko'rinmadi"
    return True, "ci/startup: ruxsat xatosi runner tirik bo'lsa ham tutildi"


def neg_ci_unreadable_is_not_green() -> tuple[bool, str]:
    """O'qib bo'lmasa exit 2 — «yaxshi» emas.

    O'qilmagan qiymatni «o'tdi» deb hisoblash — eng qimmat xato sinfi.
    """
    code, out = _run_ci(None, "CI|completed|success|abc1234|2026-09-14T12:00:00Z")
    if code == 0:
        return False, "ci/o'qilmadi: exit 0 — o'lchanmagan holat «yashil» deb o'qildi"
    if code != 2:
        return False, f"ci/o'qilmadi: exit {code} (2 kerak edi)"
    if "gh" not in out:
        return False, "ci/o'qilmadi: sabab matni ko'rinmadi"
    return True, "ci/o'qilmadi: exit 2 va sabab aytiladi"


def neg_ci_healthy_gate() -> tuple[bool, str]:
    """Ijobiy nazorat: sog'lom holat YASHIL bo'lishi shart.

    Hamma narsani qizil qiladigan skript BARCHA salbiy testlardan o'tadi
    va baribir foydasiz bo'ladi — shuning uchun yashil yo'l alohida
    tekshiriladi.
    """
    code, out = _run_ci(
        "nsn-pc-rankwant|Linux|online",
        "CI|completed|success|abc1234|2026-09-14T12:00:00Z",
    )
    if code != 0:
        return False, f"ci/yashil: sog'lom holat exit {code} berdi (0 kerak)"
    if "haqiqiy natija" not in out:
        return False, "ci/yashil: muvaffaqiyat xabari ko'rinmadi"
    return True, "ci/yashil: runner tirik + success (exit 0)"


# ── backup ───────────────────────────────────────────────────────────────


def _tmp_dir() -> "tempfile.TemporaryDirectory[str]":
    """Repo ICHIDA vaqtinchalik katalog.

    ⚠️ `/tmp` ISHLATILMAYDI. Windows'da u ikki xil joy: Git Bash uni MSYS
    ildizi deb biladi, nativ Python esa Windows ildizidagi boshqa katalogni
    ochadi — ya'ni Python yozgan faylni shell ko'rmaydi va test «fayl yo'q»
    deb yiqiladi. `.githooks/pre-push` ham aynan shu sababdan `.tmp/` ga
    yozadi.
    """
    base = ROOT / ".tmp"
    base.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(dir=str(base))


def _make_dump(path: Path, *, complete: bool) -> None:
    """Soxta `pg_dump | gzip` arxivini yasaydi.

    Tana ataylab 4 KB dan KATTA: `backup.sh` yakuniy qatorni
    `tail -c 4096` bilan qidiradi. Kichik faylda «tugallangan» va «chala»
    orasidagi farq yo'qolib ketardi va test o'z maqsadini isbotlamasdi.
    """
    body = "-- negative test dump\n" + ("SELECT 1;\n" * 900)
    if complete:
        body += "--\n-- PostgreSQL database dump complete\n--\n"
    else:
        # `pg_dump` o'rtada uzilganda aynan shunday ko'rinadi: gzip butun,
        # yakuniy qator esa yo'q.
        body += "COPY problems_problem (id) FROM stdin;\n"
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write(body)


def _run_backup_verify(path: Path) -> tuple[int, str]:
    """`backup.sh --verify-dump` ni bitta arxiv ustida ishga tushiradi.

    ⚠️ Docker KERAK EMAS va jonli bazaga TEGILMAYDI: bu rejim faqat faylni
    o'qiydi. Shuning uchun test CI da ham, stack ko'tarilmagan mashinada
    ham o'lchaydi — `workers` va `ci` guruhlari bilan bir xil uslub.

    Yo'l NISBIY uzatiladi: disk harfi ham, teskari chiziq ham shell'ga
    umuman bormaydi.
    """
    rel = path.resolve().relative_to(ROOT).as_posix()
    proc = subprocess.run(
        [_bash(), "tools/backup.sh", "--verify-dump", rel],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def neg_backup_truncated_archive() -> tuple[bool, str]:
    """Kesilgan arxiv RAD ETILSINMI?

    Eng ko'p uchraydigan holat: disk to'ldi yoki jarayon o'ldi va `.gz`
    yarmida tugadi. Bunday zaxira katalogda «bor» bo'lib turadi, hajmi ham
    ishonarli — yaroqsizligi esa faqat tiklash kunida bilinadi.
    """
    with _tmp_dir() as tmp:
        good = Path(tmp) / "pg-good.sql.gz"
        _make_dump(good, complete=True)
        chopped = Path(tmp) / "pg-truncated.sql.gz"
        raw = good.read_bytes()
        chopped.write_bytes(raw[: len(raw) // 2])
        code, out = _run_backup_verify(chopped)
        if code == 0:
            return False, (
                "backup/kesilgan: buzuq arxiv O'TKAZILDI (exit 0) — tekshiruv o'lik"
            )
        if "gzip -t" not in out:
            return False, (
                f"backup/kesilgan: yiqildi, lekin sabab ko'rinmadi — {out.strip()[:120]}"
            )
        return True, "backup/kesilgan: buzuq arxiv tutildi (exit 1)"


def neg_backup_missing_trailer() -> tuple[bool, str]:
    """Gzip BUTUN, lekin dump chala — tutilsinmi?

    ⚠️ Xavfliroq sinf: `gzip -t` bunday faylni «sog'lom» deydi, chunki
    arxivning o'zi butun. Yo'q narsa — `pg_dump` ning yakuniy qatori, ya'ni
    dump o'rtada uzilgan. Faqat `gzip -t` ga tayangan tekshiruv buni
    jimgina o'tkazib yuborardi, va zaxira «yashil» bo'lib qolardi.
    """
    with _tmp_dir() as tmp:
        half = Path(tmp) / "pg-notrailer.sql.gz"
        _make_dump(half, complete=False)
        code, out = _run_backup_verify(half)
        if code == 0:
            return False, (
                "backup/chala: yakuniy qatorsiz dump O'TKAZILDI (exit 0) — "
                "tekshiruv o'lik"
            )
        if "chala" not in out:
            return False, (
                f"backup/chala: yiqildi, lekin sabab ko'rinmadi — {out.strip()[:120]}"
            )
        return True, "backup/chala: yakuniy qatorsiz dump tutildi (exit 1)"


def neg_backup_good_dump_passes() -> tuple[bool, str]:
    """Ijobiy nazorat: BUTUN dump o'tishi SHART.

    Hamma narsani rad etadigan tekshiruv yuqoridagi ikkala salbiy testdan
    ham o'tadi va baribir foydasiz bo'ladi: zaxira har kuni «yaroqsiz» deb
    qichqirsa, odam uni o'chirib qo'yadi. `workers` va `ci` guruhlarida ham
    shu sababdan yashil yo'l alohida tekshiriladi.
    """
    with _tmp_dir() as tmp:
        good = Path(tmp) / "pg-good.sql.gz"
        _make_dump(good, complete=True)
        code, out = _run_backup_verify(good)
        if code != 0:
            return False, (
                f"backup/butun: sog'lom dump exit {code} berdi (0 kerak) — "
                f"{out.strip()[:120]}"
            )
        if "dump butun" not in out:
            return False, "backup/butun: tasdiq xabari ko'rinmadi"
        return True, "backup/butun: sog'lom dump o'tdi (exit 0)"


# ── monitor (Windows tunnel/origin monitori) ─────────────────────────────
#
# Nega alohida guruh: 2026-09-15 da sayt ildizi 200 qaytarardi, API esa
# 503 — sahifalar ochilardi, lekin brauzerdagi HAR BIR API chaqiruvi
# yiqilardi (kirish, yuborish, jadval). `monitor.ps1` faqat ildizni
# tekshirgani uchun YASHIL qoldi va avariya o'z-o'zidan tuzalmadi. Ya'ni
# bu «tekshiruv o'lik edi» sinfining aynan o'zi — faqat CI da emas,
# ishlab turgan tizimda.
#
# ⚠️ Bu testlar HECH QACHON haqiqiy konteynerni yoki tunnelni qayta ishga
# tushirmaydi. Taqiq `monitor.ps1` ning O'ZIDA: stub berilganda u dry-run
# ga MAJBURIY o'tadi, ya'ni xavfsizlik testning ehtiyotkorligiga tashlab
# qo'yilmagan. Ish katalogi ham vaqtinchalik joyga buriladi — haqiqiy
# `.handoff/monitor.log` va ogohlantirish fayli tegilmaydi.

POWERSHELL_MISSING = "powershell topilmadi"

MONITOR_CASES = {
    "API yolg'iz yiqilsa tutilsin",
    "ikkala manzil 200 bo'lsa yashil",
    "qatlam o'qilmasa exit 2, «yashil» emas",
    "konteyner yiqilishi ko'prik deb o'qilmasin",
    "ichkarida javob yo'q bo'lsa restart qilinmasin",
    "handoff qoidasi saqlansin",
}
"""Windows'ga bog'liq salbiy testlarning yorlig'i (`main()` da ishlatiladi)."""

#: Hamma qatlam sog'lom.
HTTP_HEALTHY = (
    "public-web\t200\topen\n"
    "public-api\t200\topen\n"
    "origin-web\t200\topen\n"
    "origin-api\t200\topen\n"
)

#: 2026-09-15 avariyasi: sahifa ochiladi, API yiqilgan. Origin porti TCP
#: ulanishni QABUL QILADI, lekin HTTP 000 qaytaradi — aynan shu juftlik
#: o'lgan host port ko'prigini boshqa hamma narsadan ajratadi.
HTTP_API_ONLY_OUTAGE = (
    "public-web\t200\topen\n"
    "public-api\t503\topen\n"
    "origin-web\t200\topen\n"
    "origin-api\t000\topen\n"
)


def _powershell() -> str | None:
    """`powershell` ning to'liq yo'li, topilmasa `None`.

    ⚠️ Monitor — WINDOWS darvozasi. CI runner'i Linux (o'lchandi:
    `nsn-pc-rankwant|Linux|online`), ya'ni u yerda `powershell` yo'q.
    Guruhni «o'tdi» deb ko'rsatish yolg'on yashil bo'lardi, «yiqildi»
    deb ko'rsatish esa CI ni doimiy qizil qilardi — shuning uchun
    `main()` uni OCHIQ aytib o'tkazib yuboradi. Windows'da (pre-push
    hook, ya'ni monitor haqiqatan ishlaydigan mashina) guruh doim
    ishlaydi.
    """
    for candidate in (
        os.environ.get("POWERSHELL"),
        shutil.which("powershell"),
        shutil.which("pwsh"),
    ):
        if candidate and Path(candidate).exists():
            return str(candidate)
    return None


def _run_monitor(
    http: str,
    docker: str | None = None,
    owner: str = "windows",
    tunnel: str | None = None,
    unreadable: str | None = None,
) -> tuple[int, str]:
    """`tools/monitor.ps1` ni soxta o'lchovlar bilan ishga tushiradi.

    Tarmoqqa ham, docker'ga ham, R2 ga ham CHIQMAYDI: har bir qatlam
    stub muhit o'zgaruvchisi bilan almashtiriladi.
    """
    shell = _powershell()
    if shell is None:
        return 127, POWERSHELL_MISSING
    env = dict(os.environ)
    env["MONITOR_HTTP_STUB"] = http
    env["MONITOR_OWNER_STUB"] = owner
    # Ikki qavat himoya: stub berilgani ham dry-run ni yoqadi, bu esa
    # uni ALOHIDA va ochiq talab qiladi.
    env["MONITOR_DRY_RUN"] = "1"
    for key, value in (
        ("MONITOR_DOCKER_STUB", docker),
        ("MONITOR_TUNNEL_STUB", tunnel),
        ("MONITOR_FORCE_UNREADABLE", unreadable),
    ):
        if value is None:
            env.pop(key, None)
        else:
            env[key] = value
    with tempfile.TemporaryDirectory() as work:
        env["MONITOR_WORK_DIR"] = work
        proc = subprocess.run(
            [
                shell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "tools" / "monitor.ps1"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def monitor_precondition() -> str | None:
    """Monitor o'zgarmagan, sog'lom holatda `exit 0` berishini talab qiladi.

    `None` — hammasi joyida. Aks holda sabab qaytariladi.

    Old shart BIR MARTA tekshiriladi: `powershell` topilmasa har bir
    chaqiruv `127` qaytarardi va uni «buzuq holatni tutdi» deb o'qish
    oson — node tekshiruvidagi bilan aynan bir xil tuzoq.
    """
    if _powershell() is None:
        return f"monitor.ps1 o'lchanmadi — {POWERSHELL_MISSING} (Windows darvozasi)"
    code, out = _run_monitor(HTTP_HEALTHY)
    if code != 0:
        first = out.strip().splitlines()[:3]
        return (
            f"monitor.ps1 sog'lom holatda ham yiqildi (exit {code}): {' | '.join(first)}"
        )
    return None


def neg_monitor_api_only_outage() -> tuple[bool, str]:
    """Sayt 200, API yiqiq — tutilsinmi?

    ⚠️ AYNAN SHU holat o'tkazib yuborilgan (2026-09-15). Eski monitorda
    `$apiUrl` va `$originApi` e'lon qilingan edi-yu, HECH QAYERDA
    ishlatilmasdi; `Test-Once` faqat `$siteUrl` ga qarardi. Sayt 200
    bo'lgani uchun u darhol «OK» qaytarardi va qolgan qatlamlarga
    umuman qaramasdi.
    """
    code, out = _run_monitor(
        HTTP_API_ONLY_OUTAGE,
        docker="rankwant-api-1\trunning\thealthy\t200",
    )
    if code == 0:
        return False, (
            "monitor/API yolg'iz: sayt 200 bo'lgani uchun O'TKAZILDI (exit 0) — "
            "monitor o'lik"
        )
    if "DEAD BRIDGE" not in out:
        return False, (
            f"monitor/API yolg'iz: yiqildi, lekin qatlam nomi yo'q — {out.strip()[:160]}"
        )
    if "rankwant-api-1" not in out:
        return False, "monitor/API yolg'iz: qaysi konteyner ekani aytilmadi"
    if "DRY RUN" not in out:
        return False, (
            "monitor/API yolg'iz: dry-run emas — test haqiqiy konteynerni qayta "
            "ishga tushirishi mumkin edi"
        )
    return True, (
        "monitor/API yolg'iz: DEAD BRIDGE tutildi, faqat api konteyneri (exit 1)"
    )


def neg_monitor_healthy_gate() -> tuple[bool, str]:
    """Ijobiy nazorat: hamma narsa sog'lom bo'lsa YASHIL va hech narsa qilinmasin.

    Har doim qichqiradigan monitor BARCHA salbiy testlardan o'tadi va
    baribir foydasiz bo'ladi: har 5 daqiqada yolg'on ogohlantirish
    yozadi, keyin uni o'chirib qo'yishadi.
    """
    code, out = _run_monitor(HTTP_HEALTHY)
    if code != 0:
        return False, f"monitor/yashil: sog'lom holat exit {code} berdi (0 kerak)"
    if "OK" not in out:
        return False, "monitor/yashil: `OK` qatori jurnalga yozilmadi"
    if "restart" in out:
        return False, "monitor/yashil: sog'lom holatda qayta ishga tushirishga urindi"
    return True, "monitor/yashil: ikkala manzil 200, hech narsa qilinmadi (exit 0)"


def neg_monitor_unreadable_is_not_green() -> tuple[bool, str]:
    """Qatlam o'qilmasa — «sog'lom» emas, «o'lchab bo'lmadi» bo'lsinmi?

    ⚠️ `check_workers.sh` va `check_ci.sh` bilan bir xil shartnoma:
    `exit 2`. `0` bo'lsa o'lchanmagan holat yashil deb o'qiladi; `1`
    bo'lsa odam mavjud bo'lmagan nosozlikni tuzatishga urinadi.
    """
    code, out = _run_monitor(
        HTTP_API_ONLY_OUTAGE,
        docker="rankwant-api-1\trunning\thealthy\t200",
        unreadable="docker",
    )
    if code == 0:
        return False, (
            "monitor/o'qilmadi: exit 0 — o'lchanmagan qatlam «yashil» deb o'qildi"
        )
    if code != 2:
        return False, f"monitor/o'qilmadi: exit {code} (2 kerak edi)"
    if "UNMEASURED" not in out:
        return False, "monitor/o'qilmadi: `UNMEASURED` qatlami aytilmadi"
    if "restart" in out:
        return False, "monitor/o'qilmadi: o'lchamasdan turib tiklashga urindi"
    return True, "monitor/o'qilmadi: exit 2 va hech narsa qilinmadi"


def neg_monitor_container_down_is_not_bridge() -> tuple[bool, str]:
    """Konteyner yiqilgani «o'lgan ko'prik» deb o'qilmasinmi?

    Qatlamlarni ajratishning butun ma'nosi shu: ikkalasida ham origin
    javob bermaydi, lekin DAVOSI boshqa. To'xtagan konteynerni
    `restart` qilish — noto'g'ri joyni tuzatish.
    """
    code, out = _run_monitor(
        "public-web\t200\topen\n"
        "public-api\t503\tclosed\n"
        "origin-web\t200\topen\n"
        "origin-api\t000\tclosed\n",
        docker="rankwant-api-1\texited\tnone\t000",
    )
    if code != 1:
        return False, f"monitor/konteyner: exit {code} (1 kerak edi)"
    if "CONTAINER DOWN" not in out:
        return False, f"monitor/konteyner: qatlam nomi yo'q — {out.strip()[:160]}"
    if "DEAD BRIDGE" in out:
        return False, (
            "monitor/konteyner: to'xtagan konteyner «o'lgan ko'prik» deb o'qildi"
        )
    return True, "monitor/konteyner: CONTAINER DOWN ko'prikdan ajratildi (exit 1)"


def neg_monitor_app_down_is_not_restarted() -> tuple[bool, str]:
    """Ichkarida ham javob yo'q bo'lsa — qayta ishga tushirilmasinmi?

    ⚠️ Restart universal bolg'a EMAS. Ilova xatosida konteynerni qayta
    ishga tushirish sababni yashiradi va avariyani cho'zadi: har 5
    daqiqada qayta ko'tariladi, har safar yana yiqiladi — jurnalda esa
    faqat restart qatorlari qoladi.
    """
    code, out = _run_monitor(
        HTTP_API_ONLY_OUTAGE,
        docker="rankwant-api-1\trunning\thealthy\t000",
    )
    if code != 1:
        return False, f"monitor/ilova: exit {code} (1 kerak edi)"
    if "APP DOWN" not in out:
        return False, f"monitor/ilova: qatlam nomi yo'q — {out.strip()[:160]}"
    if "restart" in out:
        return False, (
            "monitor/ilova: ichkarida javob yo'q, lekin restart qilishga urindi"
        )
    return True, "monitor/ilova: APP DOWN tutildi, restart QILINMADI (exit 1)"


def neg_monitor_handoff_guard_holds() -> tuple[bool, str]:
    """Egalik boshqa tizimda bo'lsa — hech narsa tiklanmasinmi?

    ⚠️ Bu monitorning eng muhim cheklovi: Linux live paytida Windows
    tunnelni ko'tarsa, ikki tomon bir vaqtda live bo'lardi va ikki baza
    jimgina ajralib ketardi. Yangi qatlam mantig'i uni buzmasligi
    SHART — shuning uchun qoida alohida test bilan qotirilgan.
    """
    code, out = _run_monitor(
        "public-web\t503\tclosed\npublic-api\t503\tclosed\n",
        docker="rankwant-api-1\texited\tnone\t000",
        owner="linux",
        tunnel="down",
    )
    if code != 0:
        return False, f"monitor/handoff: exit {code} (0 kerak edi — yiqilish kutilgan)"
    if "NOT LIVE" not in out:
        return False, f"monitor/handoff: sabab aytilmadi — {out.strip()[:160]}"
    if "restart" in out or "TUNNEL DOWN" in out:
        return False, "monitor/handoff: live BO'LMAGAN tizimda tiklashga urindi"
    return True, "monitor/handoff: owner=linux — hech narsa tiklanmadi (exit 0)"


def neg_ordering_missing_tiebreaker() -> tuple[bool, str]:
    """Tiebreaker'siz `ordering` — tutilsinmi?

    ⚠️ Bu sinf bir marta o'tkazib yuborilgan: `test_qidiruv_va_tartib`
    5 ishga tushirishning 1 tasida yiqilardi, sabab esa SQL tartibining
    beqarorligi edi. Test «flaky» deb yozib qo'yilsa, haqiqiy xato
    (sahifalash beqarori — bir odam ikki sahifada) yashirin qolardi.
    """
    path = ROOT / "apps/api/duels/staff_views.py"
    old = 'ordering: ClassVar[list[str]] = ["-created_at", "-pk"]'
    if old not in path.read_bytes().decode("utf-8"):
        return False, "ordering: sinov uchun qator topilmadi"
    with Mutation(path, old, 'ordering: ClassVar[list[str]] = ["-created_at"]'):
        return expect_fail("ordering", "ordering/tiebreaker yo'q")


def neg_ordering_fields_not_confused() -> tuple[bool, str]:
    """`ordering_fields` (ko'p maydonli) qoidaga TUSHMASLIGI kerak.

    Ijobiy nazorat: qoida faqat `ordering` ni ko'rsin. Aks holda har
    yangi saralanadigan maydon qo'shilsa CI qizarardi va odam qoidani
    o'chirib qo'yardi.
    """
    path = ROOT / "apps/api/duels/staff_views.py"
    old = 'ordering_fields: ClassVar[list[str]] = ["created_at", "start_at", "status"]'
    if old not in path.read_bytes().decode("utf-8"):
        return False, "ordering_fields: sinov uchun qator topilmadi"
    with Mutation(path, old, 'ordering_fields: ClassVar[list[str]] = ["created_at"]'):
        code, _out = run_check("ordering")
        if code != 0:
            return False, "ordering_fields: qoida `ordering_fields` ni ham ushlab qoldi"
    return True, "ordering_fields: qoida faqat `ordering` ga qaraydi"


# ── tooling: Windows darvozasi ───────────────────────────────────────────
#
# Bu ikki sinf 2026-09-15 da push'ni to'sdi va IKKALASI ham kodga emas,
# darvozaning O'ZIGA tegishli edi: noto'g'ri interpretator tanlandi va
# salbiy testlar begona fayllarni qayta yozdi. Shuning uchun ular ham
# xuddi tekshiruvlar kabi salbiy test bilan qo'riqlanadi.


STORE_STUB = (
    "#!/bin/sh\n"
    "echo 'Python was not found; run without arguments to install from the"
    " Microsoft Store' >&2\n"
    "exit 9009\n"
)
"""Microsoft Store'ning `python3` alias stub'i — PATH'da bor, ishga tushmaydi."""


def _run_picker(path_dirs: list[str] | None = None) -> tuple[int, str]:
    """`tools/pick-python.sh` ni berilgan PATH bilan ishga tushiradi."""
    env = dict(os.environ)
    # Test PATH'ni o'lchaydi, shuning uchun qotirilgan pin olib tashlanadi.
    env.pop("PYTHON", None)
    if path_dirs is not None:
        env["PATH"] = os.pathsep.join(path_dirs)
    proc = subprocess.run(
        [_bash(), "tools/pick-python.sh"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def neg_picker_rejects_store_stub() -> tuple[bool, str]:
    """PATH'da faqat Store stub'i bo'lsa — XATO bo'lsinmi?

    ⚠️ Aynan shu holat push'ni to'sdi. Eski mantiq `command -v python3` ga
    tayanardi: stub PATH'da bor va bajariladigan, ya'ni u TANLANARDI.
    Keyin har bir tekshiruv «Python was not found» bilan yiqilardi va
    hisobotda bu KOD nuqsoni bo'lib ko'rinardi.

    Talab: stub qabul qilinmasin. Ishlaydigan boshqa interpretator ham
    bo'lmasa — `exit 1`, ya'ni ochiq xato (jim `exit 0` emas).
    """
    with tempfile.TemporaryDirectory() as tmp:
        stub = Path(tmp) / "python3"
        stub.write_bytes(STORE_STUB.encode("utf-8"))
        stub.chmod(0o755)
        code, out = _run_picker([tmp])
    if code == 0:
        return False, (
            "picker/stub: Store stub'i TANLANDI (exit 0) — "
            f"«{out.strip()[:60]}»"
        )
    if code != 1:
        return False, f"picker/stub: exit {code} (1 kerak edi)"
    return True, "picker/stub: ishga tushmaydigan stub rad etildi (exit 1)"


def neg_picker_finds_working_python() -> tuple[bool, str]:
    """Ijobiy nazorat: haqiqiy interpretator TOPILSIN va ishlasin.

    Hamma narsani rad etadigan picker yuqoridagi testdan o'tardi va
    darvozani butunlay o'chirib qo'yardi — shuning uchun teskari tomon
    ham o'lchanadi: chiqarilgan yo'l haqiqatan ishga tushishi shart.
    """
    code, out = _run_picker()
    if code != 0:
        return False, f"picker/ishlaydi: exit {code} — interpretator topilmadi"
    chosen = out.strip().splitlines()[0] if out.strip() else ""
    if not chosen:
        return False, "picker/ishlaydi: exit 0, lekin yo'l chiqarilmadi"
    probe = subprocess.run(
        [chosen, "-c", "print('ok')"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if probe.returncode != 0 or "ok" not in (probe.stdout or ""):
        return False, f"picker/ishlaydi: `{chosen}` ishga tushmadi"
    return True, f"picker/ishlaydi: `{Path(chosen).name}` tanlandi va ishladi"


def neg_mutation_restores_bytes() -> tuple[bool, str]:
    """Mutatsiyadan keyin fayl BAYT-ANIQ qaytarilsinmi?

    ⚠️ 2026-09-15: bitta salbiy test yurishidan keyin `git status` 19 ta
    begona faylni «o'zgargan» deb ko'rsatdi. Mazmun bir xil edi — faqat
    satr oxirlari LF dan CRLF ga o'tgan, chunki `write_text` matn
    rejimida `\\n` ni `os.linesep` ga tarjima qiladi.

    Bu jim buzilish: push toza deb o'ylagan odam 19 ta faylni tasodifan
    commit qilishi mumkin. Shuning uchun test mazmunni emas, BAYTLARNI
    taqqoslaydi va ataylab CRLF ham, LF ham bor faylni oladi.
    """
    original = b"birinchi\r\nikkinchi\nuchinchi\r\n"
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "satr-oxirlari.txt"
        probe.write_bytes(original)
        with Mutation(probe, "ikkinchi", "IKKINCHI"):
            during = probe.read_bytes()
        after = probe.read_bytes()
    # Old shart: mutatsiya HAQIQATAN yozilganmi? Aks holda test bo'sh
    # bo'lardi — hech narsa o'zgarmasa baytlar albatta mos keladi.
    if b"IKKINCHI" not in during:
        return False, "mutatsiya: o'zgarish yozilmadi — test hech narsa o'lchamadi"
    if after != original:
        return False, f"mutatsiya baytlarni o'zgartirdi: {original!r} → {after!r}"
    return True, "mutatsiya: CRLF va LF bayt-aniq qaytarildi"


def neg_checker_survives_narrow_stdout() -> tuple[bool, str]:
    """Chiqish UTF-8 bo'lmagan oqimga ketsa tekshiruv qulamasinmi?

    ⚠️ 2026-09-15 da o'lchandi: 10 ta `check_*.py` dan 8 tasi chiqish
    QUVURGA yo'naltirilganda `UnicodeEncodeError` bilan qulardi — Windows
    quvur uchun `cp1252` beradi, tekshiruvlar esa `✓` chiqaradi.

    Bu shunchaki noqulaylik emas, YOLG'ON YASHIL manbai: `check_negative`
    bolalarni `capture_output=True` bilan, ya'ni quvur orqali chaqiradi.
    Qulagan bola nolga teng bo'lmagan kod qaytaradi va `expect_fail` buni
    «buzuq holatni tutdi» deb o'qiydi — mutatsiya umuman tekshirilmagan
    bo'lsa ham test yashil bo'lardi.

    Nosozlik `PYTHONIOENCODING=cp1252` bilan ATAYLAB qayta yasaladi: shu
    tarzda test Windows'da ham, Linux'da ham bir xil ma'noga ega bo'ladi
    (aks holda UTF-8 lokalda u bo'sh o'tardi). Tuzatish skriptning
    O'ZIDA bo'lishi kerak — chaqiruvchining muhitida emas.

    ⚠️ HAR BIR tekshiruv sinaladi, bitta vakil emas. Ilgari bu yerda faqat
    `check_ordering.py` turardi va 2026-09-16 da ikkita YANGI tekshiruv
    (`check_icons.py`, `check_markup_cookie.py`) himoyasiz qo'shildi:
    test ularni ko'rmadi, ikkalasi ham quvur ostida quladi va Windows'da
    push'ni to'sdi. Vakilga qarash yangi fayl uchun kafolat bermaydi.
    """
    env = dict(os.environ)
    env.pop("PYTHONUTF8", None)
    env["PYTHONIOENCODING"] = "cp1252"
    # `check_negative.py` ning o'zi chiqarilgan: u bu to'plamni qayta
    # ishga tushirib, cheksiz rekursiyaga tushardi.
    scripts = sorted(
        p.name for p in (ROOT / "tools").glob("check_*.py") if p.name != "check_negative.py"
    )
    if len(scripts) < 5:
        return False, f"tor oqim: tekshiruvlar topilmadi ({len(scripts)} ta)"
    # `check_deploy_window.py` asks the live API. On 2026-09-17 the site was
    # down after a power cut, the script correctly answered exit 2 and this
    # case turned CI red on `main`; a live contest would do the same with
    # exit 1. The stub keeps the verdict about the encoding, not production.
    # `check_deploy_gate.py` asks GitHub whether `main` CI is green; red CI would
    # fail this case for a reason that has nothing to do with encoding. A green
    # fixture keeps its `✓` line in the test.
    with stub_api(live=False) as base, tempfile.TemporaryDirectory() as tmp:
        env["RANKWANT_API_BASE"] = base
        runs = Path(tmp) / "runs.json"
        runs.write_text(json.dumps(_GATE_GREEN), encoding="utf-8")
        # `check_after_reboot.py` measures this machine (docker, gh, scheduled
        # tasks); on the Linux CI runner it rightly exits 2. Healthy facts keep
        # this case about the encoding of its `✓` lines.
        facts = Path(tmp) / "facts.json"
        facts.write_text(json.dumps(_ar_facts()), encoding="utf-8")
        # The gate also refuses to deploy while a compose file is uncommitted, which
        # this suite's own mutations can be. A clean fixture keeps the case about encoding.
        compose = Path(tmp) / "compose.json"
        compose.write_text("[]", encoding="utf-8")
        extra = {
            "check_deploy_gate.py": [
                "--head", _GATE_SHA, "--main", _GATE_SHA, "--runs", str(runs),
                "--compose-status", str(compose),
            ],
            "check_after_reboot.py": ["--facts", str(facts)],
        }
        for name in scripts:
            proc = subprocess.run(
                [PY, f"tools/{name}", *extra.get(name, [])],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
            out = (proc.stdout or "") + (proc.stderr or "")
            if "UnicodeEncodeError" in out:
                return False, f"tor oqim: {name} O'Z chiqishida quladi (UnicodeEncodeError)"
            if proc.returncode != 0:
                return False, f"tor oqim: {name} exit {proc.returncode} berdi (0 kerak)"
    return True, f"tor oqim: {len(scripts)} ta tekshiruv UTF-8 ga majburladi va o'tdi"


def neg_hook_gates_new_branch() -> tuple[bool, str]:
    """Upstream'siz branchda darvoza hammasini o'tkazib yubormasinmi?

    ⚠️ 2026-09-15 da o'lchandi: hook tekshiriladigan fayllar ro'yxatini
    `@{upstream}` dan olardi. Yangi branchda upstream hali YO'Q, `range`
    esa jimgina `HEAD` ga tushardi — toza daraxtda
    `git diff --name-only HEAD` BO'SH qaytaradi, va hook keyingi qatorda
    `exit 0` qilardi.

    Ya'ni har yangi branchning BIRINCHI push'i umuman tekshirilmay
    o'tardi: darvoza e'lon qilingan, lekin jonsiz. Bu nodir chekka holat
    emas — har bir yangi branch aynan shu yo'ldan o'tadi.

    Sinov haqiqiy repo'ga TEGMAYDI: vaqtinchalik repo yasaladi, unda na
    upstream, na `origin/main` bor — eng yomon holat.
    """
    hook = ROOT / ".githooks/pre-push"
    picker = ROOT / "tools/pick-python.sh"
    if not hook.exists() or not picker.exists():
        return False, "hook: `.githooks/pre-push` yoki picker topilmadi"

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        (repo / ".githooks").mkdir()
        (repo / "tools").mkdir()
        (repo / ".githooks/pre-push").write_bytes(hook.read_bytes())
        (repo / "tools/pick-python.sh").write_bytes(picker.read_bytes())
        (repo / "muhim.py").write_bytes(b"print('x')\n")

        # ⚠️ `GIT_*` MEROSINI UZAMIZ. Git hook'ni chaqirganda bolalarga
        # `GIT_DIR`, `GIT_INDEX_FILE` va boshqalarni beradi. Ular qolsa
        # quyidagi `git init` / `add` / `commit` vaqtinchalik katalogda
        # EMAS, haqiqiy repoda bajariladi — `cwd` ahamiyatsiz bo'lib
        # qoladi. 2026-09-16 da aynan shu yuz berdi: push paytida hook shu
        # testni chaqirdi, branchda «birinchi» nomli commit paydo bo'lib
        # repodagi hamma faylni o'chirdi va u PR'ga ketdi. Ustiga test
        # YOLG'ON YASHIL edi — `--print-files` haqiqiy repodagi 990 faylni
        # sanab, `muhim.py` ni o'sha ro'yxatdan topdi.
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

        # Identity goes in with `-c`, never `git config`: a per-command setting is
        # not written to any file, so even a sandbox that leaks into the real
        # repository cannot leave `test@example.com` behind (2026-09-16).
        for cmd in (
            ["git", "init", "-q", "-b", "yangi-branch"],
            ["git", "add", "-A"],
            [*_SANDBOX_IDENTITY, "commit", "-q", "-m", "birinchi"],
        ):
            made = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, env=env)
            if made.returncode != 0:
                return False, f"hook: sinov repo'si yasalmadi — {' '.join(cmd)}"

        proc = subprocess.run(
            [_bash(), ".githooks/pre-push", "--print-files"],
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

    listed = [line for line in (proc.stdout or "").splitlines() if line.strip()]
    if not listed:
        return False, (
            "hook/yangi branch: fayl ro'yxati BO'SH — upstream'siz push "
            "tekshirilmay o'tardi (darvoza jonsiz)"
        )
    if "muhim.py" not in listed:
        return False, f"hook/yangi branch: `muhim.py` ro'yxatda yo'q — {listed[:3]}"
    # Ro'yxat SINOV repo'siniki bo'lishi shart. U yerda atigi uchta fayl
    # bor; yuzlab bo'lsa, haqiqiy repo aralashgan (yuqoridagi `GIT_*`
    # merosi) va test o'z maqsadini emas, boshqa narsani o'lchayotgan
    # bo'ladi — aynan shu holat yolg'on yashil bergan edi.
    if len(listed) > 5:
        return False, (
            f"hook/yangi branch: {len(listed)} fayl sanaldi, sinov repo'sida esa "
            "uchta — haqiqiy repo aralashdi (GIT_* merosi uzilmagan)"
        )
    return True, f"hook/yangi branch: {len(listed)} fayl tekshiruvga olindi"


# ── push guard ───────────────────────────────────────────────────────────

_SANDBOX_IDENTITY = ("git", "-c", "user.name=test", "-c", "user.email=test@example.com")
_REAL_IDENTITY = ("git", "-c", "user.name=Probe", "-c", "user.email=probe@rankwant.uz")
_ZERO = "0" * 40
_OVERRIDE_ENV = "RANKWANT_ALLOW_MAIN_PUSH"


@contextlib.contextmanager
def _push_sandbox() -> Iterator[tuple[Path, dict[str, str]]]:
    """A throwaway repository that git cannot escape.

    Inherited `GIT_*` (a hook exports GIT_DIR/GIT_INDEX_FILE) would send
    commands to the real repository; the ceiling stops discovery above the
    sandbox; an empty global config and no system config keep the machine's own
    identity (CI runner included) out of the result.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        empty = Path(tmp) / "empty.gitconfig"
        empty.touch()
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.pop(_OVERRIDE_ENV, None)
        env["GIT_CEILING_DIRECTORIES"] = tmp
        env["GIT_CONFIG_GLOBAL"] = str(empty)
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        _sandbox_run(repo, env, "git", "init", "-q", "-b", "work")
        yield repo, env


def _sandbox_run(repo: Path, env: dict[str, str], *cmd: str) -> str:
    proc = subprocess.run(
        list(cmd),
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if proc.returncode != 0:
        raise AssertionError(f"sinov repo'si: {' '.join(cmd)} — {proc.stderr.strip()}")
    return proc.stdout.strip()


def _sandbox_commit(
    repo: Path, env: dict[str, str], identity: tuple[str, ...], name: str
) -> str:
    (repo / f"{name}.txt").write_text(f"{name}\n", encoding="utf-8")
    _sandbox_run(repo, env, "git", "add", "-A")
    _sandbox_run(repo, env, *identity, "commit", "-q", "-m", name)
    return _sandbox_run(repo, env, "git", "rev-parse", "HEAD")


def _published(repo: Path, env: dict[str, str], sha: str) -> None:
    """Pretend the remote already has `sha`."""
    _sandbox_run(repo, env, "git", "update-ref", "refs/remotes/origin/main", sha)


def _run_push_guard(
    repo: Path, env: dict[str, str], stdin: str, extra: dict[str, str] | None = None
) -> tuple[int, str]:
    proc = subprocess.run(
        [PY, str(ROOT / "tools/push_guard.py"), "origin"],
        cwd=repo,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**env, **(extra or {})},
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def neg_push_guard_placeholder_author() -> tuple[bool, str]:
    """A new commit authored as test@example.com must be rejected."""
    with _push_sandbox() as (repo, env):
        _published(repo, env, _sandbox_commit(repo, env, _REAL_IDENTITY, "base"))
        bad = _sandbox_commit(repo, env, _SANDBOX_IDENTITY, "bad")
        code, out = _run_push_guard(repo, env, f"refs/heads/work {bad} refs/heads/work {_ZERO}\n")
    if code != 1:
        return False, f"push_guard/muallif: soxta muallif exit {code} berdi (1 kerak)"
    if bad[:7] not in out:
        return False, "push_guard/muallif: rad etildi, lekin commit nomlanmadi"
    return True, "push_guard/muallif: test@example.com bilan commit rad etildi"


def neg_push_guard_real_author_passes() -> tuple[bool, str]:
    """Positive control: a real author pushing a feature branch is allowed."""
    with _push_sandbox() as (repo, env):
        _published(repo, env, _sandbox_commit(repo, env, _REAL_IDENTITY, "base"))
        good = _sandbox_commit(repo, env, _REAL_IDENTITY, "good")
        code, out = _run_push_guard(repo, env, f"refs/heads/work {good} refs/heads/work {_ZERO}\n")
    if code != 0:
        tail = out.strip()[-160:]
        return False, f"push_guard/yashil: haqiqiy muallif exit {code} berdi (0 kerak) — {tail}"
    return True, "push_guard/yashil: haqiqiy muallif o'tkazildi (exit 0)"


def neg_push_guard_published_history_ignored() -> tuple[bool, str]:
    """Placeholder commits the remote already has must not block later pushes."""
    with _push_sandbox() as (repo, env):
        _published(repo, env, _sandbox_commit(repo, env, _SANDBOX_IDENTITY, "published"))
        good = _sandbox_commit(repo, env, _REAL_IDENTITY, "good")
        code, _ = _run_push_guard(repo, env, f"refs/heads/work {good} refs/heads/work {_ZERO}\n")
    if code != 0:
        return False, f"push_guard/tarix: remote'dagi eski commit push'ni to'sdi (exit {code})"
    return True, "push_guard/tarix: e'lon qilingan eski commit hisobga olinmadi"


def neg_push_guard_main_rejected() -> tuple[bool, str]:
    """A direct update of refs/heads/main must be rejected."""
    with _push_sandbox() as (repo, env):
        base = _sandbox_commit(repo, env, _REAL_IDENTITY, "base")
        _published(repo, env, base)
        good = _sandbox_commit(repo, env, _REAL_IDENTITY, "good")
        code, out = _run_push_guard(repo, env, f"refs/heads/work {good} refs/heads/main {base}\n")
    if code != 1:
        return False, f"push_guard/main: to'g'ridan push exit {code} berdi (1 kerak)"
    if "PR" not in out:
        return False, "push_guard/main: rad etildi, lekin PR yo'li aytilmadi"
    return True, "push_guard/main: `main` ga to'g'ridan push rad etildi"


def neg_push_guard_override_allows_main() -> tuple[bool, str]:
    """Positive control: the documented emergency override really lets main through."""
    with _push_sandbox() as (repo, env):
        base = _sandbox_commit(repo, env, _REAL_IDENTITY, "base")
        _published(repo, env, base)
        good = _sandbox_commit(repo, env, _REAL_IDENTITY, "good")
        code, out = _run_push_guard(
            repo, env, f"refs/heads/work {good} refs/heads/main {base}\n", {_OVERRIDE_ENV: "1"}
        )
    if code != 0:
        tail = out.strip()[-160:]
        return False, f"push_guard/kalit: {_OVERRIDE_ENV}=1 bilan exit {code} (0 kerak) — {tail}"
    return True, f"push_guard/kalit: {_OVERRIDE_ENV}=1 favqulodda yo'lni ochdi"


def neg_push_guard_polluted_config() -> tuple[bool, str]:
    """A placeholder identity left in the repository config must stop the push."""
    with _push_sandbox() as (repo, env):
        _published(repo, env, _sandbox_commit(repo, env, _REAL_IDENTITY, "base"))
        good = _sandbox_commit(repo, env, _REAL_IDENTITY, "good")
        # Appended as text, not via `git config`: the test must not be able to
        # reproduce the leak it guards against.
        with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
            fh.write("[user]\n\temail = test@example.com\n")
        code, out = _run_push_guard(repo, env, f"refs/heads/work {good} refs/heads/work {_ZERO}\n")
    if code != 1:
        return False, f"push_guard/config: ifloslangan config exit {code} berdi (1 kerak)"
    if "--unset" not in out:
        return False, "push_guard/config: rad etildi, lekin tuzatish yo'li aytilmadi"
    return True, "push_guard/config: .git/config dagi test@example.com tutildi"


def neg_hook_wires_push_guard() -> tuple[bool, str]:
    """The real pre-push hook must call the guard — a guard nobody runs is dead."""
    needed = (
        ".githooks/pre-push",
        "tools/pick-python.sh",
        "tools/push_guard.py",
        "tools/_console.py",
    )
    if not all((ROOT / rel).exists() for rel in needed):
        return False, "hook/guard: kerakli fayllar topilmadi"
    with _push_sandbox() as (repo, env):
        for rel in needed:
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_bytes((ROOT / rel).read_bytes())
        head = _sandbox_commit(repo, env, _REAL_IDENTITY, "base")
        # Nothing differs from origin/main, so no gate runs: a non-zero exit can
        # only come from the guard, and a missing call ends in exit 0.
        _published(repo, env, head)
        proc = subprocess.run(
            [_bash(), ".githooks/pre-push", "origin", "https://example.invalid/rankwant.git"],
            cwd=repo,
            input=f"refs/heads/main {head} refs/heads/main {_ZERO}\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode == 0:
        return False, "hook/guard: `main` ga push hook'dan o'tib ketdi — guard chaqirilmagan"
    if "to'g'ridan-to'g'ri push yopiq" not in out:
        return False, f"hook/guard: hook yiqildi, lekin guard sababi emas — {out.strip()[-160:]}"
    return True, "hook/guard: pre-push `main` ga push'ni guard orqali rad etdi"


def _repo_fingerprint(repo: Path, env: dict[str, str] | None = None) -> str | None:
    """Local config (minus upstream bookkeeping) and the checked-out branch.

    `branch.*` is left out: `git push -u` in another checkout rewrites it and
    would raise a false alarm. None means git could not read the repository.
    """
    parts: list[str] = []
    for cmd in (["git", "config", "--local", "--list"], ["git", "symbolic-ref", "-q", "HEAD"]):
        proc = subprocess.run(
            cmd,
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if proc.returncode not in (0, 1):
            return None
        parts.append(
            "\n".join(line for line in proc.stdout.splitlines() if not line.startswith("branch."))
        )
    return "\x00".join(parts)


def neg_fingerprint_catches_config_write() -> tuple[bool, str]:
    """The suite tripwire must notice a config write and stay quiet without one."""
    with _push_sandbox() as (repo, env):
        first = _repo_fingerprint(repo, env)
        again = _repo_fingerprint(repo, env)
        with (repo / ".git" / "config").open("a", encoding="utf-8") as fh:
            fh.write("[user]\n\temail = test@example.com\n")
        after = _repo_fingerprint(repo, env)
    if first is None:
        return False, "barmoq izi: sinov repo'sini o'qib bo'lmadi"
    if first != again:
        return False, "barmoq izi: o'zgarishsiz holatda ham farq ko'rdi (doim qizil)"
    if after == first:
        return False, "barmoq izi: .git/config ga yozuvni ko'rmadi (tripwire o'lik)"
    return True, "barmoq izi: config yozuvi tutildi, o'zgarishsiz holat tinch"


def neg_web_unit_tests_catch_broken_cookie() -> tuple[bool, str]:
    """The Vitest gate must be alive: a broken markup-cookie parser turns it red."""
    web = ROOT / "apps/web"
    node = os.environ.get("NODE") or shutil.which("node")
    vitest = web / "node_modules/vitest/vitest.mjs"
    if not node or not vitest.exists():
        return False, "web/unit: node yoki vitest topilmadi — apps/web da `npm ci` kerak"

    def vitest_run() -> tuple[int, str]:
        proc = subprocess.run(
            [node, str(vitest), "run", "tests/unit/markup-cookie.test.ts"],
            cwd=web,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")

    # Precondition: without it a missing install would read as "caught".
    code, out = vitest_run()
    if code != 0:
        return False, f"web/unit: o'zgarmagan manbada ham yiqildi (exit {code}) — {out.strip()[-160:]}"
    path = web / "src/lib/prefs.ts"
    text = path.read_bytes().decode("utf-8")
    old = 'if (k === "s") out.statusStyle'
    if old not in text:
        return False, "web/unit: prefs.ts da mutatsiya langari topilmadi"
    with Mutation(path, old, 'if (k === "S") out.statusStyle'):
        code, out = vitest_run()
    if code == 0:
        return False, "web/unit: buzuq cookie parse'ni testlar O'TKAZDI (exit 0) — darvoza o'lik"
    if "markup cookie" not in out:
        return False, f"web/unit: yiqildi, lekin sabab cookie testi emas — {out.strip()[-160:]}"
    return True, "web/unit: buzuq cookie parse'ni Vitest tutdi (exit 1)"


def _decision_broken(rel: str, old: str, new: str, rule: str) -> tuple[bool, str]:
    """Break one owner decision in `rel`; check_decisions must name that rule."""
    path = ROOT / rel
    text = path.read_bytes().decode("utf-8")
    if old not in text:
        return False, f"decisions/{rule}: langar topilmadi ({rel})"
    with Mutation(path, old, new):
        code, out = run_check("decisions")
    if code != 1:
        return False, f"decisions/{rule}: buzilgan qaror exit {code} berdi (1 kerak)"
    if rule not in out:
        return False, f"decisions/{rule}: yiqildi, lekin boshqa sabab — {out.strip()[-160:]}"
    return True, f"decisions/{rule}: bekor qilingan qaror tutildi (exit 1)"


def neg_decisions_backup_offsite() -> tuple[bool, str]:
    return _decision_broken(
        "tools/backup.sh",
        'offsite="${RANKWANT_BACKUP_OFFSITE:-off}"',
        'offsite="${RANKWANT_BACKUP_OFFSITE:-auto}"',
        "zaxira faqat lokal",
    )


def neg_decisions_push_guard_unwired() -> tuple[bool, str]:
    return _decision_broken(
        ".githooks/pre-push",
        '"$root/tools/push_guard.py"',
        '"$root/tools/push_guard_off.py"',
        "main faqat PR orqali",
    )


def neg_decisions_hosted_runner() -> tuple[bool, str]:
    return _decision_broken(
        ".github/workflows/ci.yml",
        "runs-on: ubuntu-latest",
        "runs-on: [self-hosted, rankwant]",
        "CI testlari hosted",
    )


def neg_decisions_deploy_on_push() -> tuple[bool, str]:
    return _decision_broken(
        ".github/workflows/deploy.yml",
        "\non:\n  workflow_dispatch:",
        "\non:\n  push:\n    branches: [main]\n  workflow_dispatch:",
        "deploy faqat qo'lda",
    )


def neg_decisions_language_rule() -> tuple[bool, str]:
    return _decision_broken("CONTRIBUTING.md", "\n## Til\n", "\n## Tillar\n", "til qoidasi")


def neg_decisions_table_removed() -> tuple[bool, str]:
    return _decision_broken(
        "CLAUDE.md", "## Saidakbar aka qarorlari", "## Qarorlar", "qarorlar jadvali"
    )


def neg_decisions_locale_label_unbounded() -> tuple[bool, str]:
    """Endonim tor ekranda chegarasiz qolsa tutilsin.

    O'lchandi (320 px, `main` = 6486cd6): `max-w-[3rem]` olib tashlansa
    `Qaraqalpaqsha` til tugmasini 149 px qiladi va header 29 px toshadi
    (`O'zbekcha` +7 px, `Кыргызча` +6 px).
    """
    return _decision_broken(
        "apps/web/src/layout/LocaleSwitch.tsx",
        'className="min-w-0 max-w-[3rem] truncate text-theme-xs sm:max-w-[7.5rem]"',
        'className="min-w-0 truncate text-theme-xs sm:max-w-[7.5rem]"',
        "tor ekran 320 px ga sig'adi",
    )


def neg_decisions_locale_code_restored() -> tuple[bool, str]:
    """Tor ekranda til KODI qaytsa tutilsin.

    Kod endi triggerda ko'rinmaydi — endonim ko'rinadi. Kod qaytarilsa
    tor ekranda odam o'z tilini ko'rmaydi (tahlil B9), holbuki endonim
    `max-w` bilan chegaralanganda ham header 0 px toshadi.
    """
    return _decision_broken(
        "apps/web/src/layout/LocaleSwitch.tsx",
        "{currentLabel}\n        </span>",
        '{currentLabel}\n        </span>\n        <span className="text-theme-xs sm:hidden">'
        "{currentCode}</span>",
        "tor ekran 320 px ga sig'adi",
    )


def neg_decisions_locale_panel_not_anchored() -> tuple[bool, str]:
    """Panel tor ekranda viewport'ga bog'lanmasa tutilsin.

    O'lchandi (320 px): `fixed` bo'lmasa panel `absolute right-0 w-64`
    bo'lib chapga 44 px toshadi va BARCHA 11 bayroq `left = -32…-11` —
    ya'ni ko'rinmaydi.
    """
    return _decision_broken(
        "apps/web/src/layout/LocaleSwitch.tsx",
        ': "fixed mt-1"',
        ': "absolute mt-1"',
        "tor ekran 320 px ga sig'adi",
    )


def neg_decisions_locale_label_in_name_lost() -> tuple[bool, str]:
    """`aria-label` ko'rinadigan matnni yo'qotsa tutilsin.

    Ko'rinadigan matn — ENDONIM (`Qaraqalpaqsha`), ya'ni `aria-label` uni
    o'z ichiga olmasa WCAG 2.5.3 («Label in Name») buziladi va Lighthouse
    `label-content-name-mismatch` beradi.
    """
    return _decision_broken(
        "apps/web/src/layout/LocaleSwitch.tsx",
        "aria-label={`${currentLabel} (${currentCode}) — ${t(locale, \"locale.switchLabel\")}`}",
        "aria-label={`${currentCode} — ${t(locale, \"locale.switchLabel\")}`}",
        "tor ekran 320 px ga sig'adi",
    )


def neg_decisions_locale_cookie_beats_link() -> tuple[bool, str]:
    """Cookie havoladan ustun bo'lsa tutilsin (qaror S5).

    Shoxobchalar almashtirilsa `?lang=ru` bilan kelgan odam qurilmasidagi
    tilni ko'radi — ya'ni ulashilgan havola o'z tilini olib kelmaydi.
    """
    return _decision_broken(
        "apps/web/src/i18n/resolve.ts",
        "  if (param !== null && isLocale(param)) return { locale: param, auto: false };\n"
        "  if (cookie !== null && isLocale(cookie)) return { locale: cookie, auto: false };",
        "  if (cookie !== null && isLocale(cookie)) return { locale: cookie, auto: false };\n"
        "  if (param !== null && isLocale(param)) return { locale: param, auto: false };",
        "til havolada ham keladi",
    )


def neg_decisions_locale_header_after_next() -> tuple[bool, str]:
    """Sarlavha `next()` dan keyin yozilsa tutilsin.

    Bu AYNAN o'sha jimgina buziladigan holat: `next()` `request.headers` ni
    chaqiruv paytida ko'chiradi (o'lchandi: `next@16.3.4`,
    `response.js:128`), ya'ni keyin yozilgan qiymat joriy render'ga
    yetib bormaydi va sahifa cookie tilida chiziladi.
    """
    return _decision_broken(
        "apps/web/src/proxy.ts",
        "  if (fromParam !== null) requestHeaders.set(LOCALE_HEADER, fromParam);\n"
        "\n"
        "  const response = boshqa_domen\n"
        "    ? NextResponse.redirect(\n"
        "        new URL(`${request.nextUrl.pathname}${request.nextUrl.search}`, canonical),\n"
        "        301,\n"
        "      )\n"
        "    : NextResponse.next({ request: { headers: requestHeaders } });",
        "  const response = boshqa_domen\n"
        "    ? NextResponse.redirect(\n"
        "        new URL(`${request.nextUrl.pathname}${request.nextUrl.search}`, canonical),\n"
        "        301,\n"
        "      )\n"
        "    : NextResponse.next({ request: { headers: requestHeaders } });\n"
        "  if (fromParam !== null) requestHeaders.set(LOCALE_HEADER, fromParam);",
        "til havolada ham keladi",
    )


def neg_decisions_locale_link_not_remembered() -> tuple[bool, str]:
    """Havoladagi til cookie'ga yozilmasa tutilsin (qaror S5b).

    Usiz havola faqat BIRINCHI sahifani tuzatadi: har bir ichki bosish
    qurilma tiliga qaytadi va ichki havolalarni o'zgartirish kerak bo'lardi.
    """
    return _decision_broken(
        "apps/web/src/proxy.ts",
        "    if (fromParam !== null) rememberLocale(response, fromParam);\n",
        "",
        "til havolada ham keladi",
    )


def neg_decisions_home_cache_ttl_dropped() -> tuple[bool, str]:
    """Mehmon `s-maxage=30` olib tashlansa tutilsin."""
    return _decision_broken(
        "apps/web/src/lib/home-cache.ts",
        '  "public, s-maxage=30, stale-while-revalidate=86400";',
        '  "public, s-maxage=0, stale-while-revalidate=86400";',
        "bosh sahifa mehmon CDN keshi",
    )


def neg_decisions_home_cache_logged_in_public() -> tuple[bool, str]:
    """Kirgan javob `public` bo'lsa tutilsin — shaxsiy HTML CDN'ga tushadi."""
    return _decision_broken(
        "apps/web/src/lib/home-cache.ts",
        'export const HOME_CACHE_PRIVATE = "private, no-store";',
        'export const HOME_CACHE_PRIVATE = "public, s-maxage=30";',
        "bosh sahifa mehmon CDN keshi",
    )


def neg_decisions_home_cache_proxy_unwired() -> tuple[bool, str]:
    """Keshlangan GET `/` yana eksperiment cookie yozsa tutilsin."""
    return _decision_broken(
        "apps/web/src/proxy.ts",
        "if (homeCache.assignExperiments) assignExperiments(request, response);",
        "assignExperiments(request, response);",
        "bosh sahifa mehmon CDN keshi",
    )


def neg_decisions_home_worker_catchall_restored() -> tuple[bool, str]:
    """Worker yana `rankwant.uz/*` ni tutsa tutilsin — GET `/` kvotani yeydi."""
    return _decision_broken(
        "services/maintenance-worker/wrangler.toml",
        '  { pattern = "rankwant.uz/a*", zone_name = "rankwant.uz" },',
        '  { pattern = "rankwant.uz/*", zone_name = "rankwant.uz" },',
        "bosh sahifa mehmon CDN keshi",
    )


def neg_decisions_locale_choice_keeps_param() -> tuple[bool, str]:
    """Qo'lda tanlov `?lang=` ni tozalamasa tutilsin.

    Parametr qoldirilsa proxy uni har render'da cookie'dan ustun qo'yadi,
    ya'ni odam ro'yxatdan boshqa tilni tanlaydi-yu sahifa eskisida qolaveradi.
    """
    return _decision_broken(
        "apps/web/src/layout/LocaleSwitch.tsx",
        "        url.searchParams.delete(LOCALE_PARAM);\n",
        "",
        "til havolada ham keladi",
    )


def neg_decisions_deploy_backup_after_migrate() -> tuple[bool, str]:
    """Zaxira migratsiyadan KEYIN qolsa tutilsin.

    Tartib buzilganda skript ishlaydi, natija esa noto'g'ri bo'ladi: sxema
    zaxirasiz o'zgaradi va Django'da «orqaga» migratsiya yo'qligi uchun
    qaytish yo'li qolmaydi. Mutatsiya `migrate` chaqiruvini zaxira
    qadamidan OLDIN qo'yadi — ya'ni birinchi uchragan `run --rm migrate`
    endi zaxiradan oldin turadi.
    """
    return _decision_broken(
        "tools/deploy.sh",
        'step "4/8 Migratsiyadan oldin zaxira (pg_dump)"',
        '"${COMPOSE[@]}" run --rm migrate || true\n'
        'step "4/8 Migratsiyadan oldin zaxira (pg_dump)"',
        "avtomatik deploy xavfsiz",
    )


def neg_decisions_deploy_freeze_after_lock() -> tuple[bool, str]:
    """Muzlatish qulfdan KEYIN tekshirilsa tutilsin.

    Aks holda muzlatilgan tizim qulfni band qiladi va boshqa agentning
    deploy'i «band» deb xato o'qiladi — ya'ni muzlatish o'z ishini
    qilmaydi, faqat boshqalarni to'xtatadi.
    """
    return _decision_broken(
        "tools/deploy.sh",
        "# ── Muzlatish kaliti ──",
        'mkdir "$LOCK" 2>/dev/null || true\n# ── Muzlatish kaliti ──',
        "avtomatik deploy xavfsiz",
    )


def neg_decisions_deploy_tag_after_up() -> tuple[bool, str]:
    """SHA teg `up` dan KEYIN qo'yilsa tutilsin.

    `up` konteynerlarni yangi obrazga o'tkazadi va eski obraz «dangling»
    bo'lib qoladi; keyin qo'yilgan teg o'shanga tushadi, ya'ni rollback
    NOTO'G'RI kodni qaytaradi. Buni faqat rollback paytida bilib olishardi.
    """
    return _decision_broken(
        "tools/deploy.sh",
        "# ── 4. Rollback nuqtasi — SHA teg ──",
        '"${COMPOSE[@]}" up -d --no-deps "${SERVICES[@]}" || true\n'
        "# ── 4. Rollback nuqtasi — SHA teg ──",
        "avtomatik deploy xavfsiz",
    )


def neg_decisions_auto_deploy_no_liveness() -> tuple[bool, str]:
    """Watcher konteynerlar tirikligini tekshirmasa tutilsin.

    `check_deploy.sh` konteyner YO'Q bo'lganda ham 0 qaytaradi (o'lchandi:
    `missing` faqat xabar uchun, `exit 1` esa `stale`/`envbad` da). Ya'ni
    stack yiqilgan bo'lsa watcher «ish yo'q» deb jim qolardi va sayt
    ko'tarilmagan holda qolaverardi.
    """
    return _decision_broken(
        "tools/auto_deploy.sh",
        "if all_up && bash tools/check_deploy.sh >/dev/null 2>&1; then",
        "if bash tools/check_deploy.sh >/dev/null 2>&1; then",
        "avtomatik deploy xavfsiz",
    )


def neg_decisions_auto_deploy_attempt_after_deploy() -> tuple[bool, str]:
    """Qayta urinish yozuvi deploy'dan KEYIN bo'lsa tutilsin.

    Urinish yiqilgandan keyin yozilsa, yiqilgan yurish har 5 daqiqada
    takrorlanadi: obraz qayta quriladi, disk to'ladi, log ko'miladi.
    """
    return _decision_broken(
        "tools/auto_deploy.sh",
        'record_attempt "$TARGET"',
        'bash tools/deploy.sh --yes || true\nrecord_attempt "$TARGET"',
        "avtomatik deploy xavfsiz",
    )


def neg_decisions_signin_label_wraps() -> tuple[bool, str]:
    """Kirish yorlig'i o'raladigan bo'lsa tutilsin.

    `whitespace-nowrap` olib tashlansa yorliq tor ekranda ikki qatorga
    bo'linadi (o'lchandi: 375 px da 88x40 px, 2 qator).
    """
    return _decision_broken(
        "apps/web/src/layout/UserMenu.tsx",
        'className="flex h-10 items-center gap-2 whitespace-nowrap rw-radius-sm rw-accent-bg px-4 text-theme-sm font-medium text-white transition"',
        'className="flex h-10 items-center gap-2 rw-radius-sm rw-accent-bg px-4 text-theme-sm font-medium text-white transition"',
        "tor ekran 320 px ga sig'adi",
    )


def neg_decisions_deploy_gate_unwired() -> tuple[bool, str]:
    return _decision_broken(
        "tools/deploy.sh",
        "tools/check_deploy_gate.py ||",
        "tools/check_deploy_gate_off.py ||",
        "deploy faqat yashil main'dan",
    )


def neg_decisions_security_on_pr() -> tuple[bool, str]:
    return _decision_broken(
        ".github/workflows/security.yml",
        "on:\n",
        "on:\n  pull_request:\n",
        "PR'da og'ir CI yo'q",
    )


def neg_decisions_smoke_on_pr() -> tuple[bool, str]:
    return _decision_broken(
        ".github/workflows/ci.yml",
        "&& github.event_name != 'pull_request' }}",
        "}}",
        "PR'da og'ir CI yo'q",
    )


def neg_decisions_runner2_profile_dropped() -> tuple[bool, str]:
    return _decision_broken(
        "tools/runner/docker-compose.runner.yml",
        '    profiles: ["second"]\n',
        "",
        "PR'da og'ir CI yo'q",
    )


def neg_decisions_runner_compose_label_dropped() -> tuple[bool, str]:
    return _decision_broken(
        "tools/runner/docker-compose.runner.yml",
        "${RUNNER_LABELS:-self-hosted,Linux,X64,rankwant,rankwant-container}",
        "${RUNNER_LABELS:-self-hosted,Linux,X64,rankwant-container}",
        "CI runner konteynerda",
    )


def neg_decisions_runner_entrypoint_label_dropped() -> tuple[bool, str]:
    # `rankwant-container` contains `rankwant` as text; the rule must not count it.
    return _decision_broken(
        "tools/runner/entrypoint.sh",
        '"${RUNNER_LABELS:=self-hosted,Linux,X64,rankwant,rankwant-container}"',
        '"${RUNNER_LABELS:=self-hosted,Linux,X64,rankwant-container}"',
        "CI runner konteynerda",
    )


def neg_decisions_deploy_skips_web() -> tuple[bool, str]:
    return _decision_broken(
        "tools/deploy.sh",
        "SERVICES=(api worker beat judge web)",
        "SERVICES=(api worker beat judge)",
        "deploy hamma servisni quradi",
    )


def neg_decisions_site_closed_to_search() -> tuple[bool, str]:
    return _decision_broken(
        "apps/web/src/lib/site.ts",
        "export const SITE_INDEXABLE = true;",
        "export const SITE_INDEXABLE = false;",
        "qidiruv ochiq, AI kraulerlar yopiq",
    )


def neg_decisions_ai_crawler_dropped() -> tuple[bool, str]:
    return _decision_broken(
        "apps/web/src/app/robots.ts",
        '  "GPTBot",\n',
        "",
        "qidiruv ochiq, AI kraulerlar yopiq",
    )


def neg_decisions_nav_eager_link() -> tuple[bool, str]:
    # A plain `next/link` back in the sidebar prefetches every item on sight.
    return _decision_broken(
        "apps/web/src/layout/AppSidebar.tsx",
        'import { IntentLink } from "@/components/ui/IntentLink";\n',
        'import { IntentLink } from "@/components/ui/IntentLink";\nimport Link from "next/link";\n',
        "navigatsiya prefetch'i niyatda",
    )


def neg_decisions_home_main_eager_link() -> tuple[bool, str]:
    # A plain `next/link` back on the homepage <main> prefetches in-view CTAs.
    return _decision_broken(
        "apps/web/src/app/page.tsx",
        'import { IntentLink } from "@/components/ui/IntentLink";\n',
        'import { IntentLink } from "@/components/ui/IntentLink";\nimport Link from "next/link";\n',
        "bosh sahifa <main> prefetch'i niyatda",
    )


def neg_decisions_intent_link_eager() -> tuple[bool, str]:
    # `IntentLink` itself going back to the default prefetch undoes it for all.
    return _decision_broken(
        "apps/web/src/components/ui/IntentLink.tsx",
        "prefetch={intent ? null : false}",
        "prefetch={null}",
        "navigatsiya prefetch'i niyatda",
    )


def neg_decisions_dormant_user_field_removed() -> tuple[bool, str]:
    # A dormant column tidied away as "unused" undoes the owner's ADR-0024 choice.
    return _decision_broken(
        "apps/api/core/models.py",
        "    duel_ready_until = models.DateTimeField(null=True, blank=True)\n",
        "",
        "User modeli tenglik maydonlari",
    )


def neg_decisions_dictionary_prop() -> tuple[bool, str]:
    # The dictionary back as a prop: 72 kB of every page again.
    return _decision_broken(
        "apps/web/src/app/layout.tsx",
        "dictionaryUrl={dictionary}",
        "dictionaryUrl={dictionary} dict={{}}",
        "lug'at alohida faylda",
    )


def neg_decisions_dictionary_not_cached() -> tuple[bool, str]:
    # Without `immutable` every page view asks for the file again.
    return _decision_broken(
        "apps/web/src/app/i18n/[file]/route.ts",
        '"public, max-age=31536000, immutable"',
        '"no-store"',
        "lug'at alohida faylda",
    )


def neg_decisions_dictionary_through_proxy() -> tuple[bool, str]:
    # Through the middleware the file gets `Vary: Accept-Language`.
    return _decision_broken(
        "apps/web/src/proxy.ts",
        "favicon.ico|i18n/).*)",
        "favicon.ico).*)",
        "lug'at alohida faylda",
    )


def neg_decisions_dictionary_cache_unsynced() -> tuple[bool, str]:
    # The promise cache outliving the eviction: returning to a language that was
    # already visited then injects no <script>, the registry stays empty and the
    # page renders raw keys (measured 2026-09-19 — 38 of them).
    return _decision_broken(
        "apps/web/src/i18n/LocaleProvider.tsx",
        "useEffect(() => keepOnly(locale), [locale]);",
        "useEffect(() => evictOtherLocales(locale), [locale]);",
        "lug'at qaytishda saqlanadi",
    )


# ── Content coverage is visible (owner decision 10, 2026-09-19) ──
#
# One test per clause of `content_coverage_visible`. Measured before the fix:
# the fallback worked in 8 places but the marker appeared in 2, and the `uz`
# dictionary was marked as a fallback on its own pages (unit test caught that:
# `localNameInfo(skill, "uz").locale` was `null`).


def neg_decisions_uz_marked_as_fallback() -> tuple[bool, str]:
    # `uz` is the source language: reading Uzbek is the correct answer, not a
    # fallback. Without the guard an `uz` chip lands on the Uzbek pages.
    return _decision_broken(
        "apps/web/src/i18n/messages.ts",
        "if (locale === DEFAULT_LOCALE) {",
        "if (false) {",
        "kontent qamrovi ko'rinadi",
    )


def neg_decisions_content_source_locales_widened() -> tuple[bool, str]:
    # Adding a locale to the source list claims its content names are
    # translated. Only uz/ru/en have columns, so the list must not grow.
    return _decision_broken(
        "apps/web/src/i18n/messages.ts",
        'export const CONTENT_NAME_LOCALES = ["uz", "ru", "en"] as const;',
        'export const CONTENT_NAME_LOCALES = ["uz", "ru", "en", "kk"] as const;',
        "kontent qamrovi ko'rinadi",
    )


def neg_decisions_content_marker_dropped() -> tuple[bool, str]:
    # The tag cloud: the name is rendered without the marker, so a `zh`
    # reader takes Uzbek for Chinese.
    return _decision_broken(
        "apps/web/src/components/ArchiveSidebar.tsx",
        "<ContentName",
        "{localName",
        "kontent qamrovi ko'rinadi",
    )


def neg_decisions_content_marker_dropped_in_activity() -> tuple[bool, str]:
    # Two call sites in one file: dropping either one must be caught, which is
    # why the rule counts render sites instead of just looking for the symbol.
    return _decision_broken(
        "apps/web/src/components/profile/ActivityTabs.tsx",
        "<ContentName",
        "{localName",
        "kontent qamrovi ko'rinadi",
    )


def neg_decisions_filter_chip_unmarked() -> tuple[bool, str]:
    # The topic filter chip: the flag is what carries "this name is Uzbek"
    # from the page into the shared `Option` component.
    return _decision_broken(
        "apps/web/src/components/ProblemFilters.tsx",
        "fallback={root.fallback}",
        "fallback={false}",
        "kontent qamrovi ko'rinadi",
    )


def neg_decisions_content_text_untranslated() -> tuple[bool, str]:
    # Native `<option>`: falling back to the untranslated form puts a bare
    # `uz` token in front of a reader who does not know what it means.
    return _decision_broken(
        "apps/web/src/components/settings/SkillsSection.tsx",
        "contentNameText(s, locale)",
        "localName(s, locale)",
        "kontent qamrovi ko'rinadi",
    )


def neg_decisions_selector_coverage_hidden() -> tuple[bool, str]:
    # The language list is the only place that warns BEFORE the choice is
    # made; hiding the marker sends the reader in blind.
    return _decision_broken(
        "apps/web/src/layout/LocaleSwitch.tsx",
        "hasContentNames(code)",
        "true",
        "kontent qamrovi ko'rinadi",
    )


def neg_decisions_deploy_lock_removed() -> tuple[bool, str]:
    return _decision_broken(
        "tools/deploy.sh",
        'if ! mkdir "$LOCK" 2>/dev/null; then',
        'if ! true "$LOCK" 2>/dev/null; then',
        "deploy faqat yashil main'dan",
    )


_TRIAL_WORKFLOW = (
    "name: Runner self-test\n"
    "on:\n  workflow_dispatch:\n"
    "jobs:\n  selftest:\n    runs-on: [self-hosted, rankwant-container]\n"
    "    steps:\n      - run: echo ok\n"
)


# Every file `check_decisions.py` reads, staged for the sandbox below.
#
# This list is a hand-kept duplicate of the paths that live inside that script,
# so it drifts. Measured 2026-09-19: a new rule made the check read
# `LocaleProvider.tsx`, the sandbox did not copy it, and two UNRELATED
# trial-label tests died in CI with exit 2 ("Qarorlarni o'qib bo'lmadi").
# `neg_decisions_sandbox_covers_reads` now fails locally and names the file.
_DECISIONS_SANDBOX_FILES = (
    "tools/check_decisions.py",
    "tools/_console.py",
    "tools/backup.sh",
    "tools/push_guard.py",
    "tools/deploy.sh",
    "tools/runner/docker-compose.runner.yml",
    "tools/runner/entrypoint.sh",
    "tools/runner/recreate.sh",
    "tools/runner_watchdog.py",
    ".githooks/pre-push",
    "CONTRIBUTING.md",
    "CLAUDE.md",
    # ADR-0023: the indexing decision lives in these two files.
    "apps/web/src/lib/site.ts",
    "apps/web/src/app/robots.ts",
    # Intent prefetch (2026-09-18): the layout chrome and the link itself.
    "apps/web/src/layout/AppSidebar.tsx",
    "apps/web/src/layout/AppTopNav.tsx",
    "apps/web/src/layout/AppFooter.tsx",
    "apps/web/src/layout/HeaderStatus.tsx",
    "apps/web/src/layout/UserMenu.tsx",
    "apps/web/src/components/ui/IntentLink.tsx",
    "apps/web/src/app/page.tsx",
    # Dictionary as a cached file (2026-09-18).
    "apps/web/src/app/layout.tsx",
    "apps/web/src/app/i18n/[file]/route.ts",
    "apps/web/src/proxy.ts",
    # ADR-0024: the User columns added for competitor parity.
    "apps/api/core/models.py",
    # Header fits 320 px (2026-09-18): the locale control and the sign-in
    # link. Missing from this list, the sandbox copy cannot be read and
    # `check_decisions.py` fails with exit 2 — which is how the omission
    # was caught.
    "apps/web/src/layout/LocaleSwitch.tsx",
    # Mobile drawer (2026-09-18): the trigger, the panel, the Escape
    # handler and the scroll lock. `AppSidebar.tsx` is already listed
    # above for the earlier header rule.
    "apps/web/src/layout/AppHeader.tsx",
    "apps/web/src/layout/AppShell.tsx",
    "apps/web/src/context/SidebarContext.tsx",
    # KPI grid 4-up from `lg` (2026-09-18): the card whose value steps down
    # while the columns are narrow. Without it the sandbox copy cannot be
    # read and the check exits 2 instead of testing anything.
    "apps/web/src/components/ui/Card.tsx",
    # Profile KPI grid steps at `xl` (2026-09-18): its content column is
    # narrow because of the 300 px sidebar, so it cannot copy the home
    # page's `lg`. Missing here, `check_decisions.py` exits 2.
    "apps/web/src/app/users/[username]/layout.tsx",
    # Difficulty range counts as one filter (2026-09-18): the badge reads
    # this file. Missing here, `check_decisions.py` exits 2 rather than
    # testing the rule.
    "apps/web/src/components/ProblemFilters.tsx",
    # Brand in the header, 3-column footer (2026-09-19): the rule reads the
    # single-source `BrandMark`. Missing here, `check_decisions.py` exits 2.
    "apps/web/src/layout/BrandMark.tsx",
    # Dictionary cache in step with eviction (2026-09-19): the rule reads
    # `keepOnly` and the promise cache inside the provider. Missing here,
    # `check_decisions.py` exits 2 instead of testing the rule.
    "apps/web/src/i18n/LocaleProvider.tsx",
    # Content coverage visible (2026-09-19): the source of truth for which
    # languages have content names, the shared marker, and every call site
    # that draws it. Missing here, `check_decisions.py` exits 2.
    "apps/web/src/i18n/messages.ts",
    "apps/web/src/components/ui/UzFallbackBadge.tsx",
    "apps/web/src/components/ArchiveSidebar.tsx",
    "apps/web/src/components/profile/AboutTab.tsx",
    "apps/web/src/components/profile/TopicStrength.tsx",
    "apps/web/src/components/profile/ActivityTabs.tsx",
    "apps/web/src/components/settings/SkillsSection.tsx",
    "apps/web/src/app/problems/page.tsx",
    # Locale in the URL (2026-09-19): the rule reads the single name source,
    # the pure precedence function and the server reader. Missing here,
    # `check_decisions.py` exits 2 instead of testing the rule.
    "apps/web/src/i18n/locale-params.ts",
    "apps/web/src/i18n/resolve.ts",
    "apps/web/src/i18n/server.ts",
    # Guest homepage CDN cache (2026-09-19). Missing here, the sandbox
    # copy cannot be read and `check_decisions.py` fails with exit 2.
    "apps/web/src/lib/home-cache.ts",
    "services/maintenance-worker/wrangler.toml",
    # Automatic deploy (2026-09-19): the rule reads the watcher and the
    # rollback path, and `tools/deploy.sh` is already listed above. Missing
    # here, `check_decisions.py` exits 2 instead of testing the rule.
    "tools/auto_deploy.sh",
    "tools/rollback.sh",
)


def _decisions_sandbox(extra_workflows: dict[str, str]) -> tuple[int, str]:
    """`check_decisions.py` on a copy of the files it reads, plus extra workflows.

    Writing a workflow into the real `.github/workflows` could overwrite a real
    one or be left behind if the run is killed; a copy cannot.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel in _DECISIONS_SANDBOX_FILES:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes((ROOT / rel).read_bytes())
        workflows = root / ".github/workflows"
        workflows.mkdir(parents=True)
        for path in (ROOT / ".github/workflows").glob("*.yml"):
            (workflows / path.name).write_bytes(path.read_bytes())
        for name, text in extra_workflows.items():
            (workflows / name).write_text(text, encoding="utf-8")
        return run([PY, str(root / "tools/check_decisions.py")])


def neg_decisions_trial_label_selftest_allowed() -> tuple[bool, str]:
    # Positive control: the exception must really let the trial self-test pass,
    # or the trial runner is pushed back onto the production label.
    code, out = _decisions_sandbox({"runner-selftest.yml": _TRIAL_WORKFLOW})
    if code != 0:
        return False, f"decisions/sinov label'i: self-test rad etildi (exit {code}) — {out[-160:]}"
    return True, "decisions/sinov label'i: runner-selftest.yml o'tdi (exit 0)"


def neg_decisions_trial_label_scoped() -> tuple[bool, str]:
    code, out = _decisions_sandbox({"ci-trial.yml": _TRIAL_WORKFLOW})
    if code != 1 or "CI testlari hosted" not in out:
        return False, f"decisions/sinov label'i boshqa workflow'da: exit {code} — {out[-160:]}"
    return True, "decisions/sinov label'i boshqa workflow'da: tutildi (exit 1)"


def _decisions_read_paths() -> set[str]:
    """The repo files `check_decisions.py` reads, parsed from its own source.

    Two shapes occur: a literal (`read("tools/deploy.sh")`) and a module
    constant (`read(LOCALE_PROVIDER)`), so both are resolved. Anything else —
    the helper's own `read(rel: str)`, a computed path — is skipped.
    """
    src = (ROOT / "tools/check_decisions.py").read_text(encoding="utf-8")
    consts = dict(re.findall(r'^([A-Z][A-Z0-9_]*) = "([^"]+)"', src, re.M))
    paths: set[str] = set()
    for arg in re.findall(r"\bread\(\s*([^)]+?)\s*\)", src):
        if arg.startswith('"') and arg.endswith('"'):
            paths.add(arg[1:-1])
        elif arg in consts:
            paths.add(consts[arg])
    return paths


def neg_decisions_sandbox_covers_reads() -> tuple[bool, str]:
    """The sandbox must stage every file `check_decisions.py` reads.

    The staged list is a hand-kept duplicate of the paths inside that script,
    so it drifts. Measured 2026-09-19: a new rule made the check read
    `LocaleProvider.tsx`; the sandbox did not copy it and two UNRELATED
    trial-label tests died in CI with exit 2 ("Qarorlarni o'qib bo'lmadi").
    Drift must fail locally and name the file, not wait for CI to notice.
    """
    paths = _decisions_read_paths()
    # A regex that stopped matching would make this test pass while measuring
    # nothing — the same "0/0 ✓" silent green that `main()` guards against.
    if len(paths) < 20:
        return False, f"decisions/sandbox: faqat {len(paths)} yo'l topildi — tahlil ishlamadi"
    staged = set(_DECISIONS_SANDBOX_FILES)
    # The sandbox copies the whole workflows directory with a glob, so
    # `ci.yml`/`deploy.yml` are staged even though no line names them. Read the
    # directory rather than assume it: that is what the sandbox itself does.
    staged |= {
        f".github/workflows/{p.name}" for p in (ROOT / ".github/workflows").glob("*.yml")
    }
    missing = sorted(paths - staged)
    if missing:
        return False, f"decisions/sandbox: nusxalanmagan fayl(lar) — {', '.join(missing)}"
    return True, f"decisions/sandbox: o'qilgan {len(paths)} fayl qamrab olingan"


# ── Mobile drawer: announced, focusable, escapable, non-scrolling (2026-09-18) ──
#
# One test per clause of `mobile_drawer_is_accessible`. Measured in a live
# browser before the fix: `aria-expanded` was `null` even while open, focus
# stayed on `body`, a real Escape left the panel open, and the page scrolled
# behind it. Each mutation below removes exactly one of those guarantees.


def neg_decisions_drawer_trigger_state_lost() -> tuple[bool, str]:
    return _decision_broken(
        "apps/web/src/layout/AppHeader.tsx",
        "aria-expanded={isMobileOpen}",
        "aria-expanded={undefined}",
        "mobil panel foydalanishga yaroqli",
    )


def neg_decisions_drawer_role_lost() -> tuple[bool, str]:
    return _decision_broken(
        "apps/web/src/layout/AppSidebar.tsx",
        'role={isMobileOpen ? "dialog" : undefined}',
        "role={undefined}",
        "mobil panel foydalanishga yaroqli",
    )


def neg_decisions_drawer_focus_not_moved() -> tuple[bool, str]:
    return _decision_broken(
        "apps/web/src/layout/AppSidebar.tsx",
        "closeButtonRef.current?.focus();",
        "void closeButtonRef;",
        "mobil panel foydalanishga yaroqli",
    )


def neg_decisions_drawer_focus_not_returned() -> tuple[bool, str]:
    return _decision_broken(
        "apps/web/src/layout/AppSidebar.tsx",
        "if (opener?.isConnected) opener.focus();",
        "void opener;",
        "mobil panel foydalanishga yaroqli",
    )


def neg_decisions_drawer_escape_lost() -> tuple[bool, str]:
    return _decision_broken(
        "apps/web/src/context/SidebarContext.tsx",
        'if (event.key === "Escape") setIsMobileOpen(false);',
        'if (event.key === "Esc") setIsMobileOpen(false);',
        "mobil panel foydalanishga yaroqli",
    )


def neg_decisions_drawer_scroll_lock_lost() -> tuple[bool, str]:
    return _decision_broken(
        "apps/web/src/layout/AppShell.tsx",
        'document.body.style.overflow = "hidden";',
        'document.body.style.overflow = "auto";',
        "mobil panel foydalanishga yaroqli",
    )


# ── KPI grid: 4-up from `lg`, value steps down (owner decision 2026-09-18) ──

_KPI_RULE = "KPI to'ri lg da 4 ustun"
_VALUE_STEP = 'valueClassName="lg:text-2xl xl:text-title-sm"'


def neg_decisions_kpi_grid_stuck_at_2up() -> tuple[bool, str]:
    # Back to `xl` only: the measured 38 px above the fold, four cards on two
    # rows across the whole 1024-1279 px laptop range.
    return _decision_broken(
        "apps/web/src/app/page.tsx",
        "sm:grid-cols-2 lg:grid-cols-4",
        "sm:grid-cols-2 xl:grid-cols-4",
        _KPI_RULE,
    )


def neg_decisions_kpi_grid_3up_creeps_back() -> tuple[bool, str]:
    # The measured-to-be-useless variant: four cards still take two rows, so
    # it buys 0 px of vertical space and orphans the fourth card.
    return _decision_broken(
        "apps/web/src/app/page.tsx",
        "sm:grid-cols-2 lg:grid-cols-4",
        "sm:grid-cols-2 lg:grid-cols-3",
        _KPI_RULE,
    )


def neg_decisions_kpi_card_value_step_lost() -> tuple[bool, str]:
    # One card keeps a 30 px value in a 121 px column: an 8-digit counter
    # overflows it. `replace(..., 1)` hits the first card only, leaving 3 of 4.
    return _decision_broken(
        "apps/web/src/app/page.tsx",
        _VALUE_STEP,
        "",
        _KPI_RULE,
    )


def neg_decisions_kpi_value_prop_ignored() -> tuple[bool, str]:
    # The prop is passed but never rendered — the kind of green that means
    # nothing. Keep the template literal so the anchor still matches.
    return _decision_broken(
        "apps/web/src/components/ui/Card.tsx",
        "`mt-1 text-title-sm font-bold rw-strong ${valueClassName}`",
        "`mt-1 text-title-sm font-bold rw-strong`",
        _KPI_RULE,
    )


# ── Profile KPI grid steps at `xl`, not `lg` (owner decision 2026-09-18) ──

_PROFILE_RULE = "profil paneli xl gacha stekda"
_PROFILE_GRID = "xl:grid-cols-[300px_minmax(0,1fr)]"
_PROFILE_STEP = 'valueClassName="lg:text-2xl 2xl:text-title-sm"'
_PROFILE_LAYOUT = "apps/web/src/app/users/[username]/layout.tsx"


def neg_decisions_profile_two_columns_at_lg() -> tuple[bool, str]:
    # The pre-decision state: the 300 px sidebar at `lg` leaves a 377 px
    # content column, where 4-up KPI cards clipped the values by 27 px —
    # that is exactly what decision 21 (2026-09-19) removed.
    return _decision_broken(
        _PROFILE_LAYOUT,
        "grid gap-6 " + _PROFILE_GRID,
        "grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]",
        _PROFILE_RULE,
    )


def neg_decisions_profile_kpi_stuck_at_2xl() -> tuple[bool, str]:
    # Without the `lg` step the KPI cards stretch full width until 1536 —
    # the sidebar no longer justifies a 2-up band at 1024–1279.
    return _decision_broken(
        _PROFILE_LAYOUT,
        "sm:grid-cols-2 lg:grid-cols-4",
        "sm:grid-cols-2 2xl:grid-cols-4",
        _PROFILE_RULE,
    )


def neg_decisions_profile_kpi_step_redundant() -> tuple[bool, str]:
    # A leftover `xl:grid-cols-4` next to `lg:grid-cols-4` is dead weight —
    # it means the old (sidebar-at-lg) step was not fully removed.
    return _decision_broken(
        _PROFILE_LAYOUT,
        "sm:grid-cols-2 lg:grid-cols-4",
        "sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4",
        _PROFILE_RULE,
    )


def neg_decisions_profile_kpi_value_step_lost() -> tuple[bool, str]:
    # One card keeps a 30 px value in a 104 px column, where a 6-digit counter
    # measures exactly 104 px. `replace(..., 1)` hits the first card only.
    return _decision_broken(
        _PROFILE_LAYOUT,
        _PROFILE_STEP,
        "",
        _PROFILE_RULE,
    )


# ── The difficulty range counts as ONE filter (owner decision 2026-09-18) ──

_DIFFICULTY_RULE = "diapazon bitta filtr"
_FILTERS = "apps/web/src/components/ProblemFilters.tsx"
_DIFFICULTY_DECL = (
    "const DIFFICULTY_KEYS: readonly string[] = [\n"
    '  "level",\n'
    '  "difficulty__gte",\n'
    '  "difficulty__lte",\n'
    "];"
)
_DIFFICULTY_COUNT = (
    "  const activeCount =\n"
    "    PANEL_KEYS.filter(\n"
    "      (key) => !DIFFICULTY_KEYS.includes(key) && params.get(key),\n"
    "    ).length + (DIFFICULTY_KEYS.some((key) => params.get(key)) ? 1 : 0);"
)
_NAIVE_COUNT = (
    "  const activeCount = PANEL_KEYS.filter((key) => params.get(key)).length;"
)


def neg_decisions_difficulty_keys_declaration_removed() -> tuple[bool, str]:
    # Without the constant there is nothing left to collapse the two range
    # params with, so the rule has to stop rather than pass by default.
    return _decision_broken(_FILTERS, _DIFFICULTY_DECL, "", _DIFFICULTY_RULE)


def neg_decisions_difficulty_keys_missing_level() -> tuple[bool, str]:
    # Drop the pre-#90 spelling: an old `?level=hard` link would narrow the
    # list while the badge claimed zero filters.
    return _decision_broken(
        _FILTERS,
        _DIFFICULTY_DECL,
        _DIFFICULTY_DECL.replace('  "level",\n', ""),
        _DIFFICULTY_RULE,
    )


def neg_decisions_difficulty_count_ignores_keys() -> tuple[bool, str]:
    # The regression that actually shipped: count `PANEL_KEYS` entries again,
    # so one "Qiyin" chip reads "Filtrlar2" and the E2E spec goes red.
    return _decision_broken(
        _FILTERS, _DIFFICULTY_COUNT, _NAIVE_COUNT, _DIFFICULTY_RULE
    )


def neg_decisions_difficulty_predicate_reverted() -> tuple[bool, str]:
    # The constant stays but the predicate stops using it — the range is
    # counted twice again while the rule's first two clauses still pass.
    return _decision_broken(
        _FILTERS,
        "      (key) => !DIFFICULTY_KEYS.includes(key) && params.get(key),\n",
        "      (key) => params.get(key),\n",
        _DIFFICULTY_RULE,
    )


# ── Brand in the header, 3-column footer (owner decision 2026-09-19) ──

_BRAND_RULE = "brend headerda, footer uch ustun"
_HEADER = "apps/web/src/layout/AppHeader.tsx"
_SIDEBAR = "apps/web/src/layout/AppSidebar.tsx"
_FOOTER = "apps/web/src/layout/AppFooter.tsx"


def neg_decisions_header_brand_removed() -> tuple[bool, str]:
    # The regression the decision fixes: no brand in the header, so on a
    # phone the logo is only visible after opening the drawer.
    return _decision_broken(_HEADER, "<BrandMark", "<div", _BRAND_RULE)


def neg_decisions_sidebar_brand_back() -> tuple[bool, str]:
    # Re-duplicating the wordmark in the sidebar breaks the single-source
    # rule: three places would render the brand again.
    return _decision_broken(
        _SIDEBAR,
        '<div className="flex h-16 items-center justify-end gap-1">',
        '<div className="flex h-16 items-center justify-end gap-1">'
        '<IntentLink href="/" className="text-lg font-bold">'
        'Rank<span className="rw-accent-ink">Want</span></IntentLink>',
        _BRAND_RULE,
    )


def neg_decisions_footer_single_column() -> tuple[bool, str]:
    # Collapsing the footer to one column merges the contacts into the
    # brand block — the 3-column structure the owner chose is gone.
    return _decision_broken(
        _FOOTER,
        "lg:grid-cols-[1fr_auto_auto]",
        "lg:grid-cols-1",
        _BRAND_RULE,
    )


def neg_decisions_footer_privacy_link_lost() -> tuple[bool, str]:
    # Privacy must be on EVERY page — Google OAuth verification expects it
    # reachable from the footer (ADR-0016), so the legal row is load-bearing.
    return _decision_broken(
        _FOOTER,
        '        <IntentLink href="/privacy" className="rw-focus-ring hover:underline">\n'
        "          {t(locale, \"footer.privacy\")}\n"
        "        </IntentLink>\n",
        "",
        _BRAND_RULE,
    )


# ── Deploy gate: agents deploy only a green `main` (owner decision 2026-09-17) ──

_GATE_SHA = "a" * 40
_GATE_GREEN = [
    {
        "workflowName": "CI",
        "status": "completed",
        "conclusion": "success",
        "createdAt": "2026-09-17T00:00:00Z",
    },
    {
        "workflowName": "Security",
        "status": "completed",
        "conclusion": "success",
        "createdAt": "2026-09-17T00:00:00Z",
    },
]


def _gate_expect(
    label: str, main: str, runs: object, code: int, needle: str, dirty: object = None
) -> tuple[bool, str]:
    """Run the gate on fixtures (no git, no GitHub) and require exit `code`.

    The compose fixture is always passed: without it the gate would read this
    working tree, where the negative suite's own mutations come and go.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "runs.json"
        text = runs if isinstance(runs, str) else json.dumps(runs)
        path.write_text(text, encoding="utf-8")
        compose = Path(tmp) / "compose.json"
        compose.write_text(
            dirty if isinstance(dirty, str) else json.dumps(dirty or []), encoding="utf-8"
        )
        got, out = run_check(
            "deploy_gate", "--head", _GATE_SHA, "--main", main, "--runs", str(path),
            "--compose-status", str(compose),
        )
    if got != code:
        return False, f"deploy_gate/{label}: exit {got} ({code} kerak) — {out.strip()[-160:]}"
    if needle not in out:
        return False, f"deploy_gate/{label}: sabab ko'rinmadi ({needle!r}) — {out.strip()[-160:]}"
    return True, f"deploy_gate/{label}: exit {code}"


def neg_deploy_gate_green_passes() -> tuple[bool, str]:
    # Positive control: a gate that is always shut would pass every case below.
    return _gate_expect("yashil main o'tadi", _GATE_SHA, _GATE_GREEN, 0, "yashil")


def _gate_scan(label: str, layout: str, code: int, needle: str) -> tuple[bool, str]:
    """Run the gate with a real compose scan over temporary checkouts.

    `layout` picks the checkouts: `vanished` lists a clean repository and a
    path that no longer exists, `broken` lists a directory that is not a
    repository. CI runs still come from the green fixture.
    """
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # ⚠️ No inherited `GIT_*`, and a ceiling at the sandbox: under the
        # pre-push hook `GIT_DIR` points at the real repository, and a plain
        # `git init` here re-initialised it as bare (measured 2026-09-18;
        # the suite's fingerprint caught it). Same trap as 2026-09-16.
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env["GIT_CEILING_DIRECTORIES"] = str(root)
        if layout == "vanished":
            subprocess.run(["git", "init", "-q", str(root / "repo")], check=True, env=env)
            paths = [root / "repo", root / "removed-worktree"]
        else:
            (root / "not-a-repo").mkdir()
            paths = [root / "not-a-repo"]
        runs = root / "runs.json"
        runs.write_text(json.dumps(_GATE_GREEN), encoding="utf-8")
        listed = root / "checkouts.json"
        listed.write_text(json.dumps([str(p) for p in paths]), encoding="utf-8")
        proc = subprocess.run(
            [PY, "tools/check_deploy_gate.py", "--head", _GATE_SHA, "--main", _GATE_SHA,
             "--runs", str(runs), "--checkouts", str(listed)],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
        )
        got, out = proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    if got != code:
        return False, f"deploy_gate/{label}: exit {got} ({code} kerak) — {out.strip()[-160:]}"
    if needle not in out:
        return False, f"deploy_gate/{label}: sabab ko'rinmadi ({needle!r}) — {out.strip()[-160:]}"
    return True, f"deploy_gate/{label}: exit {code}"


def neg_deploy_gate_vanished_checkout() -> tuple[bool, str]:
    # 2026-09-18: a worktree removed mid-run stopped a deploy with exit 2.
    return _gate_scan("o'chirilgan worktree o'tkaziladi", "vanished", 0, "yashil")


def neg_deploy_gate_broken_checkout() -> tuple[bool, str]:
    # The skip must stay narrow: a checkout git cannot read still stops the deploy.
    return _gate_scan("o'qib bo'lmaydigan checkout to'xtatadi", "broken", 2, "o'lchab bo'lmadi")


def neg_deploy_gate_not_main() -> tuple[bool, str]:
    return _gate_expect("main emas", "b" * 40, _GATE_GREEN, 1, "`main` emas")


def neg_deploy_gate_dirty_compose_blocks() -> tuple[bool, str]:
    # 2026-09-17: the live stack was recreated from an uncommitted compose that carried
    # the Turnstile keys; a deploy from a worktree would have dropped them silently.
    dirty = ["C:/Users/nsn/project/cp/rankwant:  M docker-compose.public.yml"]
    return _gate_expect(
        "commit qilinmagan compose", _GATE_SHA, _GATE_GREEN, 1, "commit qilinmagan compose", dirty
    )


def neg_deploy_gate_unreadable_compose_status() -> tuple[bool, str]:
    return _gate_expect(
        "compose holati o'qilmadi", _GATE_SHA, _GATE_GREEN, 2, "o'lchab bo'lmadi", "{not json"
    )


def neg_deploy_gate_ci_failed() -> tuple[bool, str]:
    runs = [dict(_GATE_GREEN[0], conclusion="failure"), _GATE_GREEN[1]]
    return _gate_expect("CI qizil", _GATE_SHA, runs, 1, "`CI` natijasi `failure`")


def neg_deploy_gate_ci_running() -> tuple[bool, str]:
    runs = [dict(_GATE_GREEN[0], status="in_progress", conclusion=""), _GATE_GREEN[1]]
    return _gate_expect("CI tugamagan", _GATE_SHA, runs, 1, "hali tugamagan")


def neg_deploy_gate_security_missing() -> tuple[bool, str]:
    return _gate_expect("Security yo'q", _GATE_SHA, [_GATE_GREEN[0]], 1, "`Security` run'i")


def neg_deploy_gate_latest_run_wins() -> tuple[bool, str]:
    # A later failed rerun must not hide behind an earlier success.
    runs = [
        _GATE_GREEN[0],
        dict(_GATE_GREEN[0], conclusion="failure", createdAt="2026-09-17T01:00:00Z"),
        _GATE_GREEN[1],
    ]
    return _gate_expect("oxirgi run hal qiladi", _GATE_SHA, runs, 1, "`CI` natijasi `failure`")


def neg_deploy_gate_unreadable() -> tuple[bool, str]:
    return _gate_expect("o'lchanmadi", _GATE_SHA, "not json", 2, "o'lchab bo'lmadi")


def _run_deploy(lock: Path, *args: str) -> tuple[int, str]:
    """`tools/deploy.sh` with a private lock and a `docker` that always fails.

    It must never deploy, even if the code under test is broken: no `--yes` and
    a closed stdin stop it at the confirmation prompt, and the stub makes every
    Docker step fail before that.
    """
    with tempfile.TemporaryDirectory() as tmp:
        stub = Path(tmp) / "docker"
        stub.write_text("#!/bin/sh\necho 'stub docker (negative test)' >&2\nexit 99\n")
        stub.chmod(0o755)
        env = dict(os.environ, RANKWANT_DEPLOY_LOCK=str(lock))
        env["PATH"] = tmp + os.pathsep + env.get("PATH", "")
        proc = subprocess.run(
            [_bash(), "tools/deploy.sh", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            stdin=subprocess.DEVNULL,
        )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def neg_deploy_lock_held() -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as tmp:
        lock = Path(tmp) / "lock"
        lock.mkdir()
        (lock / "owner").write_text("pid 1, probe, commit x\n", encoding="utf-8")
        code, out = _run_deploy(lock)
        if code != 1 or "boshqa deploy ishlayapti" not in out:
            return False, f"deploy_lock/band: exit {code}, sabab ko'rinmadi — {out.strip()[-160:]}"
        if "Deploy darvozasi" in out or "Old shartlar" in out:
            return False, "deploy_lock/band: qulf band bo'lsa ham skript davom etdi"
        if not (lock / "owner").exists():
            return False, "deploy_lock/band: boshqa deploy'ning qulfi o'chirib yuborildi"
    return True, "deploy_lock/band: ikkinchi deploy to'xtadi, begona qulfga tegilmadi (exit 1)"


def neg_deploy_lock_released() -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as tmp:
        lock = Path(tmp) / "lock"
        code, out = _run_deploy(lock, "--skip-ci-gate")
        if code == 0:
            return False, f"deploy_lock/bo'shatish: stub docker bilan exit 0 — {out.strip()[-160:]}"
        if "--skip-ci-gate" not in out:
            return False, f"deploy_lock/bo'shatish: qulf bosqichidan o'tmadi — {out.strip()[-160:]}"
        if lock.exists():
            return False, "deploy_lock/bo'shatish: yiqilgan deploy qulfni qoldirdi"
    return True, "deploy_lock/bo'shatish: yiqilgan deploy qulfni bo'shatdi"


def _label_states() -> dict[str, str]:
    """`check_deploy.sh --label-state` in a sandbox: A (web), B (web change), C (docs).

    CI checks out one commit only, so the real history cannot be used here.
    """
    states: dict[str, str] = {}
    with _push_sandbox() as (repo, env):
        (repo / "tools").mkdir()
        (repo / "tools/check_deploy.sh").write_bytes((ROOT / "tools/check_deploy.sh").read_bytes())
        (repo / "apps/web").mkdir(parents=True)

        def commit(message: str) -> str:
            _sandbox_run(repo, env, "git", "add", "-A")
            _sandbox_run(repo, env, *_REAL_IDENTITY, "commit", "-q", "-m", message)
            return _sandbox_run(repo, env, "git", "rev-parse", "HEAD")

        (repo / "apps/web/page.tsx").write_text("v1\n", encoding="utf-8")
        (repo / "README.md").write_text("a\n", encoding="utf-8")
        shas = {"A": commit("web v1")}
        (repo / "apps/web/page.tsx").write_text("v2\n", encoding="utf-8")
        shas["B"] = commit("web v2")
        (repo / "README.md").write_text("b\n", encoding="utf-8")
        shas["C"] = commit("docs only")
        shas["missing"] = "0" * 40
        for name, sha in shas.items():
            proc = subprocess.run(
                [_bash(), "tools/check_deploy.sh", "--label-state", sha, "apps/web"],
                cwd=repo,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
            failed = f"(exit {proc.returncode}) {proc.stderr.strip()[-80:]}"
            states[name] = proc.stdout.strip() or failed
    return states


def neg_deploy_label_web_change_is_stale() -> tuple[bool, str]:
    states = _label_states()
    if states["A"] != "stale":
        return False, f"deploy_check/web o'zgardi: `{states['A']}` — stale kerak"
    if states["missing"] != "unknown":
        return False, f"deploy_check/yo'q commit: `{states['missing']}` — unknown kerak"
    return True, "deploy_check/web o'zgardi: eski yorliq stale, yo'q commit unknown"


def neg_deploy_label_docs_commit_not_stale() -> tuple[bool, str]:
    # The false red this fixes: after #39 (no web file) check_deploy.sh called
    # the web image stale because its label was not HEAD.
    states = _label_states()
    if states["B"] != "current" or states["C"] != "same":
        got = f"B=`{states['B']}` C=`{states['C']}`"
        return False, f"deploy_check/docs commit: {got} — current/same kerak"
    return True, "deploy_check/docs commit: web yorlig'i eskirgan deb ko'rsatilmadi"


def _build_label_states() -> dict[str, str]:
    """`--build-label-state` natijalari — docker'siz, faqat qaror."""
    values = {
        "missing": "",
        "unknown": "unknown",
        "novalue": "<no value>",
        "set": "2026-09-18T08:52:06Z",
    }
    env = {**os.environ, "MSYS_NO_PATHCONV": "1"}
    out: dict[str, str] = {}
    for name, value in values.items():
        proc = subprocess.run(
            [_bash(), "tools/check_deploy.sh", "--build-label-state", value],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        out[name] = proc.stdout.strip() or f"(exit {proc.returncode})"
    return out


def neg_deploy_build_label_absent_is_flagged() -> tuple[bool, str]:
    """`built-at` yo'q bo'lsa — uch xil ko'rinishda ham `unlabeled`.

    Nega kerak: yorliqning yagona ma'nosi shu. `img_time` vaqtni Docker
    metadatasidan (`.Created`) oladi, ya'ni yorliq yo'qligi HECH QANDAY
    farq qilmasdi — 2026-09-18 gacha u faqat yozilardi. Bu tekshiruv
    o'sha bo'shliqni yopadi va build argumentlari uzilganini ko'rsatadi
    (aynan shu holat `api` oilasida `git-sha` ni ham `unknown` qilgan edi).
    """
    states = _build_label_states()
    for name in ("missing", "unknown", "novalue"):
        if states[name] != "unlabeled":
            return False, f"deploy_check/built-at {name}: `{states[name]}` — unlabeled kerak"
    return True, "deploy_check/built-at yo'q/unknown/<no value>: uchtasi ham unlabeled"


def neg_deploy_build_label_set_is_ok() -> tuple[bool, str]:
    """Yorliq o'rnatilgan bo'lsa — `ok`, ya'ni yolg'on ogohlantirish YO'Q.

    Salbiy juftlik: yuqoridagi test «har doim unlabeled» qaytaradigan
    soxta tekshiruvni ham o'tkazib yuborardi. Bu test uni ushlaydi.
    """
    states = _build_label_states()
    if states["set"] != "ok":
        return False, f"deploy_check/built-at o'rnatilgan: `{states['set']}` — ok kerak"
    return True, "deploy_check/built-at o'rnatilgan: ok (yolg'on ogohlantirish yo'q)"


def _env_example_broken(rel: str, old: str, new: str, name: str) -> tuple[bool, str]:
    """Break `.env.example` or a source it mirrors; the checker must name `name`."""
    path = ROOT / rel
    text = path.read_bytes().decode("utf-8")
    if old not in text:
        return False, f"env_example/{name}: langar topilmadi ({rel})"
    with Mutation(path, old, new):
        code, out = run_check("env_example")
    if code != 1:
        return False, f"env_example/{name}: buzuq holat exit {code} berdi (1 kerak)"
    if name not in out:
        return False, f"env_example/{name}: yiqildi, lekin boshqa sabab — {out.strip()[-160:]}"
    return True, f"env_example/{name}: tutildi (exit 1)"


def neg_env_example_required_missing() -> tuple[bool, str]:
    return _env_example_broken(".env.example", "\nDJANGO_SECRET_KEY=\n", "\n", "DJANGO_SECRET_KEY")


def neg_env_example_required_commented() -> tuple[bool, str]:
    return _env_example_broken(
        ".env.example",
        "\nPUBLIC_ORIGIN=https://rankwant.uz\n",
        "\n# PUBLIC_ORIGIN=https://rankwant.uz\n",
        "PUBLIC_ORIGIN",
    )


def neg_env_example_new_compose_var() -> tuple[bool, str]:
    return _env_example_broken(
        "docker-compose.public.yml",
        '      DJANGO_DEBUG: "0"\n',
        '      DJANGO_DEBUG: "0"\n      NEW_PROBE_VAR: ${NEW_PROBE_VAR}\n',
        "NEW_PROBE_VAR",
    )


def neg_env_example_new_setting() -> tuple[bool, str]:
    return _env_example_broken(
        "apps/api/config/settings.py",
        'SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-only-not-for-production")\n',
        'SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-only-not-for-production")\n'
        'PROBE_SETTING = env("NEW_PROBE_SETTING")\n',
        "NEW_PROBE_SETTING",
    )


def neg_env_example_secret_value() -> tuple[bool, str]:
    return _env_example_broken(
        ".env.example",
        "\nTELEGRAM_BOT_TOKEN=\n",
        "\nTELEGRAM_BOT_TOKEN=123456:probe-not-a-real-token\n",
        "TELEGRAM_BOT_TOKEN",
    )


def neg_icons_pack_missing_key() -> tuple[bool, str]:
    """Bitta to'plamdan bitta kalit olib tashlansa — tutilsinmi?

    D12 shuni talab qiladi: yetishmagan ikonka asosiy to'plamdan
    OLINMAYDI, ya'ni jimgina zaxira yo'q. Bittasi yetishmasa,
    foydalanuvchi tanlagan to'plamda ikonka umuman chizilmay qolardi.
    """
    path = ROOT / "apps/web/src/icons/packs/bootstrap.tsx"
    src = path.read_bytes().decode("utf-8")
    old = '  "nav.quiz": BiQuestionCircle,'
    if old not in src:
        # Fall back to whatever the pack resolved `nav.quiz` to.
        import re

        m = re.search(r'^\s*"nav\.quiz": (\w+),', src, re.M)
        if not m:
            return False, "ikonka/kalit yetishmaydi: langar topilmadi"
        old = m.group(0)
    with Mutation(path, old, ""):
        return expect_fail("icons", "ikonka/to'plamda kalit yetishmaydi")


def neg_ci_disk_cleanup_removed() -> tuple[bool, str]:
    """CI tozalash qadami olib tashlansa — tutilsinmi?

    ⚠️ Bu 2026-09-16 dagi 58 GB muammoning o'zi: `docker compose down -v`
    konteynerni olib tashlaydi, lekin qurilgan obrazlarni QOLDIRADI. Natija
    420 ta `rw-smoke-*` yig'ilib, C: da 9.59 GB qolgandi. Tozalash qadami
    olib tashlansa, birorta test qizil bo'lmaydi — muammo haftalar ichida
    asta qaytadi. Faqat shu tekshiruv uni darhol ushlaydi.
    """
    path = ROOT / ".github/workflows/ci.yml"
    src = path.read_bytes().decode("utf-8")
    # Butun qadamni olib tashlash kerak, faqat sarlavhani emas: `run:`
    # qismi qolsa `docker rmi` matni ham qoladi va tekshiruv uni hali ham
    # «bor» deb o'qiydi. Birinchi urinish aynan shunday yolg'on yashil
    # bergan edi.
    start = src.index("      - name: Clean images")
    end = src.index("      - name:", start + 10) if "      - name:" in src[start + 10 :] else len(src)
    old = src[start:end]
    if not old.strip():
        return False, "ci_disk/tozalash: langar topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("ci_disk", "CI obrazlarni tozalamaydi")


def neg_ci_disk_nightly_cleanup_removed() -> tuple[bool, str]:
    """Nightly E2E job without its image cleanup must be caught.

    2026-09-17: one nightly run left 18 images on the shared engine, because
    its jobs only ran `down -v`. Only the second of the three cleanup steps is
    removed, so the check has to look at each job, not at the file as a whole.
    """
    path = ROOT / ".github/workflows/nightly.yml"
    src = path.read_bytes().decode("utf-8")
    marker = "      - name: Clean images"
    first = src.index(marker)
    start = src.index(marker, first + len(marker))
    end = src.index("|| true\n", start) + len("|| true\n")  # end of that step's run block
    old = src[start:end]
    if "docker rmi" not in old:
        return False, "ci_disk/nightly: langar topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("ci_disk", "nightly e2e obrazlarni tozalamaydi")


def neg_ci_disk_deploy_cleanup_removed() -> tuple[bool, str]:
    """Deploy tozalash qadami olib tashlansa — tutilsinmi?

    `deploy.yml` 122 ta `rankwant-build-*` obrazining manbai: har yurish
    yangi obraz quradi, eskisini hech kim o'chirmas edi.
    """
    path = ROOT / ".github/workflows/deploy.yml"
    src = path.read_bytes().decode("utf-8")
    start = src.index("      - name: Clean old images")
    end = src.index("      - name:", start + 10) if "      - name:" in src[start + 10 :] else len(src)
    old = src[start:end]
    if not old.strip():
        return False, "ci_disk/deploy: langar topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("ci_disk", "deploy obrazlarni tozalamaydi")


def neg_icons_camelcase_key_missing() -> tuple[bool, str]:
    """camelCase kalit bitta to'plamdan olib tashlansa — tutilsinmi?

    ⚠️ Bu teshik edi. Tekshiruvchining kalit naqshi `[a-z0-9.]` edi, ya'ni
    **faqat kichik harf**. `nav.expandDown`, `ranking.medalGold`,
    `action.sortAsc` kabi 35 kalit ko'rinmasdi.

    Nega bu jimgina o'tib ketardi: naqsh HAMMA to'plamda bir xil
    xato qiladi, ya'ni to'plamlar o'zaro baribir mos ko'rinadi. Faqat
    bittasidan kalit yo'qolsa — va u camelCase bo'lsa — xato sezilmaydi.
    Kalitlar soni ham 226 o'rniga 191 chiqardi, lekin bu «yashil» natija
    berardi.
    """
    path = ROOT / "apps/web/src/icons/packs/lucide.tsx"
    src = path.read_bytes().decode("utf-8")
    old = '  "ranking.medalGold": '
    i = src.find(old)
    if i < 0:
        return False, "ikonka/camelCase: langar topilmadi"
    end = src.find("\n", i)
    with Mutation(path, src[i : end + 1], ""):
        return expect_fail("icons", "ikonka/camelCase kalit yetishmaydi")


def neg_icons_fixed_zone_leaks() -> tuple[bool, str]:
    """Qat'iy zona registrga tushsa — tutilsinmi?

    D20 ①: verdikt va brend almashmasligi kerak. Ular registrga tushsa,
    kimdir ularni `Icon` orqali chizayotgan bo'ladi va qo'llanma tayanadigan
    belgi foydalanuvchiga qarab o'zgarib ketadi.
    """
    path = ROOT / "apps/web/src/icons/packs/lucide.tsx"
    src = path.read_bytes().decode("utf-8")
    old = '  "nav.problems": LuBookOpen,'
    if old not in src:
        return False, "ikonka/qat'iy zona: langar topilmadi"
    new = '  "nav.problems": LuBookOpen,\n  "verdict.accepted": LuCircleCheck,'
    with Mutation(path, old, new):
        return expect_fail("icons", "ikonka/qat'iy zona registrda")


def neg_markup_cookie_boot_missing() -> tuple[bool, str]:
    """Markup sozlamasi boot skriptdan olib tashlansa — tutilsinmi?

    ⚠️ Bu xato sinfi ikki marta urgan (2026-09-15, verdict va loading).
    Sozlama `MarkupPrefs` da bor, `parseMarkupCookie` da bor, lekin boot
    skriptda yo'q bo'lsa: klient bir xil markup chizadi, server boshqasini
    kutadi → **hidratsiya xatosi**. `tsc` ham, eslint ham jim o'tadi.
    """
    path = ROOT / "apps/web/src/app/layout.tsx"
    src = path.read_bytes().decode("utf-8")
    old = 'if(IP.indexOf(a.iconPack)>0)m.push("p="+a.iconPack);'
    if old not in src:
        return False, "markup/boot: langar topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("markup_cookie", "markup/boot skriptda sozlama yo'q")


def neg_markup_cookie_parse_missing() -> tuple[bool, str]:
    """Cookie o'qishdan sozlama olib tashlansa — tutilsinmi?

    Server cookie'dan o'qimasa, u standart qiymatni chizadi — ya'ni
    foydalanuvchi tanlovi birinchi yuklanishda ko'rinmaydi va keyin
    «sakraydi». Bu ham hidratsiya sinfidagi xato.
    """
    path = ROOT / "apps/web/src/lib/prefs.ts"
    src = path.read_bytes().decode("utf-8")
    old = 'else if (k === "p") out.iconPack = v as MarkupPrefs["iconPack"];'
    if old not in src:
        return False, "markup/parse: langar topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("markup_cookie", "markup/parse da sozlama yo'q")


def neg_verdict_code_missing() -> tuple[bool, str]:
    """Web'dan bitta verdikt kodi olib tashlansa — tutilsinmi?

    Bu AYnan ilgari bo'lgan holat: API'da 23 kod, web'da 10 ta, ya'ni
    14 tasi «Navbatda» bo'lib ko'ringan. `tsc` ham, eslint ham jim
    o'tgan — kalit oddiy `string`.
    """
    path = ROOT / "apps/web/src/lib/theme/verdict.ts"
    old = '  | "WRONG_TEST"\n'
    if old not in path.read_bytes().decode("utf-8"):
        return False, "verdikt/kod yetishmaydi: langar topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("verdict_codes", "verdikt/kod web'da yetishmaydi")


def neg_verdict_label_missing() -> tuple[bool, str]:
    """Bitta tildan verdikt yorlig'i olib tashlansa — tutilsinmi?

    Yorliqsiz kod foydalanuvchiga xom kalit bo'lib ko'rinardi.
    """
    path = ROOT / "apps/web/src/i18n/locales/uz.ts"
    old = '  "verdict.SKIPPED": "Hisobga olinmadi",\n'
    if old not in path.read_bytes().decode("utf-8"):
        return False, "verdikt/yorliq yetishmaydi: langar topilmadi"
    with Mutation(path, old, ""):
        return expect_fail("verdict_codes", "verdikt/yorliq bir tilda yetishmaydi")


# ── Deploy oynasi (10-operations, qoida №1) ──────────────────────────
#
# Qoida «live contest paytida deploy YO'Q» — ilgari u faqat odamning
# yodida edi. Endi `tools/check_deploy_window.py` uni bajariladigan
# qiladi, `tools/deploy.sh` esa shunga tayanadi. Bu yerda savol:
# **darvoza haqiqatan to'xtatadimi**, yoki faqat «yashil» ko'rinadimi?


class _StubApi(http.server.BaseHTTPRequestHandler):
    """`is_running` bayrog'ini boshqaradigan eng kichik API nusxasi."""

    live = False

    def do_GET(self) -> None:  # noqa: N802 — http.server shartnomasi
        body = json.dumps(
            {
                "results": [
                    {
                        "slug": "stub-cup",
                        "title": "Stub kubogi",
                        "is_running": _StubApi.live,
                        "end_at": "2026-09-16T20:00:00Z",
                    }
                ]
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        """Jurnal kerak emas — u hisobotni iflos qiladi."""


@contextlib.contextmanager
def stub_api(live: bool):
    """Vaqtinchalik API: `RANKWANT_API_BASE` shu manzilga qaratiladi."""
    _StubApi.live = live
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _StubApi)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/api/v1"
    finally:
        server.shutdown()
        server.server_close()


def run_deploy_window(base: str) -> tuple[int, str]:
    env = dict(os.environ, RANKWANT_API_BASE=base)
    proc = subprocess.run(
        [PY, "tools/check_deploy_window.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def neg_deploy_window_live_contest() -> tuple[bool, str]:
    """Faol contest bo'lsa darvoza TO'XTAYDI va sababini aytadimi?

    Uch holat ketma-ket o'lchanadi va uchtasi ham shart:
      1) bo'sh oyna (stub) → 0 — aks holda «exit != 0» yolg'on yashil
         bo'lardi: skript shunchaki ishga tushmay qolgan bo'lishi mumkin;
      2) API javob bermasa → 2 — «0 ta» deb o'qilmasligi kerak;
      3) faol contest → 1 va matnda «qoida №1» bo'lishi shart.
    """
    with stub_api(live=False) as base:
        code, out = run_deploy_window(base)
    if code != 0:
        return False, f"oyna bo'sh bo'lsa exit 0 bo'lishi kerak, kelgan {code}: {out.strip()[:200]}"

    # Yopiq port: hech kim tinglamaydi.
    code, _ = run_deploy_window("http://127.0.0.1:1/api/v1")
    if code != 2:
        return False, f"API javob bermasa exit 2 bo'lishi kerak, kelgan {code}"

    with stub_api(live=True) as base:
        code, out = run_deploy_window(base)
    if code == 0:
        return False, "faol contest bo'lsa darvoza O'TKAZDI (exit 0) — u o'lik"
    if "qoida №1" not in out:
        return False, f"to'xtadi, lekin sabab ko'rinmaydi: {out.strip()[:200]}"
    return True, "faol contest'da to'xtadi, sabab ko'rsatildi (exit 1)"


# ── Runner watchdog: idle runner + waiting jobs = restart (actions/runner#4444) ──

_WD_RUNNER = "nsn-pc-rankwant-container"
_WD_NOW = "2026-09-17T13:38:00Z"
_WD_SUSPECT = {_WD_RUNNER: {"suspect_since": "2026-09-17T13:36:00+00:00"}}


def _wd_runner(busy: bool = False) -> dict:
    labels = ("self-hosted", "Linux", "X64", "rankwant")
    return {
        "name": _WD_RUNNER,
        "status": "online",
        "busy": busy,
        "labels": [{"name": label} for label in labels],
    }


def _wd_job(
    created_at: str = "2026-09-17T13:31:03Z", labels: tuple[str, ...] = ("self-hosted", "rankwant")
) -> dict:
    return {
        "name": "API — lint, types, tests",
        "status": "queued",
        "labels": list(labels),
        "created_at": created_at,
    }


def _watchdog(runners: list[dict], jobs: list[dict], state: dict | None) -> tuple[int, str, dict]:
    """`runner_watchdog.py --dry-run` on fixtures: exit code, output and the saved state."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "runners.json").write_text(json.dumps(runners), encoding="utf-8")
        (root / "jobs.json").write_text(json.dumps(jobs), encoding="utf-8")
        state_path = root / "state.json"
        if state is not None:
            state_path.write_text(json.dumps(state), encoding="utf-8")
        code, out = run(
            [
                PY,
                "tools/runner_watchdog.py",
                "--dry-run",
                "--runners",
                str(root / "runners.json"),
                "--jobs",
                str(root / "jobs.json"),
                "--state",
                str(state_path),
                "--now",
                _WD_NOW,
            ]
        )
        saved = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    return code, out, saved


def neg_watchdog_restarts_confirmed_stall() -> tuple[bool, str]:
    # Positive control: without it every "left alone" case passes on a dead watchdog.
    code, out, _ = _watchdog([_wd_runner()], [_wd_job()], _WD_SUSPECT)
    if code != 0 or "restart qilinardi" not in out:
        return False, f"watchdog/tasdiqlangan tiqilish: restart yo'q (exit {code}) — {out.strip()[-160:]}"
    return True, "watchdog/tasdiqlangan tiqilish: restart qilinardi"


def neg_watchdog_first_sighting_waits() -> tuple[bool, str]:
    # Between two jobs a healthy runner is idle for seconds with a long-queued
    # job. One check must only record the suspicion.
    code, out, saved = _watchdog([_wd_runner()], [_wd_job()], None)
    if "restart qilinardi" in out:
        return False, "watchdog/birinchi ko'rish: bitta tekshiruvdayoq restart qilindi"
    if code != 0 or "suspect_since" not in saved.get(_WD_RUNNER, {}):
        return False, f"watchdog/birinchi ko'rish: shubha yozilmadi (exit {code}) — {out.strip()[-160:]}"
    return True, "watchdog/birinchi ko'rish: faqat shubha yozildi"


def neg_watchdog_busy_runner_left_alone() -> tuple[bool, str]:
    code, out, saved = _watchdog([_wd_runner(busy=True)], [_wd_job()], _WD_SUSPECT)
    if code != 0 or "restart" in out or saved.get(_WD_RUNNER):
        return False, f"watchdog/band runner: tegildi (exit {code}) — {out.strip()[-160:]} {saved}"
    return True, "watchdog/band runner: tegilmadi, shubha tozalandi"


def neg_watchdog_fresh_job_left_alone() -> tuple[bool, str]:
    job = _wd_job(created_at="2026-09-17T13:37:00Z")
    code, out, _ = _watchdog([_wd_runner()], [job], _WD_SUSPECT)
    if code != 0 or "restart" in out:
        return False, f"watchdog/yangi job: 60 s navbat tiqilish deb o'qildi (exit {code}) — {out.strip()[-160:]}"
    return True, "watchdog/yangi job: 60 s navbat tiqilish deb o'qilmadi"


def neg_watchdog_foreign_labels_left_alone() -> tuple[bool, str]:
    job = _wd_job(labels=("self-hosted", "rankwant-container"))
    code, out, _ = _watchdog([_wd_runner()], [job], _WD_SUSPECT)
    if code != 0 or "restart" in out:
        return False, f"watchdog/boshqa label: olmaydigan job uchun restart (exit {code}) — {out.strip()[-160:]}"
    return True, "watchdog/boshqa label: bu runner olmaydigan job'ga tegilmadi"


def neg_watchdog_cooldown_holds() -> tuple[bool, str]:
    state = {
        _WD_RUNNER: {
            "suspect_since": "2026-09-17T13:36:00+00:00",
            "restarted_at": "2026-09-17T13:33:00+00:00",
        }
    }
    code, out, _ = _watchdog([_wd_runner()], [_wd_job()], state)
    if code != 0 or "restart qilinardi" in out:
        return False, f"watchdog/tanaffus: 5 daqiqada ikkinchi restart (exit {code}) — {out.strip()[-160:]}"
    return True, "watchdog/tanaffus: 10 daqiqa ichida qayta restart qilinmadi"


def neg_watchdog_second_runner_restarts() -> tuple[bool, str]:
    name = "nsn-pc-rankwant-container-2"
    runner = {
        "name": name,
        "status": "online",
        "busy": False,
        "labels": [{"name": label} for label in ("self-hosted", "Linux", "X64", "rankwant")],
    }
    state = {name: {"suspect_since": "2026-09-17T13:36:00+00:00"}}
    code, out, _ = _watchdog([runner], [_wd_job()], state)
    if "restart qilinardi" not in out or "restart buyrug'i yo'q" in out:
        return False, f"watchdog/ikkinchi runner: restart yo'q (exit {code}) — {out.strip()[-160:]}"
    return True, "watchdog/ikkinchi runner: restart qilinardi"


def neg_watchdog_unreadable_time() -> tuple[bool, str]:
    code, out, _ = _watchdog([_wd_runner()], [_wd_job(created_at="kecha")], _WD_SUSPECT)
    if code != 2:
        return False, f"watchdog/o'qilmagan vaqt: exit {code} (2 kerak) — {out.strip()[-160:]}"
    return True, "watchdog/o'qilmagan vaqt: exit 2, sog' deb o'qilmadi"


# ── After a reboot: every link that must come back on its own is measured ──

_AR_BOOT = "2026-09-18T05:00:00.0000000Z"


def _ar_facts(**overrides: object) -> dict:
    facts: dict = {
        "docker_engine": True,
        "containers": {
            "rankwant-api-1": "Up 3 minutes (healthy)",
            "rankwant-worker-1": "Up 3 minutes",
            "rankwant-beat-1": "Up 3 minutes",
            "rankwant-judge-1": "Up 3 minutes",
            "rankwant-web-1": "Up 3 minutes",
            "rankwant-postgres-1": "Up 3 minutes (healthy)",
            "rankwant-redis-1": "Up 3 minutes (healthy)",
            "rankwant-minio-1": "Up 3 minutes",
            "rankwant-ci-runner": "Up 3 minutes",
        },
        "origin_api": 200,
        "origin_web": 200,
        "public_api": 200,
        "runners": [
            {
                "name": "nsn-pc-rankwant-container",
                "status": "online",
                "labels": [{"name": "self-hosted"}, {"name": "rankwant"}, {"name": "rankwant-container"}],
            }
        ],
        "tasks": {
            "RankWant CI Runner Watchdog": {"state": "Ready", "last_run": "2026-09-18T05:04:00.0000000Z"},
            "RankWant CI Daily Report": {"state": "Ready", "last_run": "2026-09-18T03:00:00.0000000Z"},
            "RankWant Monthly Backup": {"state": "Ready", "last_run": "2026-09-17T15:32:47.0000000Z"},
            "RankWant Tunnel Monitor": {"state": "Ready", "last_run": "2026-09-18T05:05:00.0000000Z"},
        },
        "boot": _AR_BOOT,
    }
    facts.update(overrides)
    return facts


def _after_reboot(facts: object) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "facts.json"
        path.write_text(facts if isinstance(facts, str) else json.dumps(facts), encoding="utf-8")
        return run([PY, "tools/check_after_reboot.py", "--facts", str(path)])


def _after_reboot_expect(label: str, facts: object, wanted: int, needle: str) -> tuple[bool, str]:
    code, out = _after_reboot(facts)
    if code != wanted or needle not in out:
        return False, f"after_reboot/{label}: exit {code} ({wanted} kerak), «{needle}» — {out.strip()[-160:]}"
    return True, f"after_reboot/{label}: tutildi (exit {code})"


def neg_after_reboot_all_back_passes() -> tuple[bool, str]:
    # Positive control: without it every case below passes on a check that always fails.
    code, out = _after_reboot(_ar_facts())
    if code != 0:
        return False, f"after_reboot/nazorat: sog' holat exit {code} berdi — {out.strip()[-160:]}"
    return True, "after_reboot/nazorat: hamma halqa qaytgan holat o'tdi (exit 0)"


def neg_after_reboot_container_missing() -> tuple[bool, str]:
    facts = _ar_facts()
    del facts["containers"]["rankwant-judge-1"]
    return _after_reboot_expect("judge konteyneri yo'q", facts, 1, "rankwant-judge-1")


def neg_after_reboot_database_not_healthy() -> tuple[bool, str]:
    facts = _ar_facts()
    facts["containers"]["rankwant-postgres-1"] = "Up 3 minutes (health: starting)"
    return _after_reboot_expect("postgres healthy emas", facts, 1, "rankwant-postgres-1")


def neg_after_reboot_tunnel_down() -> tuple[bool, str]:
    return _after_reboot_expect("tunnel o'lik", _ar_facts(public_api=503), 1, "tunnel")


def neg_after_reboot_runner_without_label() -> tuple[bool, str]:
    runners = [
        {"name": "nsn-pc-rankwant-container", "status": "online", "labels": [{"name": "rankwant-container"}]}
    ]
    return _after_reboot_expect("runner rankwant label'siz", _ar_facts(runners=runners), 1, "GitHub runner")


def neg_after_reboot_watchdog_idle_since_boot() -> tuple[bool, str]:
    facts = _ar_facts()
    facts["tasks"]["RankWant CI Runner Watchdog"]["last_run"] = "2026-09-17T23:00:00.0000000Z"
    return _after_reboot_expect("watchdog reboot'dan keyin yurmagan", facts, 1, "Watchdog")


def neg_after_reboot_second_runner_half_commissioned() -> tuple[bool, str]:
    facts = _ar_facts()
    facts["runners"] = [
        *facts["runners"],
        {
            "name": "nsn-pc-rankwant-container-2",
            "status": "online",
            "labels": [{"name": "self-hosted"}, {"name": "rankwant"}],
        },
    ]
    return _after_reboot_expect(
        "ikkinchi runner GitHub'da, konteyner yo'q",
        facts,
        1,
        "rankwant-ci-runner-2",
    )


def neg_after_reboot_unreadable_facts() -> tuple[bool, str]:
    return _after_reboot_expect("o'qib bo'lmagan faktlar", "{not json", 2, "o'lchab bo'lmadi")


def _report_notify(attention: object, mode: str = "print") -> tuple[int, str]:
    """`runner_report.py` notification path on fixture attention items: exit code and output."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "attention.json"
        path.write_text(
            attention if isinstance(attention, str) else json.dumps(attention), encoding="utf-8"
        )
        return run(
            [PY, "tools/runner_report.py", "--attention", str(path), "--notify", mode,
             "--out", str(Path(tmp) / "daily-report.md")]
        )


def neg_report_attention_notifies() -> tuple[bool, str]:
    # Positive control: without it, a notification that never fires passes every case below.
    code, out = _report_notify(["CI (main, 09-17 18:30): failure", "runner nsn-pc offline"])
    if code != 0 or "<toast" not in out or "2 ta e'tibor bandi" not in out or "failure" not in out:
        return False, f"runner_report/nazorat: exit {code} — {out.strip()[-160:]}"
    return True, "runner_report/nazorat: e'tibor bandi bildirishnoma yasadi (exit 0)"


def neg_report_quiet_without_attention() -> tuple[bool, str]:
    code, out = _report_notify([])
    if code != 0 or "<toast" in out:
        return False, f"runner_report/tinch kun: exit {code}, bildirishnoma chiqdi — {out.strip()[-160:]}"
    return True, "runner_report/tinch kun: bildirishnoma chiqmadi (exit 0)"


def neg_report_notify_off_is_silent() -> tuple[bool, str]:
    code, out = _report_notify(["runner offline"], mode="off")
    if code != 0 or "<toast" in out:
        return False, f"runner_report/--notify off: exit {code} — {out.strip()[-160:]}"
    return True, "runner_report/--notify off: jim qoldi (exit 0)"


def neg_report_escapes_markup() -> tuple[bool, str]:
    # An unescaped `&` or `<` from a run name would make the toast XML unparseable,
    # and Windows would then silently show nothing.
    code, out = _report_notify(["CI <web> & judge yiqildi"])
    payload = next((line for line in out.splitlines() if line.startswith("<toast")), "")
    if code != 0 or not payload:
        return False, f"runner_report/belgi: exit {code} — {out.strip()[-160:]}"
    if "&amp;" not in payload or "&lt;web&gt;" not in payload:
        return False, f"runner_report/belgi: XML'da qochirilmagan belgi — {payload[:160]}"
    try:
        minidom.parseString(payload)
    except Exception as exc:  # noqa: BLE001 - any parse failure is the bug we look for
        return False, f"runner_report/belgi: XML o'qilmadi — {exc}"
    return True, "runner_report/belgi: `<` va `&` qochirildi, XML o'qildi"


def neg_report_unreadable_attention() -> tuple[bool, str]:
    code, out = _report_notify("{not json", mode="print")
    if code != 2 or "o'qilmadi" not in out:
        return False, f"runner_report/o'qib bo'lmagan bandlar: exit {code} (2 kerak) — {out.strip()[-160:]}"
    return True, "runner_report/o'qib bo'lmagan bandlar: exit 2"


def neg_negative_rejects_unknown_group() -> tuple[bool, str]:
    """Notanish guruh nomi «0/0 ✓» bo'lib yashil qolmasinmi?

    ⚠️ 2026-09-18 da o'lchandi: `main()` da `only = argv[1]`, mos guruh
    topilmasa `total = 0` qolardi va hisobot `Salbiy testlar: 0/0 ✓` bo'lib
    **exit 0** qaytarardi. Ya'ni guruh nomi xato terilsa yoki o'zgarsa,
    to'plam hech narsa tekshirmasdan yashil ko'rinardi — CI jimgina ko'r
    bo'lardi va buni ko'rsatadigan hech qanday belgi qolmasdi.

    Nazorat ham shu yerda: MAVJUD guruh nomi bilan chaqirilganda chiqish nol
    bo'lishi shart, aks holda tuzatish guruhlarni umuman ishlamaydigan qilib
    qo'ygan bo'lardi. Nazorat uchun `deploy_lock` olingan — u `tooling`
    guruhiga kirmaydi, ya'ni o'zini-o'zi chaqirib rekursiyaga tushmaydi
    (`_run_deploy` stub docker bilan ishlaydi, deploy qilmaydi).
    """
    code, out = run([PY, "tools/check_negative.py", "deploy_lock"])
    if code != 0:
        return False, (
            f"mavjud guruh rad etildi (exit {code}) — himoya juda qattiq: "
            f"{out.strip().splitlines()[:2]}"
        )
    code, out = run([PY, "tools/check_negative.py", "nosuchgroup"])
    if code == 0:
        return False, (
            "notanish guruh YASHIL qoldi (exit 0) — "
            f"o'lchov yo'q, hisobot: {out.strip()[-80:]}"
        )
    if "noma'lum guruh" not in out:
        return False, f"notanish guruh to'xtadi (exit {code}), lekin sabab ko'rinmadi"
    return True, f"notanish guruh rad etildi (exit {code}), sabab aytildi"


CASES: list[tuple[str, list[tuple[str, object]]]] = [
    (
        "i18n",
        [
            ("bo'sh qiymat", neg_i18n_blank_value),
            ("rozilik matnida havola o'rni yo'q", neg_i18n_consent_link_dropped),
            ("yetishmayotgan kalit", neg_i18n_missing_key),
            ("kodda bor, manbada yo'q", neg_i18n_used_but_absent),
            ("prefikssiz kalit", neg_i18n_bare_key),
            ("mamlakat jadvaldan til tushib qoldi", neg_i18n_country_locale_dropped),
            ("mamlakat ICU tili jadvalga qo'shildi", neg_i18n_country_icu_locale_added),
            ("mamlakat jadvalida kod yetishmaydi", neg_i18n_country_row_missing),
            ("mamlakat jadvalida bo'sh qiymat", neg_i18n_country_row_blank),
            ("ko'rib chiqish varaqasi eskirgan", neg_i18n_review_sheet_stale),
            ("varaqda eski kalit qolgan", neg_i18n_review_sheet_old_key),
            ("paritet keyingi qoidani to'smaydi", neg_i18n_parity_does_not_mask),
            ("shablon oila kalitisiz", neg_i18n_template_family),
            ("server evict bilan chegaralangan", neg_i18n_server_drops_locales),
            ("server lug'atda til yetishmaydi", neg_i18n_server_missing_locale),
            ("reyestr modul ichiga qaytsa tutilsin", neg_i18n_registry_module_local),
            ("reyestr to'liq tozalansa tutilsin", neg_i18n_registry_cleared),
            ("runtime dev throw yo'q", neg_i18n_runtime_dev_throw),
            ("runtime takroriy jurnal", neg_i18n_runtime_dedup),
        ],
    ),
    (
        "contrast",
        [
            ("buzilgan juftlik", neg_contrast_bad_pair),
            ("o'qib bo'lmaydigan qiymat", neg_contrast_unreadable_token),
        ],
    ),
    (
        "docs",
        [
            ("buzilgan havola", neg_docs_broken_link),
            ("mavjud bo'lmagan ADR havolasi", neg_docs_missing_adr),
            ("tadqiqotda havola baribir tekshirilsin", neg_docs_research_link_still_checked),
            ("istisno faqat docs/research ga", neg_docs_research_exemption_is_scoped),
        ],
    ),
    (
        "confusables",
        [
            ("identifikatorda kirill", neg_confusable_cyrillic_identifier),
            ("matndagi grek harf xato bermasin", neg_confusable_formula_allowed),
        ],
    ),
    (
        "email_locales",
        [
            ("yetishmayotgan til", neg_email_missing_locale),
            ("bo'sh matn", neg_email_blank_value),
            ("ro'yxatda yo'q til", neg_email_undeclared_locale),
        ],
    ),
    (
        "locales_parity",
        [
            ("LANGUAGES da til yetishmaydi", neg_parity_missing_locale),
            ("LOCALES da ortiqcha til", neg_parity_extra_locale),
        ],
    ),
    (
        "hardcoded",
        [
            ("admin faylda qattiq yozilgan matn", neg_hardcoded_prose),
            ("tilsiz sana formati", neg_hardcoded_locale_less_date),
            ("raqam bilan boshlangan matn", neg_hardcoded_number_in_prose),
            ("haqiqiy rang o'tadi", neg_hardcoded_actual_colour_passes),
            ("o'lchov birligi o'tadi, so'z qoladi", neg_hardcoded_number_unit_passes),
            ("kengaytirilgan doira o'qiladi", neg_hardcoded_wide_scope),
            ("viewBox o'tadi", neg_hardcoded_viewbox_passes),
            ("bir so'zli yorliq tutilsin", neg_hardcoded_single_word_label),
        ],
    ),
    (
        "workers",
        [
            ("fail_open yopiq bo'lsa tutilsin", neg_workers_fail_open_false),
            ("o'qib bo'lmasa xato, «yaxshi» emas", neg_workers_unreadable_is_not_green),
            ("CRLF li `True` ham «ha» bo'lsin", neg_workers_crlf_stub_passes),
            ("himoyalangan holat yashil", neg_workers_restored_gate),
        ],
    ),
    (
        "ci",
        [
            ("runner oflayn bo'lsa qizil", neg_ci_offline_runner_is_red),
            ("startup_failure runner'dan mustaqil", neg_ci_startup_failure_is_red),
            ("qotib qolgan run tutilsin", neg_ci_stuck_run_is_red),
            ("o'qib bo'lmasa exit 2, «yashil» emas", neg_ci_unreadable_is_not_green),
            ("sog'lom holat yashil", neg_ci_healthy_gate),
        ],
    ),
    (
        "backup",
        [
            ("kesilgan arxiv rad etilsin", neg_backup_truncated_archive),
            ("gzip butun, dump chala — rad etilsin", neg_backup_missing_trailer),
            ("butun dump o'tadi", neg_backup_good_dump_passes),
        ],
    ),
    (
        "ordering",
        [
            ("tiebreaker yo'q bo'lsa qizil", neg_ordering_missing_tiebreaker),
            ("`ordering_fields` qoidaga tushmaydi", neg_ordering_fields_not_confused),
        ],
    ),
    (
        "icons",
        [
            ("to'plamda kalit yetishmaydi", neg_icons_pack_missing_key),
            ("qat'iy zona registrga tushsa", neg_icons_fixed_zone_leaks),
            ("camelCase kalit yetishmaydi", neg_icons_camelcase_key_missing),
        ],
    ),
    (
        "ci_disk",
        [
            ("CI tozalash qadami yo'q", neg_ci_disk_cleanup_removed),
            ("deploy tozalash qadami yo'q", neg_ci_disk_deploy_cleanup_removed),
            ("nightly e2e tozalash qadami yo'q", neg_ci_disk_nightly_cleanup_removed),
        ],
    ),
    (
        "markup_cookie",
        [
            ("boot skriptda sozlama yo'q", neg_markup_cookie_boot_missing),
            ("parse da sozlama yo'q", neg_markup_cookie_parse_missing),
        ],
    ),
    (
        "verdict_codes",
        [
            ("web'da kod yetishmasa qizil", neg_verdict_code_missing),
            ("bir tilda yorliq yetishmasa qizil", neg_verdict_label_missing),
        ],
    ),
    (
        "tooling",
        [
            ("Store stub'i rad etilsin", neg_picker_rejects_store_stub),
            ("ishlaydigan python topilsin", neg_picker_finds_working_python),
            ("mutatsiya baytlarni saqlasin", neg_mutation_restores_bytes),
            ("tor oqimda qulamasin", neg_checker_survives_narrow_stdout),
            ("yangi branch darvozasiz qolmasin", neg_hook_gates_new_branch),
            ("notanish guruh yashil qolmasin", neg_negative_rejects_unknown_group),
        ],
    ),
    (
        "web_unit",
        [
            ("buzuq cookie parse'ni Vitest tutsin", neg_web_unit_tests_catch_broken_cookie),
        ],
    ),
    (
        "push_guard",
        [
            ("soxta muallif rad etilsin", neg_push_guard_placeholder_author),
            ("haqiqiy muallif o'tsin", neg_push_guard_real_author_passes),
            ("e'lon qilingan tarix to'smasin", neg_push_guard_published_history_ignored),
            ("main ga to'g'ridan push rad etilsin", neg_push_guard_main_rejected),
            ("favqulodda kalit ishlasin", neg_push_guard_override_allows_main),
            ("ifloslangan config tutilsin", neg_push_guard_polluted_config),
            ("hook guard'ni chaqirsin", neg_hook_wires_push_guard),
            ("tripwire config yozuvini tutsin", neg_fingerprint_catches_config_write),
        ],
    ),
    (
        "monitor",
        [
            ("API yolg'iz yiqilsa tutilsin", neg_monitor_api_only_outage),
            ("ikkala manzil 200 bo'lsa yashil", neg_monitor_healthy_gate),
            (
                "qatlam o'qilmasa exit 2, «yashil» emas",
                neg_monitor_unreadable_is_not_green,
            ),
            (
                "konteyner yiqilishi ko'prik deb o'qilmasin",
                neg_monitor_container_down_is_not_bridge,
            ),
            (
                "ichkarida javob yo'q bo'lsa restart qilinmasin",
                neg_monitor_app_down_is_not_restarted,
            ),
            ("handoff qoidasi saqlansin", neg_monitor_handoff_guard_holds),
        ],
    ),
    (
        "deploy_window",
        [
            ("faol contest bo'lsa deploy to'xtasin", neg_deploy_window_live_contest),
        ],
    ),
    (
        "env_example",
        [
            ("majburiy kalit o'chsa tutilsin", neg_env_example_required_missing),
            ("majburiy kalit izohga aylansa tutilsin", neg_env_example_required_commented),
            ("compose'ga yangi o'zgaruvchi tutilsin", neg_env_example_new_compose_var),
            ("settings'ga yangi o'zgaruvchi tutilsin", neg_env_example_new_setting),
            ("shablondagi sir qiymati tutilsin", neg_env_example_secret_value),
        ],
    ),
    (
        "decisions",
        [
            ("offsite standarti qaytsa tutilsin", neg_decisions_backup_offsite),
            ("push guard uzilsa tutilsin", neg_decisions_push_guard_unwired),
            ("hosted runner qo'shilsa tutilsin", neg_decisions_hosted_runner),
            (
                "runner compose'da rankwant label'i tushsa tutilsin",
                neg_decisions_runner_compose_label_dropped,
            ),
            (
                "runner entrypoint'da rankwant label'i tushsa tutilsin",
                neg_decisions_runner_entrypoint_label_dropped,
            ),
            ("deploy push'ga qaytsa tutilsin", neg_decisions_deploy_on_push),
            ("til qoidasi o'chsa tutilsin", neg_decisions_language_rule),
            ("qarorlar jadvali o'chsa tutilsin", neg_decisions_table_removed),
            ("endonim tor ekranda chegarasiz qolsa tutilsin", neg_decisions_locale_label_unbounded),
            ("tor ekranda til kodi qaytsa tutilsin", neg_decisions_locale_code_restored),
            ("panel tor ekranda viewport'ga bog'lanmasa tutilsin", neg_decisions_locale_panel_not_anchored),
            (
                "`aria-label` ko'rinadigan endonimni yo'qotsa tutilsin",
                neg_decisions_locale_label_in_name_lost,
            ),
            ("kirish yorlig'i o'ralsa tutilsin", neg_decisions_signin_label_wraps),
            (
                "cookie havoladan ustun bo'lsa tutilsin",
                neg_decisions_locale_cookie_beats_link,
            ),
            (
                "til sarlavhasi `next()` dan keyin yozilsa tutilsin",
                neg_decisions_locale_header_after_next,
            ),
            (
                "havoladagi til cookie'ga yozilmasa tutilsin",
                neg_decisions_locale_link_not_remembered,
            ),
            (
                "tanlov `?lang=` ni tozalamasa tutilsin",
                neg_decisions_locale_choice_keeps_param,
            ),
            (
                "mehmon s-maxage olib tashlansa tutilsin",
                neg_decisions_home_cache_ttl_dropped,
            ),
            (
                "kirgan javob public bo'lsa tutilsin",
                neg_decisions_home_cache_logged_in_public,
            ),
            (
                "proxy kesh qarorini qo'llamasa tutilsin",
                neg_decisions_home_cache_proxy_unwired,
            ),
            (
                "worker catch-all qaytsa tutilsin",
                neg_decisions_home_worker_catchall_restored,
            ),
            (
                "zaxira migratsiyadan keyin qolsa tutilsin",
                neg_decisions_deploy_backup_after_migrate,
            ),
            (
                "muzlatish qulfdan keyin tekshirilsa tutilsin",
                neg_decisions_deploy_freeze_after_lock,
            ),
            (
                "SHA teg `up` dan keyin qo'yilsa tutilsin",
                neg_decisions_deploy_tag_after_up,
            ),
            (
                "watcher tiriklikni tekshirmasa tutilsin",
                neg_decisions_auto_deploy_no_liveness,
            ),
            (
                "qayta urinish yozuvi deploy'dan keyin bo'lsa tutilsin",
                neg_decisions_auto_deploy_attempt_after_deploy,
            ),
            ("deploy darvozasi uzilsa tutilsin", neg_decisions_deploy_gate_unwired),
            ("deploy qulfi olib tashlansa tutilsin", neg_decisions_deploy_lock_removed),
            ("deploy web'ni qurmasa tutilsin", neg_decisions_deploy_skips_web),
            ("sayt qidiruvga yopilsa tutilsin", neg_decisions_site_closed_to_search),
            ("AI krauler ro'yxatdan tushsa tutilsin", neg_decisions_ai_crawler_dropped),
            ("sidebar'ga oddiy Link qaytsa tutilsin", neg_decisions_nav_eager_link),
            ("bosh sahifaga oddiy Link qaytsa tutilsin", neg_decisions_home_main_eager_link),
            ("IntentLink darhol prefetch qilsa tutilsin", neg_decisions_intent_link_eager),
            ("lug'at prop'ga qaytsa tutilsin", neg_decisions_dictionary_prop),
            ("lug'at fayli keshlanmasa tutilsin", neg_decisions_dictionary_not_cached),
            ("lug'at middleware'dan o'tsa tutilsin", neg_decisions_dictionary_through_proxy),
            (
                "qaytib o'sha tilga o'tilsa lug'at yo'qolsa tutilsin",
                neg_decisions_dictionary_cache_unsynced,
            ),
            ("`uz` o'z qaytishi deb belgilansa tutilsin", neg_decisions_uz_marked_as_fallback),
            (
                "qamrov ro'yxatiga begona til qo'shilsa tutilsin",
                neg_decisions_content_source_locales_widened,
            ),
            ("teg bulutida belgi tushsa tutilsin", neg_decisions_content_marker_dropped),
            (
                "faoliyatda ikkinchi belgi tushsa tutilsin",
                neg_decisions_content_marker_dropped_in_activity,
            ),
            ("filtr chipida belgi o'chsa tutilsin", neg_decisions_filter_chip_unmarked),
            (
                "native option belgisi tarjimasiz qolsa tutilsin",
                neg_decisions_content_text_untranslated,
            ),
            (
                "tanlash ro'yxati qamrovni yashirsa tutilsin",
                neg_decisions_selector_coverage_hidden,
            ),
            ("User'dan tenglik ustuni o'chsa tutilsin", neg_decisions_dormant_user_field_removed),
            ("sinov label'i self-test'da o'tadi", neg_decisions_trial_label_selftest_allowed),
            ("sinov label'i boshqa workflow'da tutilsin", neg_decisions_trial_label_scoped),
            ("sandbox o'qilgan hamma faylni nusxalaydi", neg_decisions_sandbox_covers_reads),
            ("Security PR'da qaytsa tutilsin", neg_decisions_security_on_pr),
            ("smoke PR'da qaytsa tutilsin", neg_decisions_smoke_on_pr),
            ("runner-2 profile tushsa tutilsin", neg_decisions_runner2_profile_dropped),
            ("panel holatni e'lon qilmasa tutilsin", neg_decisions_drawer_trigger_state_lost),
            ("panel dialog rolini yo'qotsa tutilsin", neg_decisions_drawer_role_lost),
            ("fokus panelga kirmasa tutilsin", neg_decisions_drawer_focus_not_moved),
            ("fokus tugmaga qaytmasa tutilsin", neg_decisions_drawer_focus_not_returned),
            ("Esc panelni yopmasa tutilsin", neg_decisions_drawer_escape_lost),
            ("fon scroll'i qulflanmasa tutilsin", neg_decisions_drawer_scroll_lock_lost),
            ("KPI to'ri 2 ustunda qolsa tutilsin", neg_decisions_kpi_grid_stuck_at_2up),
            ("KPI to'ri 3 ustunga qaytsa tutilsin", neg_decisions_kpi_grid_3up_creeps_back),
            ("KPI raqami pog'onasi yo'qolsa tutilsin", neg_decisions_kpi_card_value_step_lost),
            ("KPI raqam prop'i e'tiborsiz qolsa tutilsin", neg_decisions_kpi_value_prop_ignored),
            ("profil `lg` da ikki ustunga qaytsa tutilsin", neg_decisions_profile_two_columns_at_lg),
            ("profil to'ri `2xl` da qolsa tutilsin", neg_decisions_profile_kpi_stuck_at_2xl),
            ("profil to'rida eskirgan `xl` pog'onasi qolsa tutilsin", neg_decisions_profile_kpi_step_redundant),
            ("profil raqami pog'onasi yo'qolsa tutilsin", neg_decisions_profile_kpi_value_step_lost),
            ("diapazon kalitlari doimiysi o'chirilsa tutilsin", neg_decisions_difficulty_keys_declaration_removed),
            ("diapazon doimiysidan `level` tushib qolsa tutilsin", neg_decisions_difficulty_keys_missing_level),
            ("diapazon yana kalit bo'yicha sanalsa tutilsin", neg_decisions_difficulty_count_ignores_keys),
            ("diapazon predikati doimiyni tashlasa tutilsin", neg_decisions_difficulty_predicate_reverted),
            ("header brendi o'chirilsa tutilsin", neg_decisions_header_brand_removed),
            ("sidebar brendi qaytsa tutilsin", neg_decisions_sidebar_brand_back),
            ("footer bitta ustunga tushsa tutilsin", neg_decisions_footer_single_column),
            ("footer privacy havolasi yo'qolsa tutilsin", neg_decisions_footer_privacy_link_lost),
        ],
    ),
    (
        "deploy_gate",
        [
            ("yashil main o'tadi (nazorat)", neg_deploy_gate_green_passes),
            ("o'chirilgan worktree deploy'ni to'xtatmaydi", neg_deploy_gate_vanished_checkout),
            ("o'qib bo'lmaydigan checkout to'xtatadi", neg_deploy_gate_broken_checkout),
            ("main emas — to'xtaydi", neg_deploy_gate_not_main),
            ("CI qizil — to'xtaydi", neg_deploy_gate_ci_failed),
            ("CI tugamagan — to'xtaydi", neg_deploy_gate_ci_running),
            ("Security run'i yo'q — to'xtaydi", neg_deploy_gate_security_missing),
            ("oxirgi qizil run yashilni bosadi", neg_deploy_gate_latest_run_wins),
            ("commit qilinmagan compose — to'xtaydi", neg_deploy_gate_dirty_compose_blocks),
            ("o'qib bo'lmagan ro'yxat — exit 2", neg_deploy_gate_unreadable),
            ("o'qib bo'lmagan compose holati — exit 2", neg_deploy_gate_unreadable_compose_status),
        ],
    ),
    (
        "deploy_lock",
        [
            ("band qulf ikkinchi deploy'ni to'xtatadi", neg_deploy_lock_held),
            ("yiqilgan deploy qulfni bo'shatadi", neg_deploy_lock_released),
        ],
    ),
    (
        "deploy_check",
        [
            ("web o'zgarishi eskirgan deb topiladi", neg_deploy_label_web_change_is_stale),
            ("docs commit'i web'ni eskirtirmaydi", neg_deploy_label_docs_commit_not_stale),
            ("built-at yo'qligi ko'rinadi", neg_deploy_build_label_absent_is_flagged),
            ("built-at bor bo'lsa ogohlantirilmaydi", neg_deploy_build_label_set_is_ok),
        ],
    ),
    (
        "runner_watchdog",
        [
            ("tasdiqlangan tiqilish restart qilinadi (nazorat)", neg_watchdog_restarts_confirmed_stall),
            ("bitta tekshiruv restart qilmaydi", neg_watchdog_first_sighting_waits),
            ("band runner'ga tegilmaydi", neg_watchdog_busy_runner_left_alone),
            ("yangi job tiqilish emas", neg_watchdog_fresh_job_left_alone),
            ("boshqa label'dagi job'ga tegilmaydi", neg_watchdog_foreign_labels_left_alone),
            ("tanaffus ichida qayta restart yo'q", neg_watchdog_cooldown_holds),
            ("o'qilmagan vaqt — exit 2", neg_watchdog_unreadable_time),
            ("ikkinchi runner restart qilinadi", neg_watchdog_second_runner_restarts),
        ],
    ),
    (
        "after_reboot",
        [
            ("hamma halqa qaytgan — o'tadi (nazorat)", neg_after_reboot_all_back_passes),
            ("konteyner yo'q — tutilsin", neg_after_reboot_container_missing),
            ("baza healthy emas — tutilsin", neg_after_reboot_database_not_healthy),
            ("tunnel o'lik — tutilsin", neg_after_reboot_tunnel_down),
            ("runner production label'siz — tutilsin", neg_after_reboot_runner_without_label),
            ("watchdog reboot'dan keyin yurmagan — tutilsin", neg_after_reboot_watchdog_idle_since_boot),
            ("o'qib bo'lmagan faktlar — exit 2", neg_after_reboot_unreadable_facts),
            ("ikkinchi runner yarim ochilsa tutilsin", neg_after_reboot_second_runner_half_commissioned),
        ],
    ),
    (
        "runner_report",
        [
            ("e'tibor bandi bildirishnoma yasaydi (nazorat)", neg_report_attention_notifies),
            ("tinch kunda bildirishnoma yo'q", neg_report_quiet_without_attention),
            ("--notify off jim qoladi", neg_report_notify_off_is_silent),
            ("`<` va `&` qochiriladi", neg_report_escapes_markup),
            ("o'qib bo'lmagan bandlar — exit 2", neg_report_unreadable_attention),
        ],
    ),
]


def main(argv: list[str]) -> int:
    only = argv[1] if len(argv) > 1 else None
    failures: list[str] = []
    total = 0

    # An unknown group name must not look like a pass. With `only` set and no
    # checker matching it, `total` stays 0 and the report reads
    # "Salbiy testlar: 0/0 ✓" while exiting 0 — a silent green that measured
    # nothing. Measured 2026-09-18: both `--help` and a typo'd group name
    # exited 0. A renamed group would leave CI blind with no signal at all.
    known = [name for name, _ in CASES]
    if only is not None and only not in known:
        print(f"  ✕ noma'lum guruh: {only!r} — hech narsa tekshirilmadi")
        print()
        print(f"Mavjud guruhlar ({len(known)}): {', '.join(known)}")
        print()
        print("O'lchov yo'q: guruh nomini tuzatib qayta yurgizing.")
        return 2

    # Old shart: Node tekshiruvi umuman ishlay oladimi? Buni BIR MARTA
    # tekshiramiz — mutatsiya ichida qilsak, «ishga tushmadi» ni
    # «buzuq holatni tutdi» deb o'qib qo'yardik.
    selected = {
        label
        for checker, cases in CASES
        if not only or checker == only
        for label, _ in cases
    }
    if selected & NODE_CASES:
        reason = node_precondition()
        if reason:
            print(f"  ✕ {reason}")
            print()
            print("1/1 salbiy test YIQILDI — muhit tayyor emas, o'lchov yo'q.")
            return 1

    # Monitor — WINDOWS darvozasi. Old shart mantig'i NODE bilan bir xil,
    # LEKIN yakuni boshqa: `powershell` faqat Windows'da bor, CI runner'i
    # esa Linux (o'lchandi). U yerda guruhni «yiqildi» deb ko'rsatish CI ni
    # DOIMIY qizil qilardi, «o'tdi» deb ko'rsatish esa yolg'on yashil
    # bo'lardi. Shuning uchun uchinchi yo'l: OCHIQ aytib o'tkazib
    # yuboriladi va hisobotning oxirida ko'rinadi. Windows'da — ya'ni
    # monitor haqiqatan ishlaydigan mashinada, pre-push hook'da — guruh
    # har doim ishlaydi.
    skipped: list[str] = []
    if selected & MONITOR_CASES:
        reason = monitor_precondition()
        if reason:
            if sys.platform == "win32":
                print(f"  ✕ {reason}")
                print()
                print("1/1 salbiy test YIQILDI — Windows darvozasi o'lchanmadi.")
                return 1
            skipped.append(f"monitor guruhi — {reason}")

    # Tripwire for the 2026-09-16 class of bug: a sandbox that leaks into this
    # repository and rewrites its config or switches its branch.
    before = _repo_fingerprint(ROOT)

    for checker, cases in CASES:
        if only and only != checker:
            continue
        if checker == "monitor" and skipped:
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

    after = _repo_fingerprint(ROOT)
    if before is None or after is None:
        skipped.append("haqiqiy repo tripwire'i — git holatini o'qib bo'lmadi")
    elif before != after:
        message = (
            "to'plam HAQIQIY repoga tegdi: .git/config yoki joriy branch o'zgardi "
            "(2026-09-16 dagi `test@example.com` hodisasi turi)"
        )
        print(f"  ✕ {message}")
        failures.append(message)

    print()
    if skipped:
        # Jimgina o'tkazib yuborish — yolg'on yashilning eng arzon turi.
        # Shuning uchun u hisobotda ALOHIDA qator bo'lib turadi.
        for row in skipped:
            print(f"  - O'TKAZIB YUBORILDI: {row}")
        print()
    if failures:
        print(
            f"{len(failures)}/{total} salbiy test YIQILDI — tekshiruv o'lik bo'lishi mumkin:"
        )
        for row in failures:
            print(f"  - {row}")
        return 1
    print(f"Salbiy testlar: {total}/{total} ✓ — har bir tekshiruv buzuq holatni tutdi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
