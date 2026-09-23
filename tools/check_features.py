"""Feature qatlami chegarasini tekshiradi.

Qoida (ChatGPT ro'yxatining 4- va 25-bandi, `docs/08-technical-spec/ui-architecture.md`):

  1. **Feature ichidagi narsa tashqariga faqat `index.ts` orqali chiqadi.**
     Boshqa feature yoki sahifa `features/x/components/Button` ga to'g'ridan-to'g'ri
     murojaat qilmasligi kerak — ichki tuzilma o'zgarsa hamma chaqiruvchi sinadi.

  2. **Feature bir xil darajadagi boshqa feature'ni import qilmasligi kerak.**
     `features/problems` → `features/contests` — bu coupling. Umumiy narsa
     `components/ui`, `lib/` yoki `context/` ga ko'chishi kerak.

  3. **Global qatlam (`components/`, `layout/`, `lib/`...) feature'ni bilmaydi.**
     Bu ChatGPT aytgan «pastki layer yuqoridagini bilmasin» qoidasi.

⚠️ Bu skript faqat **import yo'lini** o'qiydi — ya'ni statik chegara. Runtime
bog'liqlikni ko'rmaydi; u uchun test kerak (kelajakdagi ish).

Chiqish kodi: 0 — toza, 1 — chegara buzilgan.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "apps/web/src"
FEATURES = SRC / "features"

# Global qatlam — feature'ni bilmasligi kerak.
GLOBAL_DIRS = ["components", "layout", "i18n", "icons", "content", "lib", "context"]

# ── 2-qoida: ruxsat etilgan feature→feature bog'liqlik ──────────────────
# Har bir yozuv SABAB bilan: tip almashinuvi (kod emas) yoki mahsulot
# jihatidan ajralmas juftlik.
ALLOWED_CROSS = {
    ("profile", "account"): "`PrivacyField` tipi — account'dan (tip oqimi, kod emas)",
    ("account", "problems"): "`Problem` tipi — marafon vazifalari (tip oqimi, kod emas)",
    ("contests", "profile"): "`UserTitle` tipi — endi `lib/identity` dan qayta eksport",
    ("problems", "profile"): "`UserTitle` tipi — endi `lib/identity` dan qayta eksport",
    ("hackathons", "profile"): "`UserTitle` tipi — endi `lib/identity` dan qayta eksport",
    ("submissions", "hackathons"): "`HackPanel` — urinish sahifasiga singib ketgan (mahsulot juftligi)",
    ("account", "auth"): "`Turnstile` — xavfsizlik vidjeti, forma bilan birga ishlaydi",
}

# ── 3-qoida: global qatlamdan ruxsat etilgan istisnolar ────────────────
# Fayl bo'yicha (aniq yo'l) — «global qatlam» nomidan emas.
ALLOWED_GLOBAL_TO_FEATURE = {
    "lib/api/index.ts": "ataylab qayta eksport — `@/lib/api` barqaror yuzasi (ADR-0009)",
    "lib/api/endpoints.ts": "ataylab qayta eksport — `@/lib/api` barqaror yuzasi (ADR-0009)",
    "layout/HeaderActions.tsx": "qobiq vidjeti — feature o'z widgetini beradi (UpdatesBell)",
}

IMPORT_RE = re.compile(r"""from\s+["'](@/[^"']+|\.\.?/[^"']+)["']""")

# Barrel ichidagi qayta eksport: `export { A, B } from "./components/X";`
RE_EXPORT_RE = re.compile(
    r"""export\s+(?:type\s+)?\{([^}]*)\}\s+from\s+["'](\./[^"']+)["']"""
)

# Server-only API belgisi — faqat shu zanjir mijoz to'plamini buzadi.
SERVER_API_RE = re.compile(
    r"""next/headers|@/i18n/server|lib/api\.server|["']server-only["']"""
)


def feature_of(rel: str) -> str | None:
    parts = rel.split("/")
    return parts[1] if len(parts) > 1 and parts[0] == "features" else None


def main() -> int:
    problems: list[tuple[str, str, str]] = []
    allowed_hits = 0

    for path in sorted(SRC.rglob("*")):
        if path.suffix not in {".ts", ".tsx"}:
            continue
        rel = path.relative_to(SRC).as_posix()
        text = path.read_text(encoding="utf-8")
        src_feature = feature_of(rel)

        for m in IMPORT_RE.finditer(text):
            spec = m.group(1)

            if spec.startswith("@/features/"):
                parts = spec.split("/")
                dst = parts[2] if len(parts) > 2 else None

                # (1) feature ichidan tashqariga: ichki yo'l bilan chiqmasin
                if src_feature and dst and dst != src_feature:
                    if (src_feature, dst) in ALLOWED_CROSS:
                        allowed_hits += 1
                    else:
                        problems.append((
                            rel, spec,
                            f"feature→feature: {src_feature} → {dst} "
                            f"(ruxsat ro'yxatida yo'q)"
                        ))

                # (2) global qatlam feature'ni bilmasin
                if not src_feature and rel.split("/")[0] in GLOBAL_DIRS:
                    if rel in ALLOWED_GLOBAL_TO_FEATURE:
                        allowed_hits += 1
                    else:
                        problems.append((
                            rel, spec,
                            f"global qatlam ({rel.split('/')[0]}/) feature'ni import qilmoqda"
                        ))

        # (3) feature ichki yo'liga to'g'ridan-to'g'ri murojaat (index.ts dan tashqari)
        if not src_feature and rel not in ALLOWED_GLOBAL_TO_FEATURE:
            for m in IMPORT_RE.finditer(text):
                spec = m.group(1)
                if spec.startswith("@/features/"):
                    tail = spec.split("/")[3] if len(spec.split("/")) > 3 else ""
                    if tail in {"components", "api"}:
                        problems.append((
                            rel, spec,
                            "feature ichki yo'liga to'g'ridan-to'g'ri murojaat "
                            "(index.ts ishlatilsin)"
                        ))

    # ── 4-qoida: bir barrel mijoz va serverni aralashtirmasin ──────────
    # Next.js build buni faqat HAQIQIY import zanjirida ushlaydi. Ya'ni
    # barrel'da server komponenti bo'lsa-yu, uni hech kim import qilmasa —
    # build o'tib ketadi, keyin kimdir import qilsa yiqiladi. Shu sabab
    # statik tekshiramiz.
    #
    # ⚠️ Belgi ANIQ bo'lishi kerak: `"use client"` yo'qligi o'zi hali
    # server-only degani EMAS — sof taqdimot komponenti ham belgisiz
    # bo'ladi va u ikkala tomonda ham xavfsiz. Xavf faqat `next/headers`
    # kabi server API'sidan keladi. Shuning uchun aynan shuni qidiramiz.
    for feat in sorted(FEATURES.iterdir()):
        if not feat.is_dir():
            continue
        bpath = feat / "index.ts"
        if not bpath.is_file():
            continue
        rel = bpath.relative_to(SRC).as_posix()
        text = bpath.read_text(encoding="utf-8")
        client, server_only = [], []
        for m in RE_EXPORT_RE.finditer(text):
            target = m.group(2)
            cand = (feat / target).with_suffix("")
            for ext in (".tsx", ".ts"):
                p2 = Path(str(cand) + ext)
                if p2.is_file():
                    src = p2.read_text(encoding="utf-8")
                    is_client = src.startswith('"use client"')
                    uses_server_api = SERVER_API_RE.search(src) is not None
                    if is_client:
                        client.append(m.group(1))
                    elif uses_server_api:
                        server_only.append(m.group(1))
                    break
        if client and server_only:
            problems.append((
                rel,
                f"client={len(client)} server-only={len(server_only)}: "
                f"{', '.join(server_only[:3])}",
                "mijoz va server-only eksporti bitta barrel'da aralash "
                "(Next.js build'da `next/headers` mijozga tortiladi) — "
                "serverni `server.ts` ga ajrating"
            ))

    print(f"Skanerlandi: {len(list(SRC.rglob('*.tsx')))} tsx + "
          f"{len(list(SRC.rglob('*.ts')))} ts")
    print(f"Feature'lar: {len([d for d in FEATURES.iterdir() if d.is_dir()])} ta · "
          f"ruxsat etilgan kesishma: {len(ALLOWED_CROSS)} ta · "
          f"global istisno: {len(ALLOWED_GLOBAL_TO_FEATURE)} ta")

    if not problems:
        print(f"\n✓ Feature chegarasi toza — qatlamlar bir-birini bilmaydi "
              f"({allowed_hits} ta ruxsat etilgan bog'lanish ishlatilgan)")
        return 0

    print(f"\n✗ Chegara buzilishi: {len(problems)} ta")
    seen: set[tuple[str, str]] = set()
    for rel, spec, why in problems:
        key = (rel, spec)
        if key in seen:
            continue
        seen.add(key)
        print(f"  {rel}")
        print(f"      {spec}")
        print(f"      → {why}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
