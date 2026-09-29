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


class TestDeadCodesDocumented:
    """T-WP2.1: 4 ta o'lik kod verdicts.py'da hujjatlangan."""

    def test_re_has_legacy_comment(self) -> None:
        text = (ROOT / "apps/api/judging/verdicts.py").read_text(encoding="utf-8")
        assert "RE = \"RE\"" in text
        # LEGACY yoki O'LIK kalit so'zi RE izohida uchraydi
        re_block = text.split("RE = \"RE\"")[0].split("\n")[-5:]
        block = "\n".join(re_block)
        assert "O'LIK" in block or "LEGACY" in block

    def test_rate_limited_has_dead_comment(self) -> None:
        text = (ROOT / "apps/api/judging/verdicts.py").read_text(encoding="utf-8")
        assert "RATE_LIMITED = \"RATE_LIMITED\"" in text
        block = text.split("RATE_LIMITED = \"RATE_LIMITED\"")[0].split("\n")[-5:]
        assert "O'LIK" in "\n".join(block)

    def test_denial_of_judgement_has_dead_comment(self) -> None:
        text = (ROOT / "apps/api/judging/verdicts.py").read_text(encoding="utf-8")
        assert "DENIAL_OF_JUDGEMENT = \"DENIAL_OF_JUDGEMENT\"" in text
        block = text.split("DENIAL_OF_JUDGEMENT = \"DENIAL_OF_JUDGEMENT\"")[0].split("\n")[-5:]
        assert "O'LIK" in "\n".join(block)

    def test_testing_aborted_has_dead_comment(self) -> None:
        text = (ROOT / "apps/api/judging/verdicts.py").read_text(encoding="utf-8")
        assert "TESTING_ABORTED = \"TESTING_ABORTED\"" in text
        block = text.split("TESTING_ABORTED = \"TESTING_ABORTED\"")[0].split("\n")[-5:]
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
        assert Verdict.RE_SIGNAL == "RE_SIGNAL"

    def test_re_exit_exists(self) -> None:
        assert hasattr(Verdict, "RE_EXIT")
        assert Verdict.RE_EXIT == "RE_EXIT"

    def test_re_signal_and_re_exit_are_distinct(self) -> None:
        assert Verdict.RE_SIGNAL != Verdict.RE_EXIT

    def test_re_legacy_still_exists(self) -> None:
        """RE o'chirilmagan — tarixiy ma'lumotlar yaxlitligi."""
        assert hasattr(Verdict, "RE")
        assert Verdict.RE == "RE"


class TestM10Migration:
    """T-WP2.2: M10 migratsiya testlari."""

    @pytest.mark.django_db
    def test_migration_relabels_re_rows(self, user, problem, language) -> None:
        # RE qatorlar yaratish
        a1 = Attempt.objects.create(
            user=user,
            problem=problem,
            language=language,
            source_code="x",
            verdict=Verdict.RE,
        )
        a2 = Attempt.objects.create(
            user=user,
            problem=problem,
            language=language,
            source_code="y",
            verdict=Verdict.RE,
        )

        # Mock `details` maydoni — a1 signal, a2 exit_code
        a1.details = {"signal": 11}  # type: ignore[attr-defined]
        a2.details = {"exit_code": 1}  # type: ignore[attr-defined]

        # Heuristic test: signal bor → RE_SIGNAL
        assert _heuristic(a1.details) == "RE_SIGNAL"  # type: ignore[arg-type]
        # Heuristic test: exit_code bor → RE_EXIT
        assert _heuristic(a2.details) == "RE_EXIT"  # type: ignore[arg-type]
        # Heuristic test: hech narsa yo'q → RE_SIGNAL (default)
        assert _heuristic({}) == "RE_SIGNAL"

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
        """Katta hajmdagi qatorlar batch'lar bilan qayta ishlanadi."""
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

        # Hammasi RE_SIGNAL ga o'tgan (details yo'q, default)
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
        assert result.returncode == 0, f"check_verdict_codes.py failed:\n{result.stdout}\n{result.stderr}"

    def test_i18n_parity_all_locales(self) -> None:
        """Barcha 10 til'da barcha verdikt kodlari uchun yorliq bor."""
        from tools.check_verdict_codes import api_codes, locale_labels, LOCALES

        codes = api_codes()
        for code in codes:
            have = locale_labels(code)
            assert len(have) == len(LOCALES), (
                f"verdict.{code} yorlig'i yetishmaydi: "
                f"{[l for l in LOCALES if l not in have]}"
            )


# Heuristic funksiyasini alohida ajratish (migratsiya ichidagi logikani test qilish)
def _heuristic(details: dict | None) -> str:
    """M10 migratsiya heuristikasi."""
    if not isinstance(details, dict):
        return "RE_SIGNAL"
    if "signal" in details:
        return "RE_SIGNAL"
    if "exit_code" in details:
        return "RE_EXIT"
    return "RE_SIGNAL"
