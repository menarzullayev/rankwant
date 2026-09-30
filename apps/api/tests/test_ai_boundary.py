"""AI qatlami chegarasini RUNTIME tomondan tekshiradi (D6 · WP5).

Statik darvoza (`tools/check_ai_boundary.py`) kod MATNINI o'qiydi. Bu
test boshqa tomonni yopadi: `ai` paketini import qilganda `sys.modules`
ga hech qanday `*.models` moduli TUSHMASLIGI shart. Aks holda import
zanjiri DB sxemasiga yopishgan bo'lardi — statik tekshiruv buni har
doim ham ko'rmaydi (masalan import boshqa paket ichida bo'lsa).

Ikkinchi test statik darvozaning bugungi repo'da yashilligini tasdiqlaydi:
"vakuumli yashil" ni ham statik, ham runtime tomondan yopamiz.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "tools/check_ai_boundary.py"


def test_importing_ai_pulls_no_model_modules() -> None:
    """`ai` importi birorta Django model modulini tortmasin."""
    # Keshlangan import natijani yashirmasin: paketni tozalab, qaytadan
    # import qilamiz va `sys.modules` farqini o'lchaymiz.
    sys.modules.pop("ai", None)
    before = set(sys.modules)
    module = importlib.import_module("ai")
    after = set(sys.modules)

    pulled = sorted(name for name in after - before if name == "models" or name.endswith(".models"))
    assert module is not None
    assert not pulled, f"`ai` importi model modullarini tortdi: {pulled}"


def test_ai_boundary_gate_is_green() -> None:
    """Statik darvoza bugungi repo'da `exit 0` bersin."""
    proc = subprocess.run(
        [sys.executable, str(GATE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
