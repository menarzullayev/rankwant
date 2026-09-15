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

import gzip
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

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
    """
    env = dict(os.environ)
    env.pop("PYTHONUTF8", None)
    env["PYTHONIOENCODING"] = "cp1252"
    proc = subprocess.run(
        [PY, "tools/check_ordering.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    if "UnicodeEncodeError" in out:
        return False, "tor oqim: tekshiruv O'Z chiqishida quladi (UnicodeEncodeError)"
    if proc.returncode != 0:
        return False, f"tor oqim: tekshiruv exit {proc.returncode} berdi (0 kerak)"
    return True, "tor oqim: chiqish UTF-8 ga majburlandi, tekshiruv o'tdi"


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

        for cmd in (
            ["git", "init", "-q", "-b", "yangi-branch"],
            ["git", "config", "user.email", "test@example.com"],
            ["git", "config", "user.name", "test"],
            ["git", "add", "-A"],
            ["git", "commit", "-q", "-m", "birinchi"],
        ):
            made = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
            if made.returncode != 0:
                return False, f"hook: sinov repo'si yasalmadi — {' '.join(cmd)}"

        proc = subprocess.run(
            [_bash(), ".githooks/pre-push", "--print-files"],
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    listed = [line for line in (proc.stdout or "").splitlines() if line.strip()]
    if not listed:
        return False, (
            "hook/yangi branch: fayl ro'yxati BO'SH — upstream'siz push "
            "tekshirilmay o'tardi (darvoza jonsiz)"
        )
    if "muhim.py" not in listed:
        return False, f"hook/yangi branch: `muhim.py` ro'yxatda yo'q — {listed[:3]}"
    return True, f"hook/yangi branch: {len(listed)} fayl tekshiruvga olindi"


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


CASES: list[tuple[str, list[tuple[str, object]]]] = [
    (
        "i18n",
        [
            ("bo'sh qiymat", neg_i18n_blank_value),
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
]


def main(argv: list[str]) -> int:
    only = argv[1] if len(argv) > 1 else None
    failures: list[str] = []
    total = 0

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
