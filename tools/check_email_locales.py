#!/usr/bin/env python3
"""Xat matnlari HAMMA tilni qamrab olganini tekshiradi.

Nega kerak: `email_text.py` ni qo'lda tahrirlash oson, bitta tilni
tushirib qoldirish ham oson — va ilgari aynan shunday bo'lgan: 10 tildan
3 tasi bor edi, qolganlari jimgina o'zbekchaga tushardi (o'lchandi).
`strings()` endi jurnalga yozadi, lekin jurnal ishlab turgan tizimda
ko'rinadi; bu skript esa CI da to'xtatadi.

Ishlatish:
    python tools/check_email_locales.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "apps/api/core/email_text.py"

#: Kodda e'lon qilingan tillar — shu yerdan o'qiladi, qo'lda takrorlanmaydi.
LOCALES_VAR = "LOCALES"


def load_module_ast() -> ast.Module:
    return ast.parse(SOURCE.read_text(encoding="utf-8"))


def declared_locales(tree: ast.Module) -> list[str] | None:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == LOCALES_VAR:
                    if isinstance(node.value, ast.Tuple):
                        return [
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        ]
    return None


def dict_tables(tree: ast.Module) -> dict[str, ast.Dict]:
    """Modul darajasidagi «kalit → til → matn» lug'atlari."""
    tables: dict[str, ast.Dict] = {}
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if isinstance(node.value, ast.Dict):
                tables[node.target.id] = node.value
    return tables


def main() -> int:
    if not SOURCE.exists():
        sys.exit(f"email_text.py topilmadi: {SOURCE}")

    tree = load_module_ast()
    locales = declared_locales(tree)
    if not locales:
        sys.exit(f"`{LOCALES_VAR}` o'qilmadi — til ro'yxati e'lon qilinmagan")

    tables = dict_tables(tree)
    if not tables:
        sys.exit("hech qanday lug'at topilmadi — tekshiruv ko'r bo'lib qolgan")

    problems: list[str] = []
    checked = 0

    for name, table in sorted(tables.items()):
        for key_node, value_node in zip(table.keys, table.values, strict=True):
            if not isinstance(key_node, ast.Constant) or not isinstance(value_node, ast.Dict):
                continue
            key = key_node.value
            # Qaysi tillar shu satrda bor.
            present = set()
            for lang_node in value_node.keys:
                if isinstance(lang_node, ast.Constant) and isinstance(lang_node.value, str):
                    present.add(lang_node.value)
            checked += 1

            missing = [code for code in locales if code not in present]
            unknown = sorted(present - set(locales))
            blank = []
            for lang_node, text_node in zip(value_node.keys, value_node.values, strict=True):
                if not isinstance(lang_node, ast.Constant) or not isinstance(text_node, ast.Constant):
                    continue
                if isinstance(text_node.value, str) and not text_node.value.strip():
                    blank.append(lang_node.value)

            where = f"{name}.{key}"
            if missing:
                problems.append(f"{where}: yetishmaydi — {', '.join(missing)}")
            if unknown:
                problems.append(f"{where}: ro'yxatda yo'q til — {', '.join(unknown)}")
            if blank:
                problems.append(f"{where}: bo'sh matn — {', '.join(sorted(blank))}")

    if problems:
        print(f"Xat matnlari to'liq emas ({len(problems)} ta):", file=sys.stderr)
        for row in problems[:20]:
            print(f"  {row}", file=sys.stderr)
        if len(problems) > 20:
            print(f"  … va yana {len(problems) - 20} ta", file=sys.stderr)
        return 1

    print(f"Xat matnlari: {checked} satr × {len(locales)} til — to'liq ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
