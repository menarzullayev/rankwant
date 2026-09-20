#!/usr/bin/env python3
"""Judge latency raqamini run sahifasiga chiqaradi.

Nega kerak: `tests/latency/check_judge_latency.py` o'z natijasini faqat
stdout'ga yozadi, Nightly esa uni log ichiga ko'madi. Log **hech kim
o'qimaydi**, ya'ni `docs/09-development-plan/README.md` § "Launch gate" dagi

    - [ ] Judge latency o'lchangan: p50 < 5s, p95 < 15s

bandi job yashil bo'lganda ham **o'zgarmasdi**: o'lchov bor, qayd yo'q.
Bu asbob o'sha bo'shliqni yopadi — raqamni Actions'ning **run sahifasiga**
(`$GITHUB_STEP_SUMMARY`) yozadi, u yerda log ochmasdan ko'rinadi.

Manba — harness chiqargan bitta belgili satr:

    LATENCY_JSON: {"api": ..., "p50_ms": 173, "p95_ms": 1683, ...}

⚠️ Bu asbob jim buzilsa raqam yetib bormaydi va gate yana «o'lchanmagan»
bo'lib qoladi. Shuning uchun belgi topilmasa **exit 2** — «o'qib
bo'lmadi» hech qachon «yaxshi» emas. (Loyihadagi umumiy qoida: 0 = toza,
1 = muammo, 2 = o'lchab bo'lmadi.)

Ishlatish:

    python3 tools/latency_summary.py /tmp/latency.log
    GITHUB_STEP_SUMMARY=/tmp/summary.md python3 tools/latency_summary.py /tmp/latency.log
    python3 tools/latency_summary.py --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import _console

_console.force_utf8()

MARKER = "LATENCY_JSON: "


def parse(log_text: str) -> dict | None:
    """Oxirgi `LATENCY_JSON:` satrini o'qiydi.

    Oxirgisi olinadi: harness bir yurishda bir marta chiqaradi, lekin log
    bir necha urinishni birlashtirishi mumkin — qayd etiladigan raqam
    **eng oxirgi o'lchov** bo'lishi kerak.
    """
    found: dict | None = None
    for line in log_text.splitlines():
        index = line.find(MARKER)
        if index < 0:
            continue
        try:
            payload = json.loads(line[index + len(MARKER):])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            found = payload
    return found


def render(payload: dict) -> str:
    """O'lchovni markdown blokiga aylantiradi."""
    ok = bool(payload.get("ok"))
    mark = "✅" if ok else "❌"
    lines = [
        f"## {mark} Judge latency — launch gate",
        "",
        f"- **p50 = {payload.get('p50_ms')} ms** (byudjet {payload.get('budget_p50_ms')} ms)",
        f"- **p95 = {payload.get('p95_ms')} ms** (byudjet {payload.get('budget_p95_ms')} ms)",
        f"- min {payload.get('min_ms')} ms · max {payload.get('max_ms')} ms "
        f"· o'rtacha {payload.get('mean_ms')} ms",
        "",
        f"Namuna: **{payload.get('samples')}** (+{payload.get('warmup')} qizdirish) · "
        f"`{payload.get('language')}` · masala `{payload.get('problem')}`",
        f"Muhit: `{payload.get('api')}` · {payload.get('cores')} yadro · "
        f"load1 {payload.get('load1')}",
        "",
    ]
    failures = payload.get("failures") or []
    if failures:
        lines.append("**Sabablar:**")
        lines += [f"- {item}" for item in failures]
        lines.append("")
    lines.append(
        "> Bu raqam **regressiya bazasi** — GitHub runner, ishlab chiqarish "
        "mashinasi emas. Gate raqami uchun o'sha harness'ni production'ga "
        "qarating "
        "(`API=https://rankwant.uz/api/v1 LATENCY_SAMPLES=20`)."
    )
    return "\n".join(lines)


def write_summary(text: str) -> str:
    """`$GITHUB_STEP_SUMMARY` bo'lsa o'sha yerga, bo'lmasa stdout'ga yozadi.

    Qaytaradi: qayerga yozilgani (log uchun).
    """
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if not target:
        print(text)
        return "stdout"
    with open(target, "a", encoding="utf-8") as handle:
        handle.write(text + "\n")
    return target


def self_test() -> int:
    """Belgini topish va yo'qligini ajratish — tarmoqsiz sinov."""
    good = parse('old noise\nLATENCY_JSON: {"p50_ms": 1}\nLATENCY_JSON: {"p50_ms": 2}\n')
    if good != {"p50_ms": 2}:
        print(f"✗ oxirgi satr olinmadi: {good}", file=sys.stderr)
        return 1
    if parse("nothing here\n") is not None:
        print("✗ belgisiz log o'qildi", file=sys.stderr)
        return 1
    if parse("LATENCY_JSON: {buzuq\n") is not None:
        print("✗ buzuq JSON o'qildi", file=sys.stderr)
        return 1
    print("✓ latency_summary: o'zini sinovdan o'tkazdi")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("log", nargs="?", help="harness chiqishi yozilgan fayl")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.log:
        print("✗ log fayli ko'rsatilmagan", file=sys.stderr)
        return 2
    path = Path(args.log)
    if not path.exists():
        print(f"✗ log topilmadi: {path}", file=sys.stderr)
        return 2

    payload = parse(path.read_text(encoding="utf-8", errors="replace"))
    if payload is None:
        print(
            f"✗ `{MARKER}` satri topilmadi: {path} — o'lchov o'qilmadi "
            "(harness yiqilgan bo'lishi mumkin)",
            file=sys.stderr,
        )
        return 2

    where = write_summary(render(payload))
    print(
        f"✓ latency raqami yozildi ({where}): "
        f"p50 {payload.get('p50_ms')} ms · p95 {payload.get('p95_ms')} ms"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
