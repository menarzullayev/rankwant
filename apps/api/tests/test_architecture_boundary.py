"""App chegarasi darvozasini tekshiradi (D7 · WP6).

`tools/check_architecture.py` HAQIQIY repo ustida ishga tushiriladi:
allowlist bugungi importlar bilan muvozanatda bo'lmasa (yangi import
paydo bo'lsa yoki allowlist'da o'lik yozuv qolsa) gate `exit 1` beradi
va test yiqiladi.

Ikkinchi test allowlist sarlavhasidagi `# jami: N` haqiqiy yozuv soniga
tengligini talab qiladi — raqam jimgina eskirib qolmasin.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "tools/check_architecture.py"
ALLOWLIST = ROOT / "tools/architecture-allowlist.txt"


def test_architecture_gate_is_green() -> None:
    """Gate bugungi repo'da `exit 0` bersin (allowlist bilan muvozanat)."""
    proc = subprocess.run(
        [sys.executable, str(GATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_allowlist_header_matches_entry_count() -> None:
    """`# jami: N` sarlavhasi haqiqiy qator soniga teng bo'lsin."""
    text = ALLOWLIST.read_text(encoding="utf-8")
    match = re.search(r"# jami:\s*(\d+)", text)
    assert match is not None, "allowlist sarlavhasida `# jami: N` yo'q"

    entries = [
        line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")
    ]
    declared = int(match.group(1))
    assert declared == len(entries), (
        f"sarlavha {declared} deydi, faylda {len(entries)} yozuv — yangilang"
    )
