"""Django app discovery for the boundary gates (D6 · D7).

Both `check_ai_boundary.py` and `check_architecture.py` must agree on which
names under `apps/api/` are Django apps. Kept in ONE place on purpose: if the
two gates discovered apps differently, a boundary could silently open in the
gap between them.

`apps/api/` da app — `__init__.py` bo'lgan papka, `NON_APPS` dan tashqari.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = ROOT / "apps/api"

#: `apps/api/` da app bo'lmagan papkalar (sozlama, sxema, testlar).
NON_APPS = {"config", "openapi", "tests"}


def apps() -> set[str]:
    """`apps/api/` dagi app nomlari (`__init__.py` bo'lgan papkalar)."""
    return {
        path.name
        for path in APPS_DIR.iterdir()
        if path.is_dir()
        and (path / "__init__.py").exists()
        and path.name not in NON_APPS
    }
