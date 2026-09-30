"""File I/O answer classification — judge-go io_answer.go bilan bir xil."""

from __future__ import annotations

from pathlib import Path

from protocol import IO, Limits, RunOutcome, Test

DEFAULT_INPUT = "input.txt"
DEFAULT_OUTPUT = "output.txt"


def _io_mode(io: IO) -> str:
    return io.mode or "stdio"


def _output_name(io: IO) -> str:
    return io.output_file or DEFAULT_OUTPUT


def _input_name(io: IO) -> str:
    return io.input_file or DEFAULT_INPUT


def reset_io_artifacts(work: str, io: IO) -> None:
    if _io_mode(io) == "stdio":
        return
    path = Path(work) / _output_name(io)
    if path.exists():
        path.unlink()


def write_test_input_file(work: str, test: Test, io: IO) -> None:
    mode = _io_mode(io)
    if mode not in ("both", "file"):
        return
    path = Path(work) / _input_name(io)
    path.write_text(test.input, encoding="utf-8")


def classify_answer(out: RunOutcome, test: Test, lim: Limits, work: str, io: IO) -> str:
    from judge import classify

    mode = _io_mode(io)
    if mode == "stdio":
        return classify(out, test, lim)
    base = classify(out, test, lim)
    if base not in ("AC", "WA", "PE"):
        return base
    out_path = Path(work) / _output_name(io)
    if not out_path.exists():
        return "WA" if mode == "file" else base
    data = out_path.read_text(encoding="utf-8")
    synth = RunOutcome(
        stdout=data,
        exit_code=out.exit_code,
        stderr=out.stderr,
        cpu_ms=out.cpu_ms,
        wall_ms=out.wall_ms,
        peak_kb=out.peak_kb,
        oom_kill=out.oom_kill,
        timeout=out.timeout,
        output_exceeded=out.output_exceeded,
        killed_by_sandbox=out.killed_by_sandbox,
    )
    file_v = classify(synth, test, lim)
    if mode == "file":
        return file_v
    if base == "AC" or file_v == "AC":
        return "AC"
    if base == "PE" or file_v == "PE":
        return "PE"
    return "WA"
