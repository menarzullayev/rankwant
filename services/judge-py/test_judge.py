"""judge-py verdict mantiqi.

Bu testlar bake-off davomida topilgan haqiqiy xatoni qamrab oladi:
isolate signal bilan o'lgan jarayonda `exitcode` bermaydi, va
`meta.get("exitcode", "0") or ...` hech qachon ishlamaydi, chunki "0"
satri TRUTHY — natijada segfault AC deb baholanardi.
"""

from __future__ import annotations

import protocol as P
from judge import classify, normalise, src_name, subst
from protocol import Limits, RunOutcome
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
