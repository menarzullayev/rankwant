"""Bitta job ni to'liq bajaradi — judge-go/judge.go bilan bir xil mantiq."""

from __future__ import annotations

import re
import shutil
import time
from typing import Any

import protocol as P
from protocol import Job, JudgeMetaDict, Limits, ResultDict, RunOutcome, Test
from sandbox import Box, IsolateError, run_sandboxed

BOX_ID = 0
#: RLIMIT_NOFILE for compilers — judge-go `compileOpenFiles`.
COMPILE_OPEN_FILES = 256


def normalise(s: str) -> str:
    """Standart checker: qator oxiridagi bo'shliq va oxirgi bo'sh qatorlar e'tiborsiz."""
    lines = [ln.rstrip(" \t") for ln in s.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def src_name(lang_code: str) -> str:
    if lang_code.startswith(("cpp", "c++")):
        return "main.cpp"
    if lang_code.startswith("py"):
        return "main.py"
    if lang_code.startswith("java"):
        return "Main.java"
    return "main.txt"


#: Same rule as judge-go `sourceFileName`: a bare name with an extension.
SOURCE_FILE = re.compile(r"[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)+")


def source_name(language: dict[str, Any]) -> str:
    """The name the source is saved under — the language's own, else the old mapping.

    A name that is not a bare file name raises: it is joined onto the box
    directory, and replacing it with `main.txt` would turn one wrong row into a
    CE for every submission in that language.
    """
    name = language.get("source_file") or ""
    if not name:
        return src_name(language["code"])
    if not SOURCE_FILE.fullmatch(name):
        raise ValueError(f"til ta'rifida noto'g'ri manba fayl nomi: {name!r}")
    return name


def subst(args: list[str], src: str, binary: str) -> list[str]:
    out = [a.replace("{src}", src).replace("{bin}", binary) for a in args]
    # Sandbox ichida PATH bo'yicha qidiruv yo'q — birinchi element MUTLAQ
    # yo'l bo'lishi shart, aks holda execve ENOENT beradi.
    # (judge-go da ham xuddi shu tuzatish bor — nomzodlar bir xil sharoitda.)
    if out and not out[0].startswith("/"):
        resolved = shutil.which(out[0])
        if resolved:
            out[0] = resolved
    return out


def classify(out: RunOutcome, test: Test, lim: Limits) -> str:
    """Bitta test natijasini verdictga aylantiradi.

    Tartib muhim: xavfsizlik va resurs chegaralari to'g'ri javobdan OLDIN.
    """
    if out.output_exceeded:
        return P.OLE
    if out.oom_kill or (lim.memory_kb and out.peak_kb >= lim.memory_kb):
        return P.MLE
    if out.cpu_ms > lim.time_ms:
        return P.TLE
    if out.timeout:
        # Wall tugadi, CPU sarflanmadi → kutib qoldi, sikl aylanmadi
        if out.cpu_ms * 4 < lim.time_ms:
            return P.IDLENESS
        return P.TLE
    if out.killed_by_sandbox:
        return P.SECURITY_VIOLATION
    if out.exit_code == 0:
        return P.AC if normalise(out.stdout) == normalise(test.expected) else P.WA
    return P.RE


def judge(job: Job) -> ResultDict:
    t0 = time.monotonic()
    meta: JudgeMetaDict = {
        "worker": "judge-py",
        "sandbox": "isolate",
        "queue_wait_ms": 0,
        "sandbox_setup_ms": 0,
        "total_ms": 0,
    }
    result: ResultDict = {
        "job_id": job.job_id,
        "hack_id": job.hack_id,
        "hack_stage": job.hack_stage,
        "verdict": P.IE,
        "score": 0,
        "time_ms": 0,
        "memory_kb": 0,
        "failed_test_index": None,
        "compile_output": "",
        "per_test": [],
        "judge_meta": meta,
    }

    # ⚠️ YOPIQ YIQILISH — shartnoma: ../bakeoff/protocol.md § «Kirish validatori».
    #
    # Bu nomzodda validator bosqichi YO'Q. Bayroqni jimgina e'tiborsiz
    # qoldirish eng xavfli yo'l bo'lardi: validatsiya butunlay o'chib
    # qolardi va buzuq kiritma bilan istalgan TO'G'RI yechimni
    # «sindirish» mumkin bo'lib qolardi. Nomzodlar almashtiriladigan
    # bo'lgani uchun bu xavf nazariy emas — judge-go ga sozlangan ish
    # judge-py ga tushib qolishi mumkin.
    #
    # `result["verdict"]` yuqorida allaqachon `IE`: ichki xato, submission
    # aybi emas.
    if job.validate_input:
        result["compile_output"] = (
            "judge-py kirish validatorini qo'llab-quvvatlamaydi — "
            "validate_input=true bo'lgan ish rad etildi"
        )
        meta["total_ms"] = int((time.monotonic() - t0) * 1000)
        return result

    # The same fail-closed rule for `proc_self`: isolate has no procfs limited to
    # the box's own processes, and running such a language under the mask would
    # only hand every submission a misleading CE or RE.
    if job.language.get("proc_self"):
        result["compile_output"] = "judge-py proc_self'ni qo'llab-quvvatlamaydi — ish rad etildi"
        meta["total_ms"] = int((time.monotonic() - t0) * 1000)
        return result

    try:
        src = source_name(job.language)
    except ValueError as err:
        result["compile_output"] = str(err)
        meta["total_ms"] = int((time.monotonic() - t0) * 1000)
        return result
    open_files = int(job.language.get("open_files") or 0)

    try:
        with Box(BOX_ID) as box:
            setup = time.monotonic()
            box.put(src, job.source)
            meta["sandbox_setup_ms"] = int((time.monotonic() - setup) * 1000)

            # ── Kompilyatsiya ──────────────────────────────────────
            compile_cmd = job.language.get("compile")
            if compile_cmd:
                clim = Limits(**job.limits.__dict__)
                clim.time_ms = job.limits.compile_time_ms
                clim.memory_kb = 1024 * 1024
                out = run_sandboxed(
                    box,
                    subst(compile_cmd, src, "prog"),
                    "",
                    clim,
                    job.limits.compile_time_ms,
                    allow_many_processes=True,
                    open_files=max(COMPILE_OPEN_FILES, open_files),
                )
                if out.timeout:
                    result["verdict"] = P.COMPILE_TIMEOUT
                    result["compile_output"] = out.stderr
                    meta["total_ms"] = int((time.monotonic() - t0) * 1000)
                    return result
                if out.exit_code != 0:
                    result["verdict"] = P.CE
                    result["compile_output"] = out.stderr
                    meta["total_ms"] = int((time.monotonic() - t0) * 1000)
                    return result

            # ── Testlar ────────────────────────────────────────────
            run_cmd = subst(job.language["run"], src, "prog")
            # Wall chegarasi CPU dan 3× kattaroq — farqi IDLENESS ni ochadi
            wall_limit = job.limits.time_ms * 3 + 1000

            worst, max_cpu, max_mem, passed = P.AC, 0, 0, 0
            by_group: dict[int, list[int]] = {}
            failed_group: set[int] = set()
            for test in job.tests:
                out = run_sandboxed(
                    box, run_cmd, test.input, job.limits, wall_limit, open_files=open_files
                )
                verdict = classify(out, test, job.limits)
                max_cpu = max(max_cpu, out.cpu_ms)
                max_mem = max(max_mem, out.peak_kb)
                result["per_test"].append(
                    {
                        "index": test.index,
                        "verdict": verdict,
                        "time_ms": out.cpu_ms,
                        "memory_kb": out.peak_kb,
                    }
                )
                if verdict == P.AC:
                    passed += 1
                    by_group.setdefault(test.subtask, []).append(test.points)
                    continue
                worst = verdict
                failed_group.add(test.subtask)
                if result["failed_test_index"] is None:
                    result["failed_test_index"] = test.index
                if job.mode != "ioi":
                    break

            result["time_ms"] = max_cpu
            result["memory_kb"] = max_mem
            result["score"] = _score(job, passed, by_group, failed_group)
            # Qisman ball olingan bo'lsa PARTIAL — birinchi yiqilgan
            # testning verdicti emas.
            if job.mode == "ioi" and worst not in (P.AC, P.IE) and result["score"] > 0:
                worst = "PARTIAL"
            result["verdict"] = worst

    except IsolateError as exc:
        result["verdict"] = P.IE
        result["compile_output"] = str(exc)

    meta["total_ms"] = int((time.monotonic() - t0) * 1000)
    return result


def _score(job: Job, passed: int, by_group: dict[int, list[int]], failed_group: set[int]) -> int:
    """Ball — rejimga qarab.

    ACM: hammasi o'tsa 100, aks holda 0.
    IOI subtask bilan: `min` da guruh TO'LIQ o'tsagina ball beriladi,
    `sum` da o'tgan testlarning ballari yig'iladi.
    Subtasksiz IOI: o'tgan testlar ulushi (eski xatti-harakat).
    """
    if not job.tests:
        return 0
    if job.mode != "ioi":
        return 100 if passed == len(job.tests) else 0
    if not job.subtasks:
        return passed * 100 // len(job.tests)

    total = 0
    for st in job.subtasks:
        if st.scoring == "sum":
            total += sum(by_group.get(st.id, []))
        elif st.id not in failed_group:
            total += st.points
    return total
