"""Ko'rinish sozlamalari sxemasi — `User.ui_prefs`.

Qarorlar: tema sozlagichi sessiyasi, D33–D36.

Sxema **guruhlangan va versiyalangan**:

    {
      "version": 2,
      "appearance": {"style", "theme", "accent", "font", "size", "density"},
      "tokens": {},        # kuchli rejim (D9) — flag bilan O'CHIQ (D43)
      "a11y": {"vision", "motion", "bigTargets", "strongFocus"},
      "templates": [{"name", "appearance", "a11y"}],
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
FONTS = ("plex", "inter", "jakarta", "roboto", "dm-sans")
SIZES = (90, 100, 110, 120)
DENSITIES = ("compact", "comfortable", "spacious")
#: `normal` — oddiy; `protan` protanopiya VA deuteranopiya uchun (bir xil
#: o'q yo'qoladi); `tritan` — ko'k-sariq o'qi uchun (D44).
VISIONS = ("normal", "protan", "tritan")
MOTIONS = ("system", "reduce")
EFFECTS = ("none", "fade", "circle")

TEMPLATE_MAX = 5
TEMPLATE_NAME_MAX = 24
TOKEN_MAX = 64

STYLE_RE = re.compile(r"[a-z-]{1,20}")
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
        raise PrefsError("Uslub nomi noto'g'ri")
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
        raise PrefsError("accent obyekt kutilgan")
    hue, sat = value.get("hue"), value.get("sat")
    if not isinstance(hue, int) or isinstance(hue, bool) or not 0 <= hue <= 359:
        raise PrefsError("accent.hue 0–359 oralig'ida butun son bo'lsin")
    if not isinstance(sat, int) or isinstance(sat, bool) or not 0 <= sat <= 100:
        raise PrefsError("accent.sat 0–100 oralig'ida butun son bo'lsin")
    return {"hue": hue, "sat": sat}


def _clean_appearance(value: Any) -> dict[str, Any]:
    """Ko'rinish guruhi.

    ⚠️ `theme` bu yerda YO'Q. Mavzu allaqachon alohida `User.theme`
    maydonida (`default="system"`) va `PrefsSync` uni o'sha yerdan
    sinxronlaydi. Uni bu yerga ham qo'shish bir xil ma'noni ikki joyda
    saqlardi — qaysi biri ustun ekani noaniq bo'lib qolardi. Hujjatning
    o'z tamoyili shu: "bir xil ma'no ikki joyda — ziddiyat manbai".
    """
    if not isinstance(value, dict):
        raise PrefsError("appearance obyekt kutilgan")
    unknown = set(value) - {"style", "accent", "font", "size", "density"}
    if unknown:
        raise PrefsError(f"Noma'lum appearance kaliti: {sorted(unknown)[0]}")
    out: dict[str, Any] = {}
    if "style" in value:
        out["style"] = _clean_style(value["style"])
    if "accent" in value:
        out["accent"] = _clean_accent(value["accent"])
    if "font" in value:
        font = value["font"]
        if font is not None and font not in FONTS:
            raise PrefsError(f"font {FONTS} dan biri yoki null bo'lsin")
        out["font"] = font
    if "size" in value:
        if value["size"] not in SIZES:
            raise PrefsError(f"size {SIZES} dan biri bo'lsin")
        out["size"] = value["size"]
    if "density" in value:
        if value["density"] not in DENSITIES:
            raise PrefsError(f"density {DENSITIES} dan biri bo'lsin")
        out["density"] = value["density"]
    return out


def _clean_a11y(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PrefsError("a11y obyekt kutilgan")
    unknown = set(value) - {"vision", "motion", "bigTargets", "strongFocus"}
    if unknown:
        raise PrefsError(f"Noma'lum a11y kaliti: {sorted(unknown)[0]}")
    out: dict[str, Any] = {}
    if "vision" in value:
        if value["vision"] not in VISIONS:
            raise PrefsError(f"vision {VISIONS} dan biri bo'lsin")
        out["vision"] = value["vision"]
    if "motion" in value:
        if value["motion"] not in MOTIONS:
            raise PrefsError(f"motion {MOTIONS} dan biri bo'lsin")
        out["motion"] = value["motion"]
    for key in ("bigTargets", "strongFocus"):
        if key in value:
            if not isinstance(value[key], bool):
                raise PrefsError(f"{key} mantiqiy qiymat bo'lsin")
            out[key] = value[key]
    return out


def _clean_tokens(value: Any) -> dict[str, str]:
    """Kuchli rejim tokenlari (D9).

    Hozir UI YO'Q (D43 — flag bilan o'chiq), lekin sxema tayyor turadi:
    aks holda flag yonadigan kunda yana migratsiya kerak bo'lardi.
    """
    if not isinstance(value, dict):
        raise PrefsError("tokens obyekt kutilgan")
    if len(value) > TOKEN_MAX:
        raise PrefsError(f"Ko'pi bilan {TOKEN_MAX} ta token")
    out: dict[str, str] = {}
    for name, raw in value.items():
        if not isinstance(name, str) or not TOKEN_NAME_RE.fullmatch(name):
            raise PrefsError(f"Token nomi noto'g'ri: {name}")
        if not isinstance(raw, str) or not TOKEN_VALUE_RE.fullmatch(raw.strip()):
            raise PrefsError(f"Token qiymati noto'g'ri: {name}")
        out[name] = raw.strip()
    return out


def _clean_templates(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise PrefsError("templates ro'yxat kutilgan")
    if len(value) > TEMPLATE_MAX:
        raise PrefsError(f"Ko'pi bilan {TEMPLATE_MAX} ta shablon")
    out: list[dict[str, Any]] = []
    names: set[str] = set()
    for row in value:
        if not isinstance(row, dict):
            raise PrefsError("Shablon obyekt bo'lsin")
        name = row.get("name")
        if not isinstance(name, str) or not name.strip() or len(name) > TEMPLATE_NAME_MAX:
            raise PrefsError(f"Shablon nomi 1–{TEMPLATE_NAME_MAX} belgi bo'lsin")
        key = name.strip().casefold()
        if key in names:
            raise PrefsError(f"Shablon nomi takrorlandi: {name.strip()}")
        names.add(key)
        out.append(
            {
                "name": name.strip(),
                "appearance": _clean_appearance(row.get("appearance", {})),
                "a11y": _clean_a11y(row.get("a11y", {})),
            }
        )
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
        raise PrefsError("Obyekt kutilgan")
    out: dict[str, Any] = {"version": SCHEMA_VERSION}
    if "appearance" in raw:
        out["appearance"] = _clean_appearance(raw["appearance"])
    if "tokens" in raw:
        out["tokens"] = _clean_tokens(raw["tokens"])
    if "a11y" in raw:
        out["a11y"] = _clean_a11y(raw["a11y"])
    if "templates" in raw:
        out["templates"] = _clean_templates(raw["templates"])
    if "sound" in raw:
        if not isinstance(raw["sound"], bool):
            raise PrefsError("sound mantiqiy qiymat bo'lsin")
        out["sound"] = raw["sound"]
    if "effect" in raw:
        if raw["effect"] not in EFFECTS:
            raise PrefsError(f"effect {EFFECTS} dan biri bo'lsin")
        out["effect"] = raw["effect"]
    unknown = set(raw) - {"version", "appearance", "tokens", "a11y", "templates", "sound", "effect"}
    if unknown:
        raise PrefsError(f"Noma'lum sozlama: {sorted(unknown)[0]}")
    return out
