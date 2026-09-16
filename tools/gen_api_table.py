#!/usr/bin/env python3
"""Generate a domain-grouped endpoint table from the OpenAPI schema.

Source: `.handoff/schema.yaml` (exported from the running API, see
`tools/fetch_schema.sh` or the handoff notes).

Usage:
    python tools/gen_api_table.py [schema.yaml] [out.md]
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = ROOT / ".handoff" / "schema.yaml"
DEFAULT_OUT = ROOT / ".handoff" / "API-ENDPOINTS.md"

METHODS = ["get", "post", "put", "patch", "delete", "head", "options"]
WS = re.compile(r"\s+")

# DRF action -> short Uzbek gloss. Custom actions keep their own name.
ACTION_GLOSS = {
    "list": "ro'yxat",
    "retrieve": "bittasi",
    "create": "yaratish",
    "update": "yangilash",
    "partial_update": "qisman yangilash",
    "destroy": "o'chirish",
    "me": "o'z ma'lumoti",
    "read": "o'qish",
}


def first_line(text: str, limit: int = 150) -> str:
    """Collapse a description block into one readable line."""
    if not text:
        return ""
    for para in text.split("\n\n"):
        para = WS.sub(" ", para).strip()
        if para:
            break
    else:
        para = ""
    para = para.replace("|", "\\|")
    if len(para) > limit:
        para = para[: limit - 1].rstrip() + "…"
    return para


def action_of(operation_id: str) -> str:
    """DRF builds operationIds as `<basename>_<sub-path>_<action>`."""
    if not operation_id:
        return ""
    low = operation_id.lower()
    for action in ("partial_update", "list", "retrieve", "create", "update", "destroy", "me", "read"):
        if low.endswith("_" + action):
            head = operation_id[: -(len(action) + 1)]
            break
        if low == action:
            head = ""
            break
    else:
        action = operation_id.rsplit("_", 1)[-1]
        head = operation_id[: -(len(action) + 1)]

    tokens = head.split("_") if head else []
    sub = "/".join(tokens[1:]) if len(tokens) > 1 else ""
    gloss = ACTION_GLOSS.get(action, action)
    return f"{sub} · {gloss}" if sub else gloss


def domain_of(path: str) -> str:
    parts = [p for p in path.split("/") if p]
    # /api/v1/<domain>/... — anything else (e.g. /health/) keeps its own name.
    return parts[2] if len(parts) > 2 and parts[0] == "api" else (parts[0] if parts else "root")


def main() -> int:
    schema_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SCHEMA
    out_path = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT

    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    paths: dict = schema.get("paths", {})

    rows: list[tuple[str, str, str, str, str, str]] = []
    for path, ops in paths.items():
        for method in METHODS:
            op = ops.get(method) if isinstance(ops, dict) else None
            if not isinstance(op, dict):
                continue
            # `summary` birinchi: u amalga tegishli qisqa matn, `description`
            # esa ko'pincha butun ViewSet'ga tegishli (docstring).
            desc = first_line(str(op.get("summary") or op.get("description") or ""))
            op_id = str(op.get("operationId", ""))
            rows.append((domain_of(path), method.upper(), path, op_id, action_of(op_id), desc))

    by_domain: dict[str, list] = collections.defaultdict(list)
    for row in rows:
        by_domain[row[0]].append(row)

    method_count = collections.Counter(r[1] for r in rows)
    no_desc = [r for r in rows if not r[5]]

    # A description reused by 3+ operations is the ViewSet docstring, not a
    # per-action explanation — showing it 150 times adds nothing.
    desc_count = collections.Counter(r[5] for r in rows if r[5])
    generic = {text for text, n in desc_count.items() if n >= 3}

    lines: list[str] = []
    add = lines.append
    add("# RankWant API — endpointlar jadvali")
    add("")
    add(f"Manba: `{schema_path.as_posix()}` · OpenAPI {schema.get('openapi', '?')}")
    add("")
    add("## Umumiy")
    add("")
    add("| Ko'rsatkich | Soni |")
    add("|---|---|")
    add(f"| Yo'llar (path) | **{len(paths)}** |")
    add(f"| Operatsiyalar | **{len(rows)}** |")
    add(f"| Domenlar | **{len(by_domain)}** |")
    add(f"| Tavsifsiz operatsiya | **{len(no_desc)}** |")
    add(f"| Umumiy (ViewSet) tavsif | **{sum(desc_count[t] for t in generic)}** |")
    add("")
    add("| Method | Soni |")
    add("|---|---|")
    for method, count in method_count.most_common():
        add(f"| {method} | {count} |")
    add("")

    add("## Domenlar (kattalik bo'yicha)")
    add("")
    add("| Domen | Operatsiya | Yo'l |")
    add("|---|---|---|")
    for dom, dom_rows in sorted(by_domain.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        add(f"| `{dom}` | {len(dom_rows)} | {len({r[2] for r in dom_rows})} |")
    add("")

    add("## Endpointlar")
    add("")
    for dom, dom_rows in sorted(by_domain.items()):
        dom_rows.sort(key=lambda r: (r[2], METHODS.index(r[1].lower())))
        add(f"### `{dom}` — {len(dom_rows)} operatsiya")
        add("")
        add("| Method | Yo'l | Amal | Vazifasi |")
        add("|---|---|---|---|")
        for _dom, method, path, _op_id, action, desc in dom_rows:
            shown = "" if desc in generic else desc
            add(f"| {method} | `{path}` | {action or '—'} | {shown or '—'} |")
        add("")

    if no_desc:
        add("## Tavsifsiz operatsiyalar")
        add("")
        add("Hujjat yozilishi kerak — sxemada `description` ham, `summary` ham yo'q.")
        add("")
        add("| Method | Yo'l |")
        add("|---|---|")
        for _dom, method, path, _op_id, _action, _desc in sorted(no_desc, key=lambda r: r[2]):
            add(f"| {method} | `{path}` |")
        add("")

    if generic:
        add("## Umumiy (ViewSet) tavsiflar")
        add("")
        add("Bir matn 3+ operatsiyada takrorlangan — bu amalga emas, butun")
        add("ViewSet'ga tegishli. Jadvalda «—» ko'rsatilgan.")
        add("")
        add("| Takror | Matn |")
        add("|---|---|")
        for text in sorted(generic, key=lambda t: -desc_count[t]):
            add(f"| {desc_count[text]} | {text} |")
        add("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Yozildi: {out_path}")
    print(f"Yo'llar: {len(paths)} · operatsiyalar: {len(rows)} · domenlar: {len(by_domain)}")
    print("Methodlar: " + ", ".join(f"{m} {c}" for m, c in method_count.most_common()))
    print(f"Tavsifsiz: {len(no_desc)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
