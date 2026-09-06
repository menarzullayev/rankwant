"""isolate sandbox qatlami — bake-off nomzod B.

isolate (ioi/isolate, GPL-2.0+) IOI va CMS ishlatadigan CP standarti.
Muhim cheklov: isolate **cgroup v1** ga tayanadi. Zamonaviy Linux (bu host ham)
cgroup v2 da ishlaydi, ya'ni GRUB'ga `systemd.unified_cgroup_hierarchy=0`
yozish kerak bo'ladi. Bu bake-off'ning asosiy o'lchov nuqtalaridan biri
(ADR-0004 § cgroup v2 muvofiqligi).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from protocol import Limits, RunOutcome

ISOLATE = shutil.which("isolate") or "/usr/local/bin/isolate"


class IsolateError(RuntimeError):
    pass


class Box:
    """isolate box — kontekst menejer sifatida, chiqishda albatta tozalanadi."""

    def __init__(self, box_id: int) -> None:
        self.box_id = box_id
        self.path: Path | None = None

    def __enter__(self) -> "Box":
        out = subprocess.run(
            [ISOLATE, f"--box-id={self.box_id}", "--cg", "--init"],
            capture_output=True, text=True,
        )
        if out.returncode != 0:
            raise IsolateError(f"isolate --init: {out.stderr.strip()}")
        self.path = Path(out.stdout.strip()) / "box"
        return self

    def __exit__(self, *exc: object) -> None:
        subprocess.run(
            [ISOLATE, f"--box-id={self.box_id}", "--cg", "--cleanup"],
            capture_output=True,
        )

    def put(self, name: str, content: str, mode: int = 0o644) -> None:
        assert self.path is not None
        target = self.path / name
        target.write_text(content, encoding="utf-8")
        target.chmod(mode)


def _parse_meta(meta_path: Path) -> dict[str, str]:
    if not meta_path.exists():
        return {}
    out: dict[str, str] = {}
    for line in meta_path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def run_sandboxed(
    box: Box,
    cmd: list[str],
    stdin: str,
    lim: Limits,
    wall_limit_ms: int,
    *,
    allow_many_processes: bool = False,
) -> RunOutcome:
    """Buyruqni isolate ostida ishga tushiradi va resurslarni o'lchaydi."""
    assert box.path is not None
    meta = box.path.parent / "meta.txt"
    box.put("__stdin", stdin)

    procs = 16 if allow_many_processes else max(1, lim.processes)
    args = [
        ISOLATE,
        f"--box-id={box.box_id}",
        "--cg",                                   # cgroup orqali cheklash va o'lchash
        f"--meta={meta}",
        f"--time={lim.time_ms / 1000:.3f}",       # CPU vaqti
        f"--wall-time={wall_limit_ms / 1000:.3f}",# wall — IDLENESS uchun
        f"--cg-mem={lim.memory_kb}",
        f"--fsize={lim.output_kb}",
        f"--processes={procs}",                   # 09-fork-bomb
        "--stdin=__stdin",
        "--stdout=__stdout",
        "--stderr=__stderr",
        # Izolyatsiya: tarmoq default'da yopiq (11-network),
        # /proc mount qilinmaydi (12-proc-read), box tashqarisi ko'rinmaydi (10-file-write).
        "--run", "--",
    ] + cmd

    start = time.monotonic()
    proc = subprocess.run(args, capture_output=True, text=True)
    wall = int((time.monotonic() - start) * 1000)

    m = _parse_meta(meta)
    stdout = (box.path / "__stdout").read_text(encoding="utf-8", errors="replace") \
        if (box.path / "__stdout").exists() else ""
    stderr = (box.path / "__stderr").read_text(encoding="utf-8", errors="replace") \
        if (box.path / "__stderr").exists() else ""

    status = m.get("status", "")          # RE | SG | TO | XX
    message = m.get("message", "")
    cpu_ms = int(float(m.get("time", "0")) * 1000)
    peak_kb = int(m.get("cg-mem", m.get("max-rss", "0")) or 0)

    truncated = len(stdout.encode()) >= lim.output_kb * 1024
    if not truncated and status == "SG" and "size" in message.lower():
        truncated = True

    return RunOutcome(
        stdout=stdout[: lim.output_kb * 1024],
        stderr=stderr[:65536],
        exit_code=int(m.get("exitcode", "0") or (1 if status else 0)),
        cpu_ms=cpu_ms,
        wall_ms=wall,
        peak_kb=peak_kb,
        oom_kill=("cg-oom-killed" in m) or (status == "SG" and "memory" in message.lower()),
        timeout=(status == "TO"),
        output_exceeded=truncated,
        # isolate qoidani buzganda o'ldiradi; buni RE dan ajratamiz
        killed_by_sandbox=(
            status == "SG"
            and bool(re.search(r"forbidden|not allowed|permission", message, re.I))
        ),
    )
