"""judge-py verdict mantiqi.

Bu testlar bake-off davomida topilgan haqiqiy xatoni qamrab oladi:
isolate signal bilan o'lgan jarayonda `exitcode` bermaydi, va
`meta.get("exitcode", "0") or ...` hech qachon ishlamaydi, chunki "0"
satri TRUTHY — natijada segfault AC deb baholanardi.
"""

from __future__ import annotations

from typing import NoReturn

import pytest

import judge as judge_module
import protocol as P
from judge import classify, normalise, src_name, subst
from protocol import Job, Limits, RunOutcome
from protocol import Test as JudgeTest
from sandbox import _exit_code

LIM = Limits(time_ms=1000, memory_kb=65536, output_kb=1024, processes=1)
TEST = JudgeTest(index=1, input="", expected="42\n")


class TestExitCode:
    def test_muvaffaqiyatli_yakun(self) -> None:
        assert _exit_code({"exitcode": "0"}, "") == 0

    def test_signal_bilan_olim_nolga_teng_emas(self) -> None:
        """SEGFAULT: isolate `exitcode` bermaydi, `exitsig` beradi."""
        assert _exit_code({"exitsig": "11"}, "SG") == 139

    def test_status_bor_lekin_exitcode_yoq(self) -> None:
        assert _exit_code({}, "RE") != 0

    def test_nolga_teng_exitcode_status_bilan(self) -> None:
        """Aynan shu holat oldin AC bergan edi."""
        assert _exit_code({"exitcode": "0"}, "SG") != 0

    def test_notogri_exitcode(self) -> None:
        assert _exit_code({"exitcode": "xato"}, "") == 0


class TestNormalise:
    def test_qator_oxiridagi_boshliq(self) -> None:
        assert normalise("42  \n") == normalise("42\n")

    def test_oxirgi_bosh_qatorlar(self) -> None:
        assert normalise("42\n\n\n") == "42"

    def test_crlf(self) -> None:
        assert normalise("1\r\n2\r\n") == normalise("1\n2\n")

    def test_ichki_bosh_qator_saqlanadi(self) -> None:
        assert normalise("1\n\n2\n") == "1\n\n2"


class TestClassify:
    def test_ac(self) -> None:
        out = RunOutcome(stdout="42\n", exit_code=0, cpu_ms=10, peak_kb=1000)
        assert classify(out, TEST, LIM) == P.AC

    def test_wa(self) -> None:
        out = RunOutcome(stdout="41\n", exit_code=0, cpu_ms=10)
        assert classify(out, TEST, LIM) == P.WA

    def test_re_segfault(self) -> None:
        """Regressiya: bu holat oldin AC bergan."""
        out = RunOutcome(stdout="", exit_code=139, cpu_ms=5)
        assert classify(out, TEST, LIM) == P.RE

    def test_tle_cpu_boyicha(self) -> None:
        out = RunOutcome(exit_code=0, cpu_ms=1500)
        assert classify(out, TEST, LIM) == P.TLE

    def test_idleness_tle_emas(self) -> None:
        """Wall tugadi, CPU sarflanmadi → kutib qoldi, sikl aylanmadi."""
        out = RunOutcome(exit_code=0, cpu_ms=5, timeout=True)
        assert classify(out, TEST, LIM) == P.IDLENESS

    def test_wall_tugadi_lekin_cpu_ham_sarflandi(self) -> None:
        out = RunOutcome(exit_code=0, cpu_ms=900, timeout=True)
        assert classify(out, TEST, LIM) == P.TLE

    def test_mle(self) -> None:
        out = RunOutcome(exit_code=0, peak_kb=65536)
        assert classify(out, TEST, LIM) == P.MLE

    def test_oom_kill_mle(self) -> None:
        out = RunOutcome(exit_code=137, oom_kill=True)
        assert classify(out, TEST, LIM) == P.MLE

    def test_ole(self) -> None:
        out = RunOutcome(exit_code=0, output_exceeded=True)
        assert classify(out, TEST, LIM) == P.OLE

    def test_security_violation(self) -> None:
        out = RunOutcome(exit_code=1, killed_by_sandbox=True)
        assert classify(out, TEST, LIM) == P.SECURITY_VIOLATION

    def test_tartib_ole_hammadan_ustun(self) -> None:
        """Chegaralar to'g'ri javobdan OLDIN tekshiriladi."""
        out = RunOutcome(stdout="42\n", exit_code=0, output_exceeded=True)
        assert classify(out, TEST, LIM) == P.OLE


class TestCommandBuilding:
    def test_manba_nomi(self) -> None:
        assert src_name("cpp23") == "main.cpp"
        assert src_name("py313") == "main.py"
        assert src_name("java21") == "Main.java"

    def test_shablon_almashtirish(self) -> None:
        assert subst(["{bin}"], "main.cpp", "prog") == ["prog"]

    def test_mutlaq_yolga_ogiriladi(self) -> None:
        """Sandbox ichida PATH qidiruvi yo'q — mutlaq yo'l shart."""
        result = subst(["python3", "{src}"], "main.py", "prog")
        assert result[0].startswith("/"), result


VALIDATOR: dict[str, object] = {
    "code": "py312",
    "compile": None,
    "run": ["python3", "{src}"],
    "source": "import sys\n",
}


def _job(*, validate_input: bool, validator: dict[str, object] | None = VALIDATOR) -> Job:
    return Job(
        job_id="validator-test",
        language={"code": "py312", "compile": None, "run": ["python3", "{src}"]},
        source="a, b = map(int, input().split())\nprint(a + b)\n",
        limits=Limits(),
        tests=[JudgeTest(index=1, input="0 3\n", expected="3\n")],
        validator=validator,
        validate_input=validate_input,
    )


class TestValidatorYopiqYiqilish:
    """judge-py'da validator bosqichi YO'Q.

    Shartnoma (../bakeoff/protocol.md § «Kirish validatori»): bunday nomzod
    `validate_input` ishini IE bilan RAD ETADI va sandbox'ga umuman
    tegmaydi. Jimgina davom etsa, buzuq kiritma bilan istalgan to'g'ri
    yechimni «sindirish» mumkin bo'lardi.
    """

    @pytest.fixture(autouse=True)
    def sandbox_taqiqlangan(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def ishga_tushdi(*args: object, **kwargs: object) -> NoReturn:
            raise AssertionError("sandbox ishga tushirildi")

        monkeypatch.setattr(judge_module, "Box", ishga_tushdi)
        monkeypatch.setattr(judge_module, "run_sandboxed", ishga_tushdi)

    def test_validate_input_ie_bilan_rad_etiladi(self) -> None:
        result = judge_module.judge(_job(validate_input=True))
        assert result["verdict"] == P.IE
        assert "validator" in result["compile_output"]
        assert result["per_test"] == []
        assert result["failed_test_index"] is None

    def test_validator_berilmagan_bolsa_ham_rad_etiladi(self) -> None:
        result = judge_module.judge(_job(validate_input=True, validator=None))
        assert result["verdict"] == P.IE

    def test_bayroqsiz_ish_sandboxga_yetib_boradi(self) -> None:
        """Nazorat: rad etish faqat bayroqqa bog'liq, har ishga emas."""
        with pytest.raises(AssertionError, match="sandbox ishga tushirildi"):
            judge_module.judge(_job(validate_input=False))

    def test_rad_etilgan_ish_ham_hack_marshrutini_qaytaradi(self) -> None:
        """Rad etish ham hackka bog'lanishi kerak — aks holda u abadiy kutardi."""
        job = _job(validate_input=True)
        job.hack_id, job.hack_stage = 7, "reference"

        result = judge_module.judge(job)

        assert result["hack_id"] == 7
        assert result["hack_stage"] == "reference"


# Haqiqiy job'dagi notanish kalit (`input_ref`) jimgina tashlanadi —
# `validate_input` esa aynan shunday tashlanmasligi shart.
RAW_JOB: dict[str, object] = {
    "job_id": "j",
    "language": {"code": "py312", "run": ["python3", "{src}"]},
    "source": "",
    "limits": {},
    "tests": [{"index": 1, "input": "1\n", "expected": "1\n", "input_ref": "s3://x/1.in"}],
}


class TestJobFromJson:
    def test_validator_maydonlari_oqiladi(self) -> None:
        """Bayroq tashlab yuborilsa, nomzod validatsiyani SEZMASDAN o'tkazardi."""
        job = Job.from_json({**RAW_JOB, "validate_input": True, "validator": VALIDATOR})
        assert job.validate_input is True
        assert job.validator == VALIDATOR

    def test_standart_qiymatlar(self) -> None:
        job = Job.from_json(RAW_JOB)
        assert job.validate_input is False
        assert job.validator is None
        assert job.hack_id == 0
        assert job.hack_stage == ""

    def test_hack_marshruti_oqiladi(self) -> None:
        job = Job.from_json({**RAW_JOB, "hack_id": 7, "hack_stage": "defend"})
        assert job.hack_id == 7
        assert job.hack_stage == "defend"
