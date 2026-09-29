"""Statik accessibility tekshiruvi — axe'ni to'ldiradi (RW-ARCH-010).

⚠️ **Nega statik, nega axe YETARLI EMAS.**

`axe` — HAQIQIY brauzerda ishlaydi va faqat brauzer ko'radigan narsani
topadi: hisoblangan kontrast, DOM tartibi, `aria-labelledby` haqiqatan
mavjud elementga ishora qiladimi. Bu — eng ishonchli o'lchov, lekin u
**ishlayotgan stack** talab qiladi (compose + judge `--privileged`),
ya'ni PR'da ishlamaydi (`tests/e2e/README.md`).

Natijada eng ko'p uchraydigan uchta xato PR'da **umuman ko'rinmasdi**:

  1. `<img>` da `alt` yo'q — ekran o'quvchi fayl nomini o'qiydi.
  2. `<button>` da ko'rinadigan matn ham, `aria-label` ham yo'q —
     ekran o'quvchi «tugma» deydi, nima qilishini aytmaydi.
  3. `onClick` `<div>`/`<span>` da — klaviatura bilan bosilmaydi, ya'ni
     sichqonchasi yo'q odam uchun **butun funksiya yopiq**.

Uchinchisi eng og'iri va u **aynan statik ko'rinadi**: HTML'da `role`,
`tabIndex` va `onKeyDown` bo'lishi shart. Shu skript o'sha uchtasini
tekshiradi — arzon, PR'da ishlaydi, va `axe` qamrovini toraytirmaydi,
balki oldinga suradi.

To'liq qamrov (kontrast, tartib, ARIA grafi) `tests/e2e/` dagi axe
loyihasida qoladi — u staging deploy'dan keyin yuguradi.

Ishlatish:
    python tools/check_a11y.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "apps/web/src"

#: Tekshirilmaydigan papkalar.
SKIP_DIRS = {"node_modules", ".next", "locales"}

#: `<img ...>` ochilish tegi.
#:
#: ⚠️ `[^>]*?` (non-greedy) YARAMAYDI: `alt=""` keyingi satrda bo'lsa
#: regex birinchi `>` da to'xtab, `alt` ni ko'rmay qoladi va **yolg'on
#: musbat** beradi (o'lchandi 2026-09-24: ikkita to'g'ri `<img>`).
#: Shuning uchun teg oxiri `scan_tag` bilan topiladi.
IMG_START_RE = re.compile(r"<img\b", re.I)
#: `<button ...>` ochilish teglari.
#:
#: ⚠️ **`re.I` YO'Q — va bu o'lchandi.** `IGNORECASE` bilan bu regex
#: `<Button` (katta harf — TSX KOMPONENTI) ni ham tutardi. Komponent
#: `</Button>` bilan yopiladi, ya'ni `find_close_button` uning
#: yopilishini topa olmay keyingi HAQIQIY `</button>` gacha cho'zilardi
#: va ikkita elementning tanasi bitta bo'lib qo'shilib ketardi. Natija:
#: 15 ta yolg'on «ichma-ich tugma» va Customizer'dagi yorliqsiz
#: ikonka-tugma **ko'rinmay qolgan** (o'lchandi 2026-09-24 salbiy test
#: bilan).
#:
#: JSX qoidasi qat'iy: HTML tegi — kichik harf (`<button>`, `<img>`),
#: komponent — katta harf (`<Button>`). Shu farq yetarli.
#:
#: ⚠️ Teg OXIRI `scan_tag` bilan topiladi, regex bilan emas. Sabab:
#: `onClick={() => f()}` ichida `=>` bor, ya'ni `[^>]*?` birinchi `>`
#: da to'xtab, tegni yarmida kesadi. Natijada «tana» atributlarning
#: davomidan boshlanib, keyingi elementning matnini o'ziga qo'shib
#: oladi va yorliqsiz tugma **matnli bo'lib ko'rinadi** (o'lchandi
#: 2026-09-24).
BUTTON_START_RE = re.compile(r"<button\b")
#: Ikonka-tugma: `<button ...>\n  <XIcon` ko'rinishi.
ICON_BTN_RE = re.compile(r"<button\b([^>]*?)>\s*<(?P<icon>[A-Z]\w*)\b", re.S)

#: Interaktiv atributlar.
CLICK_ATTR = re.compile(r"\bonClick\s*=")
ROLE_ATTR = re.compile(r"\brole\s*=")
KEY_ATTR = re.compile(r"\bon(KeyDown|KeyUp|KeyPress)\s*=")
TAB_ATTR = re.compile(r"\btabIndex\s*=")

#: `aria-hidden` — ataylab ekran o'quvchidan yashirilgan element.
ARIA_HIDDEN = re.compile(r"\baria-hidden\s*=\s*(\"|'|\{)?\s*true")

#: Interaktiv bo'lmagan, lekin `onClick` olishi mumkin bo'lgan teglar.
TAG_OPEN_RE = re.compile(r"<(?P<tag>div|span|li|td|tr|section)\b")

#: **Ataylab istisno**: to'liq ekranli `scrim` (foni bosilganda yopiladigan
#: parda). WCAG 2.1.1 uchun `role` talab qilinmaydi, chunki funksiya
#: **faqat sichqoncha yordamchisi**: yopishning boshqa yo'li bor — `Escape`
#: (`rw-ov` overlay host o'zi tutadi) yoki ko'rinadigan «yopish» tugmasi.
#: Bunday elementni `role="button"` qilish NOTO'G'RI bo'lardi: ekran
#: o'quvchi ro'yxatida «Yopish tugmasi» ikkinchi marta chiqib, haqiqiy
#: tugmani topishni qiyinlashtirardi.
#:
#: Istisno **sinf nomi bo'yicha** tor qamrovda: `rw-ov-scrim` —
#: `globals.css` dagi yagona parda klassi. Boshqa har qanday `<div onClick>`
#: tekshiruvdan o'tadi.
SCRIM_CLASS = re.compile(r"\brw-ov-scrim\b")


def sanitize(text: str) -> str:
    """Izohlar va satr ichidagi misollarni olib tashlaydi.

    ⚠️ Bu SHART va o'lchandi: `updates/[id]/page.tsx` da izoh ichida
    ``oddiy `<img>` `` yozilgan. Uni skanerlasak, `scan_tag` izohdagi
    `<img>` ni teg deb o'qib, 30 satr pastdagi **to'g'ri** elementni
    ko'rmay qolardi — natijada yolg'on musbat (o'lchandi 2026-09-24).

    Izohlar matn **uzunligini saqlagan holda** bo'sh joyga
    almashtiriladi, shunda keyingi hisoblangan satr raqamlari to'g'ri
    qoladi.
    """
    def blank(m: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))

    text = re.sub(r"\{/\*.*?\*/\}", blank, text, flags=re.S)  # JSX izohi
    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)  # blok izoh
    text = re.sub(r"(?m)^\s*//.*$", blank, text)  # to'liq qator izohi
    return text


def iter_tsx() -> list[Path]:
    """Tekshiriladigan `.tsx` fayllar."""
    out: list[Path] = []
    for path in WEB.rglob("*.tsx"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        out.append(path)
    return sorted(out)


def scan_tag(text: str, start: int) -> str:
    """`<` dan boshlab teg oxirigacha bo'lgan matnni qaytaradi.

    JSX'da `>` ifoda ichida ham uchraydi (`onClick={() => x > 1}`), ya'ni
    oddiy `text.find(">")` tegni erta kesib qo'yardi va atributlar
    ko'rinmay qolardi. Shu sababli `{}`, `()` va tirnoq chuqurligi
    sanaladi.
    """
    depth = 0
    quote: str | None = None
    i = start
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == quote and text[i - 1] != "\\":
                quote = None
        elif ch in ('"', "'"):
            quote = ch
        elif ch in "{(":
            depth += 1
        elif ch in "})":
            depth -= 1
        elif ch == ">" and depth <= 0:
            return text[start : i + 1]
        i += 1
    return text[start:]


def check_img_alt(problems: list[str]) -> int:
    """Har bir `<img>` da `alt` bo'lsin (bo'sh bo'lsa ham).

    `alt=""` — to'g'ri javob DEKORATIV rasm uchun: ekran o'quvchi uni
    butunlay tashlab ketadi. Ya'ni tekshiruv `alt` ning MAVJUDLIGINI
    talab qiladi, mazmunini emas.
    """
    count = 0
    for path in iter_tsx():
        text = sanitize(path.read_text(encoding="utf-8"))
        pos = 0
        while True:
            match = IMG_START_RE.search(text, pos)
            if not match:
                break
            pos = match.start() + 1
            tag_text = scan_tag(text, match.start())
            count += 1
            if re.search(r"\balt\s*=", tag_text):
                continue
            rel = path.relative_to(ROOT).as_posix()
            line = text[: match.start()].count("\n") + 1
            problems.append(f"{rel}:{line} — `<img>` da `alt` yo'q")
    return count


def find_close_button(text: str) -> int:
    """Mos `</button>` indeksini topadi.

    ⚠️ **Ichma-ich tugma sanalmaydi** — HTML'da `<button>` boshqa
    `<button>` ni o'z ichiga olishi TAQIQLANGAN, ya'ni birinchi
    `</button>` har doim shu tegning yopilishi. Ilgari bu yerda
    chuqurlik sanalardi; u `BUTTON_RE` dagi `re.I` xatosi bilan
    qo'shilib, komponent (`<Button>`) ochilishini «ichki tugma» deb
    hisoblab, tanani keyingi haqiqiy tugmagacha cho'zardi (o'lchandi
    2026-09-24).
    """
    return text.find("</button>")


#: JSX ifodasi — `{...}` (ichma-ich qavslar sanaladi).
JSX_EXPR_RE = re.compile(r"\{[^{}]*\}", re.S)


def body_has_label(body: str) -> bool:
    """Tugma ichida ko'rinadigan yorliq bormi.

    ⚠️ Bu yerda **`{expr}` MATN hisoblanadi**. Sabab: `{children}`,
    `{label}`, `{action.label}` — hammasi chaqiruvchidan keladigan
    ko'rinadigan matn. Ularni «bo'sh» deb hisoblash 31 ta **yolg'on
    musbat** berdi (o'lchandi 2026-09-24): `ui/Button.tsx` dagi
    `{children}`, `ui/Table.tsx` dagi `{label}`, `ui/EmptyState.tsx`
    dagi `{action.label}` — uchtasi ham aslida to'g'ri.

    Faqat IKKI narsa matn EMAS:
      * ikonka komponenti (`<Icon …/>`, `<XIcon …/>`) — ekran o'quvchi
        uni ko'rmaydi;
      * sof «bo'sh» ifoda (`{busy && <Spinner />}`) — natijasi `false`
        yoki JSX ikonka.
    """
    # 1. Avval JSX ifodalarini matn belgisiga almashtiramiz.
    has_expr_text = False
    for m in JSX_EXPR_RE.finditer(body):
        inner = m.group(0)[1:-1].strip()
        if is_meaningful_expr(inner):
            has_expr_text = True
    # 2. Ikonka teglarini olib tashlaymiz.
    plain = re.sub(r"<[A-Z]\w*\b[^>]*/>", "", body, flags=re.S)
    plain = re.sub(r"</?[a-z]\w*\b[^>]*>", "", plain, flags=re.S)
    plain = re.sub(r"\{[^{}]*\}", "", plain, flags=re.S)
    if has_expr_text:
        return True
    return bool(re.search(r"[A-Za-z0-9]", plain))


def is_meaningful_expr(inner: str) -> bool:
    """`{expr}` ko'rinadigan matn beradimi?

    Ikonka yasaydigan ifoda matn emas: `<Spinner />`, `busy && <Spinner />`.
    Qolgani — matn (`children`, `label`, `t(locale, "x")`, `name`).
    """
    if not inner:
        return False
    # Butun ifoda bitta JSX tegi bo'lsa — matn emas.
    if re.fullmatch(r"<[^>]*/>", inner, re.S):
        return False
    # `cond && <Tag />` — natijasi `false` yoki ikonka.
    tail = inner.split("&&")[-1].strip()
    if re.fullmatch(r"<[^>]*/>", tail, re.S):
        return False
    # `cond ? <A/> : <B/>` — ikkisi ham ikonka bo'lsa matn emas.
    if "?" in inner and ":" in inner:
        arms = [a.strip() for a in inner.split("?", 1)[1].split(":", 1)]
        if all(re.fullmatch(r"<[^>]*/>", a, re.S) for a in arms):
            return False
    return True


def iter_buttons(text: str) -> list[tuple[int, str, int]]:
    """Har bir `<button>` uchun `(teg_boshi, atributlar, tana_boshi)`.

    Teg oxiri `scan_tag` bilan topiladi (izohга qarang), tana esa
    keyingi mos `</button>` da tugaydi.
    """
    out: list[tuple[int, str, int]] = []
    pos = 0
    while True:
        match = BUTTON_START_RE.search(text, pos)
        if not match:
            break
        pos = match.start() + 1
        tag_text = scan_tag(text, match.start())
        if tag_text.startswith("</"):
            continue
        attrs = tag_text[len("<button") : -1]
        out.append((match.start(), attrs, match.start() + len(tag_text)))
    return out


def button_body(text: str, body_start: int) -> str:
    """Tugma tanasi — keyingi mos `</button>` gacha (600 belgi bilan)."""
    after = text[body_start : body_start + 600]
    close = find_close_button(after)
    return after[:close] if close != -1 else after


def check_button_label(problems: list[str]) -> int:
    """Har bir `<button>` da ko'rinadigan matn YOKI `aria-label` bo'lsin.

    ⚠️ Faqat ikonka qo'yilgan tugma eng ko'p uchraydigan xato: ko'z
    ikonkani taniydi, ekran o'quvchi esa «tugma» deydi va nima
    qilishini aytmaydi.
    """
    count = 0
    for path in iter_tsx():
        text = sanitize(path.read_text(encoding="utf-8"))
        for start, attrs, body_start in iter_buttons(text):
            count += 1
            if re.search(r"\baria-label\s*=|\baria-labelledby\s*=", attrs):
                continue
            body = button_body(text, body_start)
            if body_has_label(body):
                continue
            rel = path.relative_to(ROOT).as_posix()
            line = text[:start].count("\n") + 1
            problems.append(
                f"{rel}:{line} — `<button>` da matn ham, `aria-label` ham yo'q"
            )
    return count


def check_click_targets(problems: list[str]) -> int:
    """`onClick` faqat interaktiv tegda yoki `role`+klaviatura bilan.

    ⚠️ Bu eng qimmatli tekshiruv: `<div onClick>` sichqoncha bilan
    ishlaydi, lekin **Tab bilan yetib bo'lmaydi** va Enter/Space uni
    ishga tushirmaydi. Ko'zdan yashirin, chunki sahifa to'g'ri
    ko'rinadi — faqat klaviatura foydalanuvchisi uchun yopiq.
    """
    count = 0
    for path in iter_tsx():
        text = sanitize(path.read_text(encoding="utf-8"))
        pos = 0
        while True:
            match = TAG_OPEN_RE.search(text, pos)
            if not match:
                break
            pos = match.start() + 1
            if pos > 0 and text[match.start() - 1] == "/":
                continue  # yopiluvchi teg `</div>`
            tag_text = scan_tag(text, match.start())
            if not CLICK_ATTR.search(tag_text):
                continue
            count += 1
            # To'liq ekranli parda — ataylab istisno (yuqoridagi izoh).
            if SCRIM_CLASS.search(tag_text) and not ARIA_HIDDEN.search(tag_text):
                # `aria-hidden` bo'lmasa ham istisno: parda ekran
                # o'quvchi uchun ko'rinmas (foni bo'sh `div`).
                continue
            has_role = ROLE_ATTR.search(tag_text) is not None
            has_key = KEY_ATTR.search(tag_text) is not None
            has_tab = TAB_ATTR.search(tag_text) is not None
            # `role="presentation"` — element ekran o'quvchi uchun
            # KO'RINMAYDI, ya'ni klaviatura manzili ham bo'lishi shart
            # emas. Bunday element faqat sichqoncha yordamchisi
            # (fon bosilganda yopish) va u yerda yopishning boshqa
            # yo'li bor.
            if re.search(r'\brole\s*=\s*["\'](presentation|none)["\']', tag_text):
                continue
            # `role="dialog"`/`menu`/`toolbar` — o'zi fokus konteyneri;
            # `onKeyDown` overlay host tomonidan markazlashtirilgan
            # (`OverlayHost` Escape ni tutadi).
            if re.search(r'\brole\s*=\s*["\'](dialog|alertdialog|menu)["\']', tag_text):
                continue
            if has_role and has_key:
                continue
            rel = path.relative_to(ROOT).as_posix()
            line = text[: match.start()].count("\n") + 1
            missing = []
            if not has_role:
                missing.append("`role`")
            if not has_key:
                missing.append("`onKeyDown`")
            if not has_tab:
                missing.append("`tabIndex`")
            problems.append(
                f"{rel}:{line} — `<{match.group('tag')} onClick>` da "
                + ", ".join(missing)
                + " yo'q (klaviatura bilan ishlamaydi)"
            )
    return count


def check_icon_only_buttons(problems: list[str]) -> int:
    """Ikonka-tugma `aria-label` siz qolmasin.

    ⚠️ `check_button_label` bilan takrorlanmasligi kerak: u **matn**
    borligini tekshiradi va `{t(locale, "auth.logout")}` ni matn deb
    to'g'ri qabul qiladi. Bu esa boshqa savolga javob beradi: tugma
    ichida **faqat ikonka** qolganmi (matn yo'q)?

    Ya'ni: ikonka bor Va ko'rinadigan matn yo'q ⇒ `aria-label` shart.
    """
    count = 0
    for path in iter_tsx():
        text = sanitize(path.read_text(encoding="utf-8"))
        for start, attrs, body_start in iter_buttons(text):
            if re.search(r"\baria-label\s*=|\baria-labelledby\s*=", attrs):
                continue
            body = button_body(text, body_start)
            has_icon = bool(re.search(r"<[A-Z]\w*\b[^>]*/>", body))
            if not has_icon:
                continue
            if body_has_label(body):
                continue
            count += 1
            rel = path.relative_to(ROOT).as_posix()
            line = text[:start].count("\n") + 1
            problems.append(
                f"{rel}:{line} — ikonka-tugmada `aria-label` yo'q"
            )
    return count


def main() -> int:
    problems: list[str] = []
    files = iter_tsx()
    imgs = check_img_alt(problems)
    buttons = check_button_label(problems)
    clicks = check_click_targets(problems)
    icons = check_icon_only_buttons(problems)

    print(
        f"Tekshirildi: {len(files)} tsx · {imgs} img · {buttons} button · "
        f"{clicks} onClick · {icons} ikonka-tugma"
    )
    if problems:
        unique = sorted(set(problems))
        print(f"\n{len(unique)} ta A11Y muammo:\n")
        for p in unique:
            print(f"  {p}")
        return 1
    print("A11Y statik qoidalar ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
