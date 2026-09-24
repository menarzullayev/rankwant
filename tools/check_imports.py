"""Import butunligini tekshiradi: har bir `@/...` yo'li haqiqiy faylga
ishora qiladimi?

Nima uchun kerak: katta ko'chirishdan keyin yo'l xato bo'lsa, `tsc` ishlamasa
(npm paketlar o'rnatilmagan) buni hech kim ko'rmaydi — sayt shunchaki
oq ekran bo'lib qoladi. Bu skript statik tekshiradi.

Chiqish kodi: 0 — toza, 1 — sinigan import bor.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "apps/web/src"

IMPORT_RE = re.compile(r"""from\s+["'](@/[^"']+)["']""")
EXTS = [".ts", ".tsx", ".js", ".jsx", ".json", ".css", ".md"]


def resolves(spec: str) -> bool:
    base = SRC / spec[2:]  # strip "@/"
    # exact file
    if base.is_file():
        return True
    # with extension
    for ext in EXTS:
        if Path(str(base) + ext).is_file():
            return True
    # directory with index
    if base.is_dir():
        for ext in EXTS:
            if (base / f"index{ext}").is_file():
                return True
    # .server / .client suffixed (Next.js convention) e.g. api.server
    for ext in EXTS:
        if Path(str(base) + ".server" + ext).is_file():
            return True
        if Path(str(base) + ".client" + ext).is_file():
            return True
    return False


def main() -> int:
    bad: list[tuple[str, str]] = []
    total = 0

    for path in sorted(SRC.rglob("*")):
        if path.suffix not in {".ts", ".tsx"}:
            continue
        rel = path.relative_to(SRC).as_posix()
        text = path.read_text(encoding="utf-8")
        for m in IMPORT_RE.finditer(text):
            spec = m.group(1)
            total += 1
            if not resolves(spec):
                bad.append((rel, spec))

    print(f"Tekshirildi: {total} ta `@/` import")

    if not bad:
        print("\n✓ Import butunligi: hamma yo'l haqiqiy faylga ishora qiladi")
        return 0

    print(f"\n✗ Sinigan import: {len(bad)} ta")
    for rel, spec in bad:
        print(f"  {rel}")
        print(f"      {spec}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
