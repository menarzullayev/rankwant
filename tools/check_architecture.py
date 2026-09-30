#!/usr/bin/env python3
"""App chegarasi — bir app boshqa app'ning `models` modulini import qilmasin.

QOIDA (D7): `apps/api/` ichida A app'ining biror moduli B app'ining
`models` modulini import qilsa (`from B.models import ...`,
`import B.models`), bu **chegara buzilishi**. Sabab — app'lar orasidagi
YASHIRIN bog'liqlik: `check_security_boundary.py` faqat compose
chegarasini o'lchaydi, Python import chegarasini **EMAS**.

ISTISNOLAR (qoidada aniq belgilangan):
  * `migrations/` — sxema tarixi (generatsiya qilinadi), runtime emas;
  * `tests/` — testlar app'larni ataylab bog'laydi (fixture, ssenariy);
  * `core` — UMUMIY poydevor app (`User`, bazaviy abstraksiyalar). Unga
    tayanish ruxsat: `from core.models import ...` har app'da qonuniy.
    LEKIN `core` O'ZI boshqa app'ning `models`ini import qilsa —
    baribir buzilish (poydevor feature'ga tayanmasligi kerak).

GRANDFATHER + RATCHET (D7): bugungi buzilishlar
`tools/architecture-allowlist.txt` da sanab qo'yilgan; gate ular uchun
yashil (exit 0). Yangi buzilish → `exit 1`. Allowlist'da bor, lekin
repo'da **endi mavjud bo'lmagan** yozuv → `exit 1` — ro'yxat faqat
QISQARADI: importni tuzatgan odam yozuvini ham o'chirishi shart.

Allowlist qatori: `<nisbiy/yol.py>:<import qilingan modul>` — masalan
`arena/services.py:qvant.models`. Fayl boshida `# jami: N`.

CHIQISH KODLARI:
  0 — chegara allowlist bilan muvozanatda
  1 — yangi buzilish yoki o'lik allowlist yozuvi (ratchet)
  2 — o'qib bo'lmadi (qamrov yo'q, fayl buzuq, allowlist yo'q)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# Chiqish quvurga yo'naltirilganda Windows uni `cp1252` deb yozadi va
# birinchi `✓` belgisida qulaydi — sabab va o'lchov `tools/_console.py` da.
import _boundary_apps
import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = ROOT / "apps/api"
ALLOWLIST = ROOT / "tools/architecture-allowlist.txt"

#: Skanerdan chiqariladigan papka nomlari.
SKIP_PARTS = {"migrations", "tests", "__pycache__"}
#: Umumiy poydevor — unga tayanish ruxsat (istisno docstring'da).
FOUNDATION = {"core"}


def _violations(apps: set[str]) -> list[tuple[str, int, str]]:
    """`(nisbiy yo'l, satr, import qilingan modul)` — chegara buzilishlari."""
    out: list[tuple[str, int, str]] = []
    for path in sorted(APPS_DIR.rglob("*.py")):
        parts = path.relative_to(APPS_DIR).parts
        if any(part in SKIP_PARTS for part in parts):
            continue
        own = parts[0]
        if own not in apps:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:
            rel = path.relative_to(ROOT).as_posix()
            raise ValueError(f"{rel}: o'qib bo'lmadi — {exc}") from exc

        found: list[tuple[int, str]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.endswith(".models"):
                    found.append((node.lineno, node.module))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.endswith(".models"):
                        found.append((node.lineno, alias.name))

        rel = path.relative_to(APPS_DIR).as_posix()
        for lineno, module in found:
            target = module.split(".")[0]
            if target in apps and target != own and target not in FOUNDATION:
                out.append((rel, lineno, module))
    return out


def _allowlist() -> set[str]:
    """Allowlist yozuvlari to'plami (`#` izoh va bo'sh qatorlardan tashqari)."""
    if not ALLOWLIST.exists():
        raise ValueError(f"{ALLOWLIST.relative_to(ROOT).as_posix()} topilmadi")
    entries: set[str] = set()
    for raw in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            entries.add(line)
    return entries


def main() -> int:
    if not APPS_DIR.is_dir():
        print("  ✗ apps/api topilmadi — o'lchov yo'q")
        return 2
    apps = _boundary_apps.apps()
    if not apps:
        print("  ✗ app topilmadi — naqsh o'zgargan bo'lishi mumkin")
        return 2

    try:
        raw = _violations(apps)
        allowed = _allowlist()
    except ValueError as exc:
        print(f"  ✗ {exc}")
        return 2

    current = {f"{rel}:{module}" for rel, _lineno, module in raw}
    new = sorted(current - allowed)
    stale = sorted(allowed - current)

    print(
        f"Tekshirildi: {len(apps)} app · {len(current)} import · "
        f"allowlist {len(allowed)} yozuv"
    )

    failed = False
    if new:
        failed = True
        print(f"\n{len(new)} ta YANGI chegara buzilishi (allowlist'da yo'q):\n")
        for key in new:
            print(f"  ✗ {key}")
        print("\nYechim: importni umumiy modul orqali to'g'rilang; ATAYLAB bo'lsa —")
        print("  allowlist'ga qo'shib, ADR yozuvi bilan qayd eting.")
    if stale:
        failed = True
        print(f"\n{len(stale)} ta allowlist yozuvi ENDI MAVJUD EMAS (ratchet):\n")
        for key in stale:
            print(f"  ✗ {key}")
        print("\nRo'yxat faqat QISQARADI: tuzatilgan importni allowlist'dan o'chiring.")

    if failed:
        return 1
    print("App chegarasi toza ✓ (allowlist bilan muvozanatda)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
