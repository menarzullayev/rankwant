"""`SECRET_KEY` fail-fast (D5) — sukut sir bilan prod ko'tarilmasin.

`config.settings` `DJANGO_SECRET_KEY` bo'sh yoki yo'q bo'lsa
`ImproperlyConfigured` ko'tarishi SHART: ma'lum sukut bilan ko'tarilgan
production har bir sessiya/CSRF/PAT tokenni ommaviy kalit bilan
imzolaydi va uni istalgan kishi qalbakilashtira oladi.

Tekshiruv SUBPROCESS'da: xato sozlamalar import VAQTIDA chiqadi, ya'ni
uni joriy pytest jarayonida qayta yuklab bo'lmaydi (Django `settings`
obyektini keshlaydi). Subprocess toza interpretator — aynan qaysi
qiymat bilan sozlamalar yuklanishini o'lchaydi.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

#: `config` paketi shu katalogdan import qilinadi (pytest rootdir).
API_DIR = Path(__file__).resolve().parent.parent

#: Faqat sozlamalar modulini o'qish — `django.setup()` ATAYLAB chaqirilmaydi
#: (app `ready()` ilgaklari keraksiz; bizga faqat import vaqtidagi guard kerak).
_IMPORT_SETTINGS = "import importlib; importlib.import_module('config.settings')"


def _load_settings(secret_key: str | None) -> subprocess.CompletedProcess[str]:
    """`config.settings` ni subprocess'da yuklab, natijani qaytaradi.

    `secret_key=None` — o'zgaruvchi muhitdan OLIB TASHLANADI (yo'q holat);
    `""` — bo'sh qiymat; aks holda shu qiymat beriladi.
    """
    env = {**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings"}
    if secret_key is None:
        env.pop("DJANGO_SECRET_KEY", None)
    else:
        env["DJANGO_SECRET_KEY"] = secret_key
    return subprocess.run(
        [sys.executable, "-c", _IMPORT_SETTINGS],
        cwd=API_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_missing_secret_key_raises_improperly_configured() -> None:
    """`DJANGO_SECRET_KEY` umuman yo'q → `ImproperlyConfigured`."""
    result = _load_settings(None)
    assert result.returncode != 0, "sirsiz sozlamalar yuklanmasligi kerak edi"
    assert "ImproperlyConfigured" in result.stderr
    assert "DJANGO_SECRET_KEY" in result.stderr


def test_blank_secret_key_raises_improperly_configured() -> None:
    """Bo'sh qiymat ham yetarli emas — jimgina davom etmasin."""
    result = _load_settings("")
    assert result.returncode != 0, "bo'sh SECRET_KEY bilan yuklanmasligi kerak edi"
    assert "ImproperlyConfigured" in result.stderr
    assert "DJANGO_SECRET_KEY" in result.stderr


def test_present_secret_key_loads_cleanly() -> None:
    """Qiymat berilganda sozlamalar xatosiz yuklanadi (guard ortiqcha emas)."""
    result = _load_settings("test-only-not-for-production")
    assert result.returncode == 0, result.stderr
    assert "ImproperlyConfigured" not in result.stderr
