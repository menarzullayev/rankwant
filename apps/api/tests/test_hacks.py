"""Hack dvigateli — ADR-0020 siyosatlari va uch bosqichli oqim.

Judge bu yerda soxta: `memory_judge` navbatga tushgan ishlarni ro'yxatda
saqlaydi, natijalar esa `apply_hack_result` ga qo'lda beriladi. Shu
tarzda bosqichlar ketma-ketligi va har bosqichning YOMON yo'li ham
tekshiriladi — haqiqiy sandbox bilan buni takrorlab bo'lmasdi.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.utils import timezone

from hacks import policies
from hacks.models import Hack
from hacks.services import HackError, apply_hack_result, can_view_source, open_policy, submit
from judging.verdicts import Verdict
from problems.models import ReferenceSolution, TestCase, Validator
from qvant.models import QvantTransaction
from ratings.models import UserSolvedProblem

SOURCE = "int main(){}\n"


@pytest.fixture(autouse=True)
def fake_storage(fake_hack_storage: dict[str, str]) -> dict[str, str]:
    """Butun modulda S3 o'rniga lug'at — `conftest.fake_hack_storage`.

    Fixture'ning o'zi conftest'da: API qatlamining testlari ham aynan shu
    soxta saqlashni ishlatadi va ikki nusxa vaqt o'tib ajralib ketardi.
    """
    return fake_hack_storage


def _result(
    hack: Hack, stage: str, verdict: str, *, stdout: str = "", detail: str = ""
) -> dict[str, Any]:
    """Judge qaytaradigan natija — marshrut bilan."""
    return {
        "hack_id": hack.pk,
        "hack_stage": stage,
        "verdict": verdict,
        "compile_output": detail,
        "per_test": [{"index": 1, "verdict": verdict, "stdout": stdout}],
    }


@pytest.mark.django_db
class TestPolicyWindow:
    def test_musobaqasiz_urinish_amaliyot(self, defender_attempt) -> None:
        assert open_policy(defender_attempt) is policies.PRACTICE

    def test_yopilgan_musobaqa_oynasi_amaliyotga_tushmaydi(self, defender_attempt, contest) -> None:
        """Yopilgan oyna «doim ochiq» bo'lib qolmasin.

        `contest` fixture'i allaqachon tugagan va uphack o'chirilgan —
        ya'ni hamma oyna yopiq. Bunday urinish amaliyotga tushib ketsa,
        musobaqa cheklovlari ma'nosini yo'qotardi.
        """
        contest.uphack_days = 0
        contest.save(update_fields=["uphack_days"])
        defender_attempt.contest = contest
        defender_attempt.save(update_fields=["contest"])

        assert open_policy(defender_attempt) is None

    def test_uphack_oynasi_reytingdan_keyin(self, defender_attempt, contest) -> None:
        contest.ratings_applied_at = timezone.now()
        contest.save(update_fields=["ratings_applied_at"])
        defender_attempt.contest = contest
        defender_attempt.save(update_fields=["contest"])

        assert open_policy(defender_attempt) is policies.UPHACK


@pytest.mark.django_db
class TestEligibility:
    def test_ozini_hack_qila_olmaydi(self, defender_attempt, other_user) -> None:
        with pytest.raises(HackError, match="your own solution"):
            submit(other_user, defender_attempt, raw_input="1 2\n")

    def test_yechmaganlar_hack_qila_olmaydi(self, defender_attempt, user) -> None:
        UserSolvedProblem.objects.filter(user=user).delete()
        with pytest.raises(HackError, match="yourself first"):
            submit(user, defender_attempt, raw_input="1 2\n")

    def test_ac_bolmagan_yechim_nishon_emas(self, defender_attempt, user) -> None:
        defender_attempt.verdict = Verdict.WA
        defender_attempt.save(update_fields=["verdict"])
        with pytest.raises(HackError, match="accepted solution"):
            submit(user, defender_attempt, raw_input="1 2\n")

    def test_validatorsiz_masala_yopiq(self, defender_attempt, user) -> None:
        """ADR-0020, 3-qaror: validator MAJBURIY darvoza."""
        Validator.objects.all().delete()
        with pytest.raises(HackError, match="validator"):
            submit(user, defender_attempt, raw_input="1 2\n")

    def test_etalonsiz_masala_yopiq(self, defender_attempt, user) -> None:
        """ADR-0021: javobni beradigan etalon yechimsiz hack ochilmaydi."""
        ReferenceSolution.objects.all().delete()
        with pytest.raises(HackError, match="reference solution"):
            submit(user, defender_attempt, raw_input="1 2\n")

    def test_takroriy_hack_rad_etiladi(self, defender_attempt, user) -> None:
        submit(user, defender_attempt, raw_input="1 2\n")
        with pytest.raises(HackError, match="already running"):
            submit(user, defender_attempt, raw_input="1 3\n")

    def test_manba_faqat_huquqli_hackerga_korinadi(
        self, defender_attempt, user, other_user
    ) -> None:
        assert can_view_source(user, defender_attempt) is True
        # Himoyachining o'zi — bu yo'l orqali emas (u egasi sifatida ko'radi).
        assert can_view_source(other_user, defender_attempt) is False


@pytest.mark.django_db
class TestThreeStages:
    def test_birinchi_ish_validator_bilan_etalonga_ketadi(
        self, defender_attempt, user, memory_judge
    ) -> None:
        submit(user, defender_attempt, raw_input="0 5\n")

        assert len(memory_judge.jobs) == 1
        job = memory_judge.jobs[0]
        assert job.hack_stage == Hack.Stage.REFERENCE
        # Kiritma ISHONCHSIZ — validator shu bosqichda ishlaydi.
        assert job.validate_input is True
        assert job.validator is not None
        assert job.tests[0]["input"] == "0 5\n"

    def test_marshrut_maydonlari_json_bilan_ketadi(
        self, defender_attempt, user, memory_judge
    ) -> None:
        """Dataclass'da bo'lishi YETMAYDI — judge JSON o'qiydi.

        `JudgeJob.to_json()` maydonlarni qo'lda sanab yozadi: dataclass'ga
        qo'shib, o'sha lug'atga qo'shmaslik jim nuqson bo'lardi — ish
        marshrutsiz ketib, natija qaytganda uni hech kim hack bilan
        bog'lay olmasdi va hack abadiy `TESTING` bo'lib qolardi.
        """
        hack = submit(user, defender_attempt, raw_input="0 5\n")

        payload = json.loads(memory_judge.jobs[0].to_json())

        assert payload["hack_id"] == hack.pk
        assert payload["hack_stage"] == Hack.Stage.REFERENCE
        assert payload["validate_input"] is True
        assert payload["validator"]["source"]

    def test_toliq_oqim_muvaffaqiyatli_hack(
        self, defender_attempt, user, other_user, memory_judge, fake_storage
    ) -> None:
        hack = submit(user, defender_attempt, raw_input="0 5\n")

        # 1-bosqich: etalon yechim javobni berdi.
        apply_hack_result(_result(hack, Hack.Stage.REFERENCE, Verdict.AC, stdout="5\n"))
        hack.refresh_from_db()
        assert hack.stage == Hack.Stage.DEFEND
        defend_job = memory_judge.jobs[1]
        assert defend_job.hack_stage == Hack.Stage.DEFEND
        assert defend_job.source == "hacked_code"
        # Kiritma allaqachon tekshirilgan — ikkinchi marta validatsiya yo'q.
        assert defend_job.validate_input is False
        assert defend_job.tests[0]["output_ref"].endswith(".out")

        # 2-bosqich: himoyachining kodi yiqildi.
        apply_hack_result(_result(hack, Hack.Stage.DEFEND, Verdict.WA))
        hack.refresh_from_db()
        defender_attempt.refresh_from_db()

        assert hack.status == Hack.Status.SUCCESSFUL
        assert hack.defender_verdict == Verdict.WA
        assert defender_attempt.verdict == Verdict.HACKED
        # `AC` bekor qilindi — yechilgan masala yozuvi ham ketdi.
        assert not UserSolvedProblem.objects.filter(
            user=other_user, problem=defender_attempt.problem
        ).exists()
        # Amaliyot siyosati: mukofot faqat ledger orqali (ADR-0002).
        assert QvantTransaction.objects.filter(
            user=user, reason=QvantTransaction.Reason.HACK
        ).exists()
        # Test asosiy to'plamga qo'shildi va manbasi ko'rinadi.
        added = TestCase.objects.filter(origin=TestCase.Origin.HACK).first()
        assert added is not None
        assert hack.added_test_id == added.pk

    def test_himoyachi_otsa_muvaffaqiyatsiz(self, defender_attempt, user, memory_judge) -> None:
        hack = submit(user, defender_attempt, raw_input="1 2\n")
        apply_hack_result(_result(hack, Hack.Stage.REFERENCE, Verdict.AC, stdout="3\n"))
        apply_hack_result(_result(hack, Hack.Stage.DEFEND, Verdict.AC))

        hack.refresh_from_db()
        defender_attempt.refresh_from_db()
        assert hack.status == Hack.Status.UNSUCCESSFUL
        assert defender_attempt.verdict == Verdict.AC
        assert not TestCase.objects.filter(origin=TestCase.Origin.HACK).exists()

    def test_validator_rad_etsa_jazolanmaydi(self, defender_attempt, user) -> None:
        """ADR-0020, 3-qaror: noto'g'ri test ARZON bo'lishi kerak."""
        hack = submit(user, defender_attempt, raw_input="0 5\n")
        apply_hack_result(
            _result(hack, Hack.Stage.REFERENCE, Verdict.WRONG_TEST, detail="1 <= a buzildi")
        )

        hack.refresh_from_db()
        defender_attempt.refresh_from_db()
        assert hack.status == Hack.Status.INVALID_INPUT
        assert "buzildi" in hack.detail
        assert defender_attempt.verdict == Verdict.AC
        assert not QvantTransaction.objects.exists()

    def test_etalon_yiqilsa_hisobga_olinmaydi(self, defender_attempt, user) -> None:
        """Masala nuqsoni hackerga yozilmaydi (ADR-0021)."""
        hack = submit(user, defender_attempt, raw_input="1 2\n")
        apply_hack_result(_result(hack, Hack.Stage.REFERENCE, Verdict.TLE))

        hack.refresh_from_db()
        assert hack.status == Hack.Status.IGNORED
        assert hack.points == 0

    def test_judge_yiqilsa_hisobga_olinmaydi(self, defender_attempt, user) -> None:
        hack = submit(user, defender_attempt, raw_input="1 2\n")
        apply_hack_result(_result(hack, Hack.Stage.REFERENCE, Verdict.AC, stdout="3\n"))
        apply_hack_result(_result(hack, Hack.Stage.DEFEND, Verdict.IE))

        hack.refresh_from_db()
        defender_attempt.refresh_from_db()
        assert hack.status == Hack.Status.IGNORED
        assert defender_attempt.verdict == Verdict.AC

    def test_eski_bosqich_javobi_tashlanadi(self, defender_attempt, user) -> None:
        """Kechikkan javob keyingi bosqichni buzib yubormasin."""
        hack = submit(user, defender_attempt, raw_input="1 2\n")

        apply_hack_result(_result(hack, Hack.Stage.DEFEND, Verdict.WA))

        hack.refresh_from_db()
        defender_attempt.refresh_from_db()
        assert hack.status == Hack.Status.TESTING
        assert hack.stage == Hack.Stage.REFERENCE
        assert defender_attempt.verdict == Verdict.AC


@pytest.mark.django_db
class TestGenerator:
    def test_generator_chiqishi_kiritma_boladi(
        self, defender_attempt, user, language, memory_judge, fake_storage
    ) -> None:
        hack = submit(
            user,
            defender_attempt,
            generator_language=language,
            generator_source="print(1)",
        )
        assert memory_judge.jobs[0].hack_stage == Hack.Stage.GENERATE

        apply_hack_result(_result(hack, Hack.Stage.GENERATE, Verdict.AC, stdout="7 8\n"))

        hack.refresh_from_db()
        assert hack.stage == Hack.Stage.REFERENCE
        assert hack.input_size == len("7 8\n")
        assert memory_judge.jobs[1].tests[0]["input"] == "7 8\n"

    def test_generator_yiqilsa_alohida_holat(self, defender_attempt, user, language) -> None:
        hack = submit(user, defender_attempt, generator_language=language, generator_source="bad")
        apply_hack_result(_result(hack, Hack.Stage.GENERATE, Verdict.CE, detail="xato"))

        hack.refresh_from_db()
        assert hack.status == Hack.Status.GENERATOR_CRASHED
        assert hack.points == 0

    def test_bosh_generator_rad_etiladi(self, defender_attempt, user, language) -> None:
        with pytest.raises(HackError, match="Generator source"):
            submit(user, defender_attempt, generator_language=language, generator_source="  ")

    def test_generator_oz_tilining_chegaralarini_oladi(
        self, defender_attempt, user, language, memory_judge
    ) -> None:
        """A JVM or .NET generator does not start with one process (ADR-0022)."""
        language.process_limit = 32
        language.compile_time_ms = 20_000
        language.save(update_fields=["process_limit", "compile_time_ms"])

        submit(user, defender_attempt, generator_language=language, generator_source="print(1)")

        limits = memory_judge.jobs[0].limits
        assert limits["processes"] == 32
        assert limits["compile_time_ms"] == 20_000
