# Language memory overhead and the MLE rule (2026-11-11)

Stage 2 of [ADR-0060](../../07-adr/0060-abramyan-import.md) § 2.2: the owner chose
"64 MB plus a measured overhead per language, at platform level". This record is
the measurement and the judge defect it turned up.

## Method

- **Judge:** the production judge image (`rankwant-judge:latest`, built from
  `d8026d1`), started as its own compose project with its own Redis queue. It
  had no S3 and no route out, used inline tests, and was torn down with
  `down -v` afterwards. The production queue was not touched.
- **Programs:** for every active language, the accepted A+B source of the
  language matrix (the latest `AC` on `a-plus-b`, read from the production
  database), with the language's own compile and run commands and its
  process, `/proc` and open-file settings.
- **Runs:** 7 jobs × 5 tests = 35 runs per language, under a 1 GB limit so
  that nothing hits it. The figure taken is the peak the judge reports
  (`memory.peak` of the run's cgroup), the same number it compares with the
  limit.
- **Overhead:** the 95th percentile of the 35 samples, rounded up to a whole
  MB. The SQL runner (Python + `sqlite3`) was measured the same way:
  p50 8 472 kB, p95 8 996 kB, giving 9 MB.

## Result (kB; overhead in MB)

| Language | p50 | p95 | max | Overhead |
|---|---:|---:|---:|---:|
| `julia113` | 109 588 | 119 316 | 383 788 | 117 |
| `r45` | 44 040 | 44 572 | 68 260 | 44 |
| `scala39` | 34 408 | 34 940 | 35 376 | 35 |
| `kotlin24` | 25 020 | 32 952 | 46 748 | 33 |
| `powershell76` | 27 376 | 27 900 | 97 892 | 28 |
| `pypy73` | 26 228 | 26 476 | 86 148 | 26 |
| `ts24` | 25 936 | 26 340 | 79 736 | 26 |
| `java21` | 20 376 | 20 988 | 21 000 | 21 |
| `js24` | 13 056 | 13 612 | 49 556 | 14 |
| `caml53` | 11 180 | 11 748 | 25 748 | 12 |
| `prolog92` | 9 820 | 10 160 | 11 928 | 10 |
| `ruby33` | 6 796 | 7 296 | 11 976 | 8 |
| `vbnet17` | 6 748 | 7 284 | 11 416 | 8 |
| `csharp14` | 6 028 | 6 520 | 6 612 | 7 |
| `fsharp10` | 6 372 | 6 948 | 6 988 | 7 |
| `php84` | 5 848 | 6 632 | 28 584 | 7 |
| `py313` | 4 732 | 5 008 | 11 672 | 5 |
| `dart313` | 3 196 | 3 708 | 3 980 | 4 |
| `lisp25` | 3 668 | 3 960 | 36 208 | 4 |
| `ada14`, `cobol32`, `d140`, `go124`, `haskell96`, `ocaml53`, `perl540`, `swift60` | 1 664–2 460 | 2 064–2 940 | ≤ 6 016 | 3 |
| `c17`, `cpp23`, `fortran14`, `lua54`, `nasm216`, `objc14`, `pascal322`, `rust185` | 1 536–1 660 | 1 688–1 936 | ≤ 2 220 | 2 |

The values are frozen in migration `problems.0040` and in
`apps/api/problems/languages.py` (`memory_overhead_kb`).
`tests/test_languages.py` checks that the two agree.

**Where the maxima come from.** Of the 13 values above 1.5 × median, 11 are
the very first test of the first job: the runtime's files read cold, which the
kernel charges to the run's cgroup as page cache. The other two are run-to-run
variance: `kotlin24`, 46 748 kB, and `ada14`, 3 208 kB, both on job 5,
test 1. The 95th percentile leaves the cold run out.

## The MLE defect this measurement found

Before this change the judge returned MLE when `memory.peak >= limit`. But
`memory.peak` counts page cache as well. When the kernel reaches the limit, it
reclaims page cache instead of killing the program, so a program that never
held that much memory could come back MLE.

- **Probe:** a C++ program that holds 1 MB and writes 150 MB of files, run
  under a 64 MB limit in `custom` mode so its output is visible.
  - Run 1 printed `7` (it ran to the end) and was judged **MLE** at a peak of
    exactly 65 536 kB.
  - Run 2 was killed for real: the dirty pages were not written back in time,
    and the output was empty.
- **Production:** a Julia A+B was judged MLE at exactly 262 144 kB, the
  problem's limit (2026-09-29). Afterwards `a-plus-b` was given a 512 MB
  per-language override for Julia.
- **Fix:** MLE now means the kernel killed the program for memory
  (`memory.events` `oom_kill`). The peak is still what the attempt reports;
  it no longer decides the verdict.

The fixed judge was built from this branch and run on the same isolated
stack:

| Case | Verdict |
|---|---|
| 150 MB written, run killed (3 of 4) | MLE |
| 150 MB written, run finished and printed `7` (1 of 4) | **AC** (MLE before) |
| 400 MB `std::vector` under 64 MB (bake-off `05-mle`) | MLE |

**No bake-off case for this.** The fault needs dirty pages, or file pages in
active use, at the moment usage reaches the limit. Files written with `fsync`
are reclaimed before the peak gets there (32 650 kB under a 32 768 kB limit).
Whether a write-back keeps up depends on the host. The rule is guarded
instead by the unit test `TestMLEIsTheKernelKilling` and by the decision rule
`memory_limit_is_what_the_program_holds`.

## Not changed

- **Interactive runs** report no MLE at all (`interactive.go`). That gap was
  there before this change.
- **Reported memory includes page cache.** A cold Julia run still shows about
  380 MB.
