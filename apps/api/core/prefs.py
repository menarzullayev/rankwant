"""Ko'rinish sozlamalari sxemasi — `User.ui_prefs`.

Qarorlar: tema sozlagichi sessiyasi, D33–D36.

Sxema **guruhlangan va versiyalangan**:

    {
      "version": 2,
      "appearance": {"style", "accent", "font", "fontHeading", "size", "scale",
                     "lineHeight", "tracking", "width", "density", "navMode",
                     "navShape", "card", "pattern", "verdictStyle",
                     "statusStyle", "loadingStyle", "iconPack"},
      "tokens": {},        # kuchli rejim (D9) — flag bilan O'CHIQ (D43)
      "a11y": {"vision", "motion", "bigTargets", "strongFocus"},
      "templates": [{"name", "appearance", "a11y", "theme"?}],
      "problemset": {"hideTags", "hideSolved"},   # ADR-0024
      "sound": bool,       # v1 dan qoldi
      "effect": str        # v1 dan qoldi
    }

Nega guruhlangan: 20+ yassi kalitdan keyin validator ham, kelajakdagi
o'zgarish ham boshqarib bo'lmaydigan bo'ladi.

Nega `sound`/`effect` guruhga KO'CHIRILMADI: ular ko'rinish emas —
qaytarish aloqasi (ovoz, mavzu almashish effekti). Ko'chirish eski
qurilma nusxasini va eski klientni buzardi, foyda esa yo'q.

**Noma'lum versiya** (kelajakdagi klient yozgan, yoki buzilgan) —
SAQLANADI, lekin QO'LLANMAYDI (D36). Aks holda yangi klient yozgan
sozlamani eski klient o'chirib qo'yardi va odam yangi qurilmaga
qaytganda sozlamasi jimgina yo'qolardi.
"""

from __future__ import annotations

import re
from typing import Any

#: Joriy sxema versiyasi. O'zgarish orqaga mos bo'lmasa — oshiriladi va
#: `migrate()` ga yangi qadam qo'shiladi.
SCHEMA_VERSION = 2

THEMES = ("light", "dark", "system")
#: `null` — uslubning o'z shrifti (D14: Editorial/Terminal uni saqlaydi).
#: `plex` — v1 dan qolgan qiymat: eski hisoblarda saqlanib qolgan, shuning
#: uchun ro'yxatdan chiqarilmaydi.
FONTS = ("plex", "inter", "jakarta", "roboto", "dm-sans", "lexend")
#: Ildiz shrift o'lchami, foiz (D45) — klientdagi `SIZE_MIN/MAX/STEP`.
SIZE_MIN, SIZE_MAX, SIZE_STEP = 75, 150, 5
#: Tipografik shkala (D45), qator balandligi va harf oralig'i (D47),
#: kontent kengligi (D48) — hammasi klientdagi `clamp*` chegaralari.
SCALE_MIN, SCALE_MAX = 0.9, 1.15
LINE_HEIGHT_MIN, LINE_HEIGHT_MAX = 0.9, 1.4
TRACKING_MIN, TRACKING_MAX = -0.02, 0.06
WIDTH_MIN, WIDTH_MAX, WIDTH_STEP = 1000, 1800, 100
DENSITIES = ("compact", "comfortable", "spacious")
#: `normal` — oddiy; `protan` protanopiya VA deuteranopiya uchun (bir xil
#: o'q yo'qoladi); `tritan` — ko'k-sariq o'qi uchun (D44).
VISIONS = ("normal", "protan", "tritan")
#: Harakat darajasi (D49). `reduce` — v1 dan qolgan qiymat, eski
#: hisoblarda uchraydi; klient endi `system|full|mild|off` yuboradi.
MOTIONS = ("system", "full", "mild", "off", "reduce")
EFFECTS = ("none", "fade", "circle")

TEMPLATE_MAX = 5
TEMPLATE_NAME_MAX = 24
TOKEN_MAX = 64

#: Katalog maydonlari: navigatsiya, karta, naqsh, verdikt/holat/yuklanish
#: ko'rinishi va ikonka to'plami. Ularning RO'YXATI klientda (`nav-config.ts`,
#: `theme/*.ts`) va u tez-tez o'sadi — D54, D55, D57, D60, D62 shu haqda.
#:
#: Server ro'yxatni TAKRORLAMAYDI, faqat shaklini tekshiradi. Sabab: ikkinchi
#: nusxa jimgina eskiradi va yangi ikonka to'plami qo'shilgan kuni saqlash
#: 400 bera boshlardi — aynan shu holat 2026-09-18 da o'lchangan
#: (`docs/research/2026-09-18-appearance-audit/BOARD.md`). Sxemaning vazifasi
#: axlat va cheksiz satrni to'sish, mahsulot katalogini boshqarish emas.
CATALOG_KEYS = (
    "navMode",
    "navShape",
    "card",
    "pattern",
    "verdictStyle",
    "statusStyle",
    "loadingStyle",
    "iconPack",
)
APPEARANCE_KEYS = {
    "style",
    "accent",
    "font",
    "fontHeading",
    "size",
    "scale",
    "lineHeight",
    "tracking",
    "width",
    "density",
    *CATALOG_KEYS,
}

STYLE_RE = re.compile(r"[a-z-]{1,20}")
SLUG_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9-]{0,23}")
TOKEN_NAME_RE = re.compile(r"--rw-[a-z0-9-]{1,32}")
#: Token qiymati faqat rang yoki son — ixtiyoriy satr emas. `--rw-font`
#: kabi tipografiya tokenlarini shrift tanlagichi boshqaradi, matn emas.
TOKEN_VALUE_RE = re.compile(
    r"(#[0-9a-fA-F]{3,8}"
    r"|rgba?\([\d.,\s%/]+\)"
    r"|-?\d+(\.\d+)?(px|rem|em|%)?"
    r"|transparent)"
)


class PrefsError(ValueError):
    """Sxemaga mos kelmagan sozlama."""


def _clean_style(value: Any) -> str:
    if not isinstance(value, str) or not STYLE_RE.fullmatch(value):
        raise PrefsError("Style name is invalid")
    return value


def _clean_accent(value: Any) -> dict[str, int] | None:
    """Accent TUS sifatida saqlanadi, tayyor rang emas (D42).

    Sabab: bitta rang ikki muhitga sig'maydi (yorug' `L ≤ 0.1733`,
    qorong'i `L ≥ 0.2160` — oraliqlar kesishmaydi). Yorqinlikni har
    muhit uchun alohida hisoblash kerak, ya'ni xom hex saqlash
    yetarli emas.
    """
    if value is None:
        return None
    if not isinstance(value, dict):
        raise PrefsError("accent must be an object")
    hue, sat = value.get("hue"), value.get("sat")
    if not isinstance(hue, int) or isinstance(hue, bool) or not 0 <= hue <= 359:
        raise PrefsError("accent.hue must be an integer from 0 to 359")
    if not isinstance(sat, int) or isinstance(sat, bool) or not 0 <= sat <= 100:
        raise PrefsError("accent.sat must be an integer from 0 to 100")
    return {"hue": hue, "sat": sat}


def _clean_step(key: str, value: Any, low: int, high: int, step: int) -> int:
    """Butun son, chegara ichida va qadamga tushgan (`size`, `width`)."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise PrefsError(f"{key} must be an integer")
    if not low <= value <= high or value % step:
        raise PrefsError(f"{key} must be between {low} and {high} in steps of {step}")
    return value


def _clean_ratio(key: str, value: Any, low: float, high: float) -> float:
    """Kasr koeffitsiyent chegara ichida (`scale`, `lineHeight`, `tracking`).

    Klient qiymatni yuzdan biriga yaxlitlaydi; server ham shuni qiladi, aks
    holda `0.30000000000000004` kabi qiymat saqlanib qolardi.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PrefsError(f"{key} must be a number")
    if not low <= value <= high:
        raise PrefsError(f"{key} must be between {low} and {high}")
    return round(float(value), 3)


def _clean_slug(key: str, value: Any) -> str:
    """Katalog qiymati — qisqa slug. Ro'yxat klientda (`CATALOG_KEYS`)."""
    if not isinstance(value, str) or not SLUG_RE.fullmatch(value):
        raise PrefsError(
            f"{key} must be a short slug (`[a-zA-Z][a-zA-Z0-9-]*`, up to 24 characters)"
        )
    return value


def _clean_appearance(value: Any) -> dict[str, Any]:
    """Ko'rinish guruhi.

    ⚠️ `theme` bu yerda YO'Q. Mavzu allaqachon alohida `User.theme`
    maydonida (`default="system"`) va `PrefsSync` uni o'sha yerdan
    sinxronlaydi. Uni bu yerga ham qo'shish bir xil ma'noni ikki joyda
    saqlardi — qaysi biri ustun ekani noaniq bo'lib qolardi. Hujjatning
    o'z tamoyili shu: "bir xil ma'no ikki joyda — ziddiyat manbai".
    """
    if not isinstance(value, dict):
        raise PrefsError("appearance must be an object")
    unknown = set(value) - APPEARANCE_KEYS
    if unknown:
        raise PrefsError(f"Unknown appearance key: {sorted(unknown)[0]}")
    out: dict[str, Any] = {}
    if "style" in value:
        out["style"] = _clean_style(value["style"])
    if "accent" in value:
        out["accent"] = _clean_accent(value["accent"])
    for key in ("font", "fontHeading"):
        if key in value:
            font = value[key]
            if font is not None and font not in FONTS:
                raise PrefsError(f"{key} must be one of {FONTS} or null")
            out[key] = font
    if "size" in value:
        out["size"] = _clean_step("size", value["size"], SIZE_MIN, SIZE_MAX, SIZE_STEP)
    if "width" in value:
        out["width"] = _clean_step("width", value["width"], WIDTH_MIN, WIDTH_MAX, WIDTH_STEP)
    for key, low, high in (
        ("scale", SCALE_MIN, SCALE_MAX),
        ("lineHeight", LINE_HEIGHT_MIN, LINE_HEIGHT_MAX),
        ("tracking", TRACKING_MIN, TRACKING_MAX),
    ):
        if key in value:
            out[key] = _clean_ratio(key, value[key], low, high)
    if "density" in value:
        if value["density"] not in DENSITIES:
            raise PrefsError(f"density must be one of {DENSITIES}")
        out["density"] = value["density"]
    for key in CATALOG_KEYS:
        if key in value:
            out[key] = _clean_slug(key, value[key])
    return out


def _clean_a11y(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PrefsError("a11y must be an object")
    unknown = set(value) - {"vision", "motion", "bigTargets", "strongFocus"}
    if unknown:
        raise PrefsError(f"Unknown a11y key: {sorted(unknown)[0]}")
    out: dict[str, Any] = {}
    if "vision" in value:
        if value["vision"] not in VISIONS:
            raise PrefsError(f"vision must be one of {VISIONS}")
        out["vision"] = value["vision"]
    if "motion" in value:
        if value["motion"] not in MOTIONS:
            raise PrefsError(f"motion must be one of {MOTIONS}")
        out["motion"] = value["motion"]
    for key in ("bigTargets", "strongFocus"):
        if key in value:
            if not isinstance(value[key], bool):
                raise PrefsError(f"{key} must be a boolean")
            out[key] = value[key]
    return out


def _clean_tokens(value: Any) -> dict[str, str]:
    """Kuchli rejim tokenlari (D9).

    Hozir UI YO'Q (D43 — flag bilan o'chiq), lekin sxema tayyor turadi:
    aks holda flag yonadigan kunda yana migratsiya kerak bo'lardi.
    """
    if not isinstance(value, dict):
        raise PrefsError("tokens must be an object")
    if len(value) > TOKEN_MAX:
        raise PrefsError(f"At most {TOKEN_MAX} tokens")
    out: dict[str, str] = {}
    for name, raw in value.items():
        if not isinstance(name, str) or not TOKEN_NAME_RE.fullmatch(name):
            raise PrefsError(f"Invalid token name: {name}")
        if not isinstance(raw, str) or not TOKEN_VALUE_RE.fullmatch(raw.strip()):
            raise PrefsError(f"Invalid token value: {name}")
        out[name] = raw.strip()
    return out


def _clean_templates(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise PrefsError("templates must be a list")
    if len(value) > TEMPLATE_MAX:
        raise PrefsError(f"At most {TEMPLATE_MAX} templates")
    out: list[dict[str, Any]] = []
    names: set[str] = set()
    for row in value:
        if not isinstance(row, dict):
            raise PrefsError("A template must be an object")
        name = row.get("name")
        if not isinstance(name, str) or not name.strip() or len(name) > TEMPLATE_NAME_MAX:
            raise PrefsError(f"Template name must be 1–{TEMPLATE_NAME_MAX} characters")
        key = name.strip().casefold()
        if key in names:
            raise PrefsError(f"Duplicate template name: {name.strip()}")
        names.add(key)
        template: dict[str, Any] = {
            "name": name.strip(),
            "appearance": _clean_appearance(row.get("appearance", {})),
            "a11y": _clean_a11y(row.get("a11y", {})),
        }
        # Optional: templates saved before the theme was captured have none,
        # and the client then keeps the current mode. Other unknown keys are
        # still dropped, so this one is picked out on purpose.
        theme = row.get("theme")
        if theme is not None:
            if theme not in THEMES:
                raise PrefsError(f"theme must be one of {THEMES}")
            template["theme"] = theme
        out.append(template)
    return out


#: Problemset toggles (ADR-0024). Codeforces keeps them as account settings;
#: here they lived only in one browser's `localStorage`.
PROBLEMSET_KEYS = ("hideTags", "hideSolved")


def _clean_problemset(value: Any) -> dict[str, bool]:
    if not isinstance(value, dict):
        raise PrefsError("problemset must be an object")
    unknown = set(value) - set(PROBLEMSET_KEYS)
    if unknown:
        raise PrefsError(f"Unknown problemset setting: {sorted(unknown)[0]}")
    out: dict[str, bool] = {}
    for key, flag in value.items():
        if not isinstance(flag, bool):
            raise PrefsError(f"problemset.{key} must be a boolean")
        out[key] = flag
    return out


def migrate(raw: Any) -> dict[str, Any]:
    """v1 → v2. Noma'lum versiya O'ZGARTIRILMAYDI (D36)."""
    if not isinstance(raw, dict):
        return {}
    if raw.get("version") == SCHEMA_VERSION:
        return dict(raw)
    if raw.get("version") is not None:
        # Kelajakdagi yoki buzilgan versiya — tegmaymiz.
        return dict(raw)
    # v1 — yassi shakl: {"style", "sound", "effect"}
    out: dict[str, Any] = {"version": SCHEMA_VERSION}
    appearance: dict[str, Any] = {}
    if isinstance(raw.get("style"), str) and STYLE_RE.fullmatch(raw["style"]):
        appearance["style"] = raw["style"]
    out["appearance"] = appearance
    for key in ("sound", "effect"):
        if key in raw:
            out[key] = raw[key]
    return out


def applies(raw: Any) -> bool:
    """Bu sozlamani qo'llash mumkinmi? Noma'lum versiya — yo'q (D36)."""
    return migrate(raw).get("version") == SCHEMA_VERSION


def validate(raw: Any) -> dict[str, Any]:
    """To'liq tekshiruv. Xato bo'lsa `PrefsError` ko'tariladi."""
    if not isinstance(raw, dict):
        raise PrefsError("An object was expected")
    out: dict[str, Any] = {"version": SCHEMA_VERSION}
    if "appearance" in raw:
        out["appearance"] = _clean_appearance(raw["appearance"])
    if "tokens" in raw:
        out["tokens"] = _clean_tokens(raw["tokens"])
    if "a11y" in raw:
        out["a11y"] = _clean_a11y(raw["a11y"])
    if "templates" in raw:
        out["templates"] = _clean_templates(raw["templates"])
    if "problemset" in raw:
        out["problemset"] = _clean_problemset(raw["problemset"])
    if "sound" in raw:
        if not isinstance(raw["sound"], bool):
            raise PrefsError("sound must be a boolean")
        out["sound"] = raw["sound"]
    if "effect" in raw:
        if raw["effect"] not in EFFECTS:
            raise PrefsError(f"effect must be one of {EFFECTS}")
        out["effect"] = raw["effect"]
    unknown = set(raw) - {
        "version",
        "appearance",
        "tokens",
        "a11y",
        "templates",
        "problemset",
        "sound",
        "effect",
    }
    if unknown:
        raise PrefsError(f"Unknown setting: {sorted(unknown)[0]}")
    return out
