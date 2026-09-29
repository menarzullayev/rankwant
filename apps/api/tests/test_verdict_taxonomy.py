"""Verdikt taxonomy — o'lik kodlar, M10 migratsiya, regressiya testlari."""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from judging.models import Attempt
from judging.verdicts import Verdict

ROOT = Path(__file__).resolve().parent.parent.parent.parent

# `tools/` paket emas (import kerak bo'lsa `check_verdict_codes` import
# qilinishi kerak) — lokatorni qo'lda qo'shamiz. Yo'lni modul sifatida
# o'zgartirmaymiz: `tools` nomi tashqi muhitda allaqachon olinishi mumkin
# (tests/ ildizdan import qiladi) — shu sababli funksiya ichida.
TOOLS_DIR = ROOT / "tools"


def _load_check_verdict_codes():
    sys.path.insert(0, str(TOOLS_DIR))
    try:
        return importlib.import_module("check_verdict_codes")
    finally:
        # Qo'shilgan yo'lni olib tashlaymiz — boshqa testlarga ta'sir qilmasin.
        if str(TOOLS_DIR) in sys.path:
            sys.path.remove(str(TOOLS_DIR))


class TestDeadCodesDocumented:
    """T-WP2.1: 4 ta o'lik kod verdicts.py'da hujjatlangan."""

    def test_re_has_legacy_comment(self) -> None:
        text = (ROOT / "apps/api/judging/verdicts.py").read_text(encoding="utf-8")
        assert 'RE = "RE"' in text
        # LEGACY yoki O'LIK kalit so'zi RE izohida uchraydi
        re_block = text.split('RE = "RE"')[0].split("\n")[-5:]
        block = "\n".join(re_block)
        assert "O'LIK" in block or "LEGACY" in block

    def test_rate_limited_has_dead_comment(self) -> None:
        text = (ROOT / "apps/api/judging/verdicts.py").read_text(encoding="utf-8")
        assert 'RATE_LIMITED = "RATE_LIMITED"' in text
        block = text.split('RATE_LIMITED = "RATE_LIMITED"')[0].split("\n")[-5:]
        assert "O'LIK" in "\n".join(block)

    def test_denial_of_judgement_has_dead_comment(self) -> None:
        text = (ROOT / "apps/api/judging/verdicts.py").read_text(encoding="utf-8")
        assert 'DENIAL_OF_JUDGEMENT = "DENIAL_OF_JUDGEMENT"' in text
        block = text.split('DENIAL_OF_JUDGEMENT = "DENIAL_OF_JUDGEMENT"')[0].split("\n")[-5:]
        assert "O'LIK" in "\n".join(block)

    def test_testing_aborted_has_dead_comment(self) -> None:
        text = (ROOT / "apps/api/judging/verdicts.py").read_text(encoding="utf-8")
        assert 'TESTING_ABORTED = "TESTING_ABORTED"' in text
        block = text.split('TESTING_ABORTED = "TESTING_ABORTED"')[0].split("\n")[-5:]
        assert "O'LIK" in "\n".join(block)

    def test_all_four_dead_codes_exist(self) -> None:
        """Barcha 4 o'lik kod enum'da mavjud va o'chirilmagan."""
        assert hasattr(Verdict, "RE")
        assert hasattr(Verdict, "RATE_LIMITED")
        assert hasattr(Verdict, "DENIAL_OF_JUDGEMENT")
        assert hasattr(Verdict, "TESTING_ABORTED")


class TestReSignalReExitSplit:
    """T-WP2.3: RE_SIGNAL/RE_EXIT ajratish regressiya testlari."""

    def test_re_signal_exists(self) -> None:
        assert hasattr(Verdict, "RE_SIGNAL")
        assert Verdict.RE_SIGNAL.value == "RE_SIGNAL"

    def test_re_exit_exists(self) -> None:
        assert hasattr(Verdict, "RE_EXIT")
        assert Verdict.RE_EXIT.value == "RE_EXIT"

    def test_re_signal_and_re_exit_are_distinct(self) -> None:
        assert Verdict.RE_SIGNAL.value != Verdict.RE_EXIT.value

    def test_re_legacy_still_exists(self) -> None:
        """RE o'chirilmagan — tarixiy ma'lumotlar yaxlitligi."""
        assert hasattr(Verdict, "RE")
        assert Verdict.RE.value == "RE"


class TestM10Migration:
    """T-WP2.2: M10 migratsiya testlari (judge_meta heuristikasi)."""

    @pytest.mark.django_db
    def test_migration_relabels_by_judge_meta(self, user, problem, language) -> None:
        """judge_meta dagi signal/exit_code kaliti bo'yicha ajratiladi."""
        a1 = Attempt.objects.create(
            user=user,
            problem=problem,
            language=language,
            source_code="x",
            verdict=Verdict.RE,
            judge_meta={"signal": 11},
        )
        a2 = Attempt.objects.create(
            user=user,
            problem=problem,
            language=language,
            source_code="y",
            verdict=Verdict.RE,
            judge_meta={"exit_code": 1},
        )
        a3 = Attempt.objects.create(
            user=user,
            problem=problem,
            language=language,
            source_code="z",
            verdict=Verdict.RE,
            judge_meta={},
        )

        # Heuristic test: signal bor → RE_SIGNAL
        from judging.migrations._m10_heuristic import judge_meta_choice

        assert judge_meta_choice({"signal": 11}) == "RE_SIGNAL"
        # Heuristic test: exit_code bor → RE_EXIT
        assert judge_meta_choice({"exit_code": 1}) == "RE_EXIT"
        # Heuristic test: hech narsa yo'q → RE_SIGNAL (default)
        assert judge_meta_choice({}) == "RE_SIGNAL"
        assert judge_meta_choice(None) == "RE_SIGNAL"

        a1.refresh_from_db()
        a2.refresh_from_db()
        a3.refresh_from_db()
        # Qatorlar hali o'zgartirilmagan (migratsiya ishga tushmagan)
        assert a1.verdict == Verdict.RE
        assert a2.verdict == Verdict.RE
        assert a3.verdict == Verdict.RE

    @pytest.mark.django_db
    def test_migration_runs_without_error(self) -> None:
        """Migratsiya funksiyasi yiqilmasdan ishlaydi."""
        mod = importlib.import_module("judging.migrations.0008_relabel_re_legacy")
        _relabel_re_legacy = mod._relabel_re_legacy

        # apps va schema_editor mock'ini yaratish
        apps = MagicMock()
        AttemptMock = MagicMock()
        apps.get_model.return_value = AttemptMock
        AttemptMock.objects.filter.return_value.values_list.return_value = []

        # Yiqilishmasligini tekshirish
        _relabel_re_legacy(apps, None)  # type: ignore[arg-type]

        AttemptMock.objects.filter.assert_called_once_with(verdict="RE")

    @pytest.mark.django_db
    def test_migration_batch_processing(self, user, problem, language) -> None:
        """Katta hajmdagi qatorlar batch'lar bilan qayta ishlanadi.

        O'lchangan cheklov (QA 2026-09-29): judge signal/exit kodini
        natijaga YOZMAYDI, shuning uchun judge_meta'da kalitlar yo'q va
        hammasi default RE_SIGNAL ga o'tadi — migratsiya xatosiz ishlaydi.
        """
        mod = importlib.import_module("judging.migrations.0008_relabel_re_legacy")
        _relabel_re_legacy = mod._relabel_re_legacy

        # 5 ta RE qator yaratish
        attempts = []
        for i in range(5):
            a = Attempt.objects.create(
                user=user,
                problem=problem,
                language=language,
                source_code=f"x{i}",
                verdict=Verdict.RE,
            )
            attempts.append(a)

        # Mock apps.get_model to return real Attempt model
        apps = MagicMock()
        apps.get_model.return_value = Attempt

        _relabel_re_legacy(apps, None)  # type: ignore[arg-type]

        # Hammasi RE_SIGNAL ga o'tgan (judge_meta'da kalit yo'q, default)
        for a in attempts:
            a.refresh_from_db()
            assert a.verdict == "RE_SIGNAL"


class TestCheckVerdictCodes:
    """T-WP2.3: check_verdict_codes.py yashil."""

    def test_check_verdict_codes_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/check_verdict_codes.py")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"check_verdict_codes.py failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_i18n_parity_all_locales(self) -> None:
        """Barcha 10 til'da barcha verdikt kodlari uchun yorliq bor."""
        mod = _load_check_verdict_codes()

        codes = mod.api_codes()
        for code in codes:
            have = mod.locale_labels(code)
            missing = [loc for loc in mod.LOCALES if loc not in have]
            assert len(have) == len(mod.LOCALES), f"verdict.{code} yorlig'i yetishmaydi: {missing}"


def _heuristic(details: dict | None) -> str:
    """M10 migratsiya heuristikasi (migratsiya modulidan delegatsiya).

    Migratsiya fayli `import` qilib bo'lmaydigan joyda (migrations
    namunasi) logikani `_m10_heuristic.py` da saqlaymiz va ikkala joyda
    ishlatamiz.
    """
    from judging.migrations._m10_heuristic import judge_meta_choice

    return judge_meta_choice(details)
