#!/usr/bin/env python3
"""Ikonka registri butunligini tekshiradi (D12).

Uch narsani kafolatlaydi:

1. **Har bir to'plam bir xil kalitlarga ega.** D12: yetishmagan ikonka
   asosiy to'plamdan OLINMAYDI, ya'ni jimgina zaxira yo'q. Bittasi
   yetishmasa — xato.
2. **Qat'iy zonalar to'plamlarga tushmagan** (D20 ①). `verdict.*` va
   `brand.*` almashmasligi kerak; ular registrda bo'lsa, kimdir ularni
   `Icon` orqali chizayotgan bo'ladi va qoida buziladi.
3. **Har bir kalitning domeni ma'lum.** `nav`/`action`/`status` —
   o'zgaradi, `verdict`/`brand` — qat'iy. Notanish domen (`foo.bar`)
   jimgina o'tib ketmasligi kerak: u qat'iy hisoblanadi va foydalanuvchi
   kutgan ikonka almashmay qoladi.

Nega Python: qolgan tekshiruvlar (`check_hardcoded.py`,
`check_verdict_codes.py`) Python'da va ularning `tools/pick-python.sh`
naqshini ishlatadi.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Chiqish quvurga yo'naltirilganda Windows uni `cp1252` deb yozadi va
# birinchi `✓` belgisida qulaydi — sabab va o'lchov `tools/_console.py` da.
import _console

_console.force_utf8()

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKS_DIR = ROOT / "apps/web/src/icons/packs"
PACKS_TS = ROOT / "apps/web/src/lib/theme/icon-packs.ts"
KEYS_MJS = ROOT / "tools/icon-keys.mjs"

#: `export const LUCIDE_ICONS: Record<...> = { ... };`
#:
#: ⚠️ Tip ichida `=>` bor (`(p: IconProps) => React.JSX.Element`), ya'ni
#: `Record<[^>]*>` kabi sodda naqsh `=>` ning `>` sida to'xtab qoladi.
#: Shuning uchun tip tashlanmaydi: `_ICONS` dan keyin birinchi `{` va
#: undan keyingi `\n};` olinadi.
MAP_START_RE = re.compile(r"export const ([A-Z0-9_]+)_ICONS\b[^\n]*= \{")
# ⚠️ `[a-zA-Z]` — kalitlar camelCase (`nav.expandDown`,
# `ranking.medalGold`). Faqat kichik harf qabul qilinsa 35 kalit
# jimgina tushib qoladi va soni 226 o'rniga 191 chiqadi.
KEY_RE = re.compile(r'^\s*"([a-z][a-zA-Z0-9.]*)":', re.M)
#: `export const ZONES: Record<IconZone, boolean> = { ... };`
ZONES_RE = re.compile(r"ZONES:\s*Record<IconZone,\s*boolean>\s*=\s*\{(.*?)\n\};", re.S)
ZONE_ENTRY_RE = re.compile(r"^\s*([a-z]+):\s*(true|false),", re.M)


def pack_keys(text: str) -> tuple[str, set[str]] | None:
    """`(export name, keys)` yoki `None`."""
    m = MAP_START_RE.search(text)
    if not m:
        return None
    body = text[m.end() :]
    end = body.find("\n};")
    if end < 0:
        return None
    return m.group(1), set(KEY_RE.findall(body[:end]))


def fail(msg: str) -> None:
    print(f"  ✕ {msg}")


def main() -> int:
    problems = 0

    if not PACKS_DIR.is_dir():
        print("Ikonka to'plamlari topilmadi — `tools/gen-icon-packs.mjs` ishlatilsin.")
        return 1

    # ── 1. Har bir to'plamning kalitlari ────────────────────────────────
    packs: dict[str, set[str]] = {}
    for path in sorted(PACKS_DIR.glob("*.tsx")):
        text = path.read_text(encoding="utf-8")
        parsed = pack_keys(text)
        if not parsed:
            fail(f"{path.name}: ikonka xaritasi topilmadi")
            problems += 1
            continue
        packs[path.stem] = parsed[1]

    if not packs:
        print("Hech qanday to'plam o'qilmadi.")
        return 1

    reference = max(packs, key=lambda p: len(packs[p]))
    base = packs[reference]
    for name, keys in packs.items():
        if keys != base:
            missing = sorted(base - keys)
            extra = sorted(keys - base)
            fail(
                f"{name}: kalitlar mos emas — yetishmaydi {missing or '—'}, "
                f"ortiqcha {extra or '—'}"
            )
            problems += 1

    # ── 2. Kalitlar `icon-keys.mjs` bilan bir xilmi ─────────────────────
    if KEYS_MJS.exists():
        src = KEYS_MJS.read_text(encoding="utf-8")
        # Format: `"nav.home": { d: "…", c: [...] }` — qiymat obyekt,
        # massiv emas. Ilgari bu yerda `\[` kutilardi va `declared`
        # bo'sh chiqib, tekshiruv doim qizarardi.
        declared = set(
            re.findall(r'^\s*"([a-z][a-zA-Z0-9.]*)":\s*\{', src, re.M)
        )
        # ⚠️ `brand.*` ataylab registrda YO'Q (D20 ①). Ular logotip:
        # Phosphor'da Python belgisi yo'q. Ular `lib/tech-icons.tsx` da
        # yashaydi va Simple Icons'dan keladi. Shuning uchun solishtirishdan
        # chiqariladi — aks holda tekshiruv doim qizarardi.
        declared = {k for k in declared if not k.startswith("brand.")}
        if declared != base:
            fail(
                "`tools/icon-keys.mjs` va generatsiya qilingan xaritalar "
                f"mos emas — farq: {sorted(declared ^ base)}"
            )
            problems += 1

    # ── 3. Qat'iy zonalar registrga tushmagan (D20 ①) ───────────────────
    zones: dict[str, bool] = {}
    if PACKS_TS.exists():
        zs = ZONES_RE.search(PACKS_TS.read_text(encoding="utf-8"))
        if zs:
            zones = {k: v == "true" for k, v in ZONE_ENTRY_RE.findall(zs.group(1))}
        else:
            fail("`icon-packs.ts` da ZONES topilmadi")
            problems += 1

    for key in sorted(base):
        zone = key.split(".")[0]
        if zone not in zones:
            fail(f"`{key}`: noma'lum domen `{zone}` — ZONES ga qo'shilsin")
            problems += 1
        elif not zones[zone]:
            fail(
                f"`{key}`: qat'iy zona (`{zone}`) registrda — D20 ① bo'yicha "
                "u to'plamga bo'ysunmasligi kerak"
            )
            problems += 1

    # ── 4. O'zgaruvchi zonalar bo'sh bo'lmasin ──────────────────────────
    #
    # ⚠️ Faqat **o'zgaruvchi** zonalar tekshiriladi. Qat'iy zonalarda
    # (`verdict`, `brand`) registrda kalit bo'lmasligi **to'g'ri** — ular
    # `Verdict` va brend komponentlari orqali Phosphor'dan chiziladi.
    # Ilgari bu shart hammasiga qo'yilgan edi va tekshiruv doim qizarardi.
    for zone, changes in zones.items():
        if not changes:
            continue
        n = sum(1 for k in base if k.split(".")[0] == zone)
        if n == 0:
            fail(
                f"`{zone}` o'zgaruvchi zona, lekin registrda bitta ham kaliti "
                "yo'q — ZONES dagi yozuv o'lik"
            )
            problems += 1

    if problems:
        print(f"\nJami: {problems} muammo — {len(packs)} to'plam, {len(base)} kalit.")
        return 1

    changing = sorted(z for z, c in zones.items() if c)
    fixed = sorted(z for z, c in zones.items() if not c)
    print(
        f"Tekshirildi: {len(packs)} to'plam × {len(base)} kalit · "
        f"o'zgaradi: {', '.join(changing)} · qat'iy: {', '.join(fixed)}\n"
        "Registr butun ✓"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
