"""Bitta job ni to'liq bajaradi — judge-go/judge.go bilan bir xil mantiq."""

from __future__ import annotations

import shutil
import time

import protocol as P
from protocol import Job, JudgeMetaDict, Limits, ResultDict, RunOutcome, Test
from sandbox import Box, IsolateError, run_sandboxed

BOX_ID = 0


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
        "verdict": P.IE,
        "score": 0,
        "time_ms": 0,
        "memory_kb": 0,
        "failed_test_index": None,
        "compile_output": "",
        "per_test": [],
        "judge_meta": meta,
    }

    try:
        with Box(BOX_ID) as box:
            setup = time.monotonic()
            src = src_name(job.language["code"])
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
            for test in job.tests:
                out = run_sandboxed(box, run_cmd, test.input, job.limits, wall_limit)
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
                    continue
                worst = verdict
                result["failed_test_index"] = test.index
                if job.mode != "ioi":
                    break

            result["verdict"] = worst
            result["time_ms"] = max_cpu
            result["memory_kb"] = max_mem
            if job.tests:
                result["score"] = passed * 100 // len(job.tests)

    except IsolateError as exc:
        result["verdict"] = P.IE
        result["compile_output"] = str(exc)

    meta["total_ms"] = int((time.monotonic() - t0) * 1000)
    return result
