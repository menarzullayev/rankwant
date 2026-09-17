# ADR-0022: Judge languages — 35 languages, per-language sandbox settings

**STATUS:** accepted (2026-09-17)
**Affects:** [ADR-0004](0004-judge-engine.md) (language images layer);
[05-domain-model](../05-domain-model/README.md) 🔒 — new `Language` fields

## Problem

RankWant judged three languages (C++23, Python 3.13, Java 21). The rival judges offer
12 (KEP.uz), 19 (Robocontest) and 34 (Codeforces). On 2026-09-17 the owner decided to
add 35 languages — every language offered by at least one rival plus the TIOBE top 50 —
as long as the judge image stays under about **20 GB**:

- on all three rivals: Python, C, C++, Java, C#, JavaScript, Rust, Go, PHP, Kotlin
- on two: Pascal, Ruby, Haskell
- on one: R, Swift, Perl, D, OCaml, TypeScript, Dart, Scala
- on none (TIOBE top 50): Visual Basic .NET, Fortran, Assembly, Ada, Objective-C, COBOL,
  Julia, Caml, Prolog, Lua, PowerShell, Common Lisp
- outside the top 50, on a rival: PyPy, F#

Zig was measured as well and then left out by the owner's decision: the platform does
not need it.

Every language was compiled and run in the real judge (nsjail, the production flags) on
A+B. On the first pass 21 of 35 were accepted. The other 14 failed on assumptions that
held for three languages only:

| Assumption | Broke | Measured |
| ---------- | ----- | -------- |
| The source file name follows from the code prefix | everything outside cpp/py/java was saved as `main.txt` | code reading (`srcName`) |
| `/proc` can be an empty tmpfs | CoreCLR (C#, VB.NET, F#, PowerShell), Dart, Julia, the Swift compiler | `Failed to create CoreCLR, HRESULT: 0x8007000E`; Dart `Failed to retrieve stack bounds`; Julia `unexpected error while retrieving exepath` |
| 64 open files is enough | Roslyn and fsc (compile), R and PowerShell (run) | Roslyn fails at 64, works at 128; R and PowerShell fail at 128, work at 192 |
| One 10 s compile budget | leaves little room for the JVM compilers: kotlinc takes 5.0 s CPU for A+B | CPU time over all compiler threads |
| `/tmp` is writable | rustc, cobc, ocamlopt, R | `Read-only file system` |

Allow-lists add a product-level break: 1,866 of 2,096 problems list the languages they
accept, and every list names only the three founding languages, so a new language would
be refused on all of them.

## Options

1. **Judge0 for the new languages.** Rejected again: ADR-0004's reasons still hold
   (GPL-3.0, its install guide still requires `systemd.unified_cgroup_hierarchy=0`,
   push model with an open HTTP port), and it would not shrink the image — the
   `judge0/judge0:1.13.1-dev` image is 3.30 GB compressed.
2. **A full procfs for every run.** Rejected: it changes existing languages — the JVM
   reads `/proc/self/mountinfo` for container limits and would size its default heap
   from the cgroup — and widens what every submission can read.
3. **Per-language settings on the `Language` row.** Chosen. The mask stays the default;
   only a language that cannot start without `/proc/self` asks for it.
4. **One image or worker pool per language family.** Deferred. A single image fits the
   budget (below); separate pools only pay off when throughput needs them.

## Decision

`Language` gains four fields, carried in every job's `language` object
([protocol](../../services/bakeoff/protocol.md) § «Til»):

| Field | Meaning | Default |
| ----- | ------- | ------- |
| `source_file` | name the source is saved under; a bare file name only | blank → old prefix mapping |
| `compile_time_ms` | CPU budget for one compile | 10 000 |
| `proc_self` | mount a procfs of the sandbox's own processes instead of the mask | false |
| `open_files` | `RLIMIT_NOFILE` for programs | 0 → 64 |

The compile step gets `max(256, open_files)` open files. Hack generators take their
language's compile budget and process limit as well.

**One catalog.** `apps/api/problems/languages.py` lists every language. `seed_demo`
writes it, data migrations add rows to deployed databases, and
`tests/compatibility/check_languages.py` runs each entry inside the judge image.

**Toolchains.** Debian trixie packages where the version is current (GCC 14 family,
Rust 1.85, Go 1.24, PHP 8.4, GHC 9.6, R 4.5, Swift 6.0, LDC 1.40, OCaml 5.3, SWI-Prolog 9.2,
SBCL 2.5, PyPy 7.3, GnuCOBOL 3.2, …). Official archives, pinned by their published
checksums, where Debian has nothing or something too old: .NET SDK 10, Node.js 24 LTS,
PowerShell 7.6, Kotlin 2.4, Scala 3.9, Dart 3.13, Julia 1.13. Build-time assets replace
per-submission work: Go standard-library export data (`go tool compile/link`, 89 ms
instead of 5.6 s CPU), .NET reference lists.

**Sandbox safety of `proc_self`.** The procfs is mounted inside the sandbox's own PID
namespace with `subset=pid,hidepid=invisible`: it lists only the sandbox's processes and
no global files. Bake-off `22-proc-self` checks the exact output —
`['1', 'self', 'thread-self']`, `/proc/1` is the submission itself, no `meminfo`, no
`sys` — and a full procfs prints 62 entries including both (measured), so the case
catches it. The existing `12-proc-read` case still runs masked and passes.

**Allow-lists.** A problem whose list names all three founding languages is treated as
open and receives the new languages; a problem restricted to a subset (387 Python-only,
16 Java-only, 13 C++-only, 8 two-language) stays restricted. The KEP importer follows
the same rule: a KEP problem that allows all twelve general KEP languages is open to
every active language.

## Rationale

Measured on 2026-09-17 in the judge image built from this decision:

- **Size.** Uncompressed layers per group, from `docker history` of the images each
  group's PR built: group 1 +1.94 GB, group 2 +4.36 GB, group 3 +1.79 GB, on a 0.74 GB
  base — about **8.8 GB**, under half the budget. Swift (in group 2's 3.62 GB of
  packages) and Julia (1.1 GB) are the largest single toolchains.
- **All 35 accepted** A+B in nsjail after the changes; the whole bake-off suite, with
  `22-proc-self`, passed on the same judge.
- **Compile cost (CPU, A+B):** g++ 161 ms, javac 634 ms, csc 344 ms, fsc 937 ms,
  swiftc 771 ms, Dart AOT 801 ms, Go 89 ms, kotlinc 5.0 s.

## Consequences

- Languages land in three groups, one PR each, in the order of the list above: the ten
  on all three rivals (C, C#, JavaScript, Rust, Go, PHP and Kotlin join the founding
  three), then the next eleven, then the rest. Each group's image growth and CI build
  time is measured on its own.
- The judge image grows to about 8.8 GB of layers; a clean build downloads about 2 GB.
  CI builds the image on every PR that touches the judge.
- .NET needs `libicu76` and aborts with `Couldn't find a valid ICU package` without it.
  In the all-language measurement it arrived as a dependency of R and GNUstep, so the
  group that brings .NET installs it explicitly.
- Kotlin and Scala get 20 s of compile CPU.
- Julia holds ~200 MB right after start; problems limited to 256 MB leave it little room.
  Per-language memory allowances are a separate decision.
- Thread counts were measured on an 8-core host. The JVM, Node.js and the Go runtime
  size thread pools from the core count, so `processes` must be re-measured when judge
  hosts change.
- Archive-installed toolchains are not updated by apt; each bump is a checksum change
  in the Dockerfile.
- Objective-C uses GCC's runtime: `@autoreleasepool` and ARC are not available, the
  classic `NSAutoreleasePool` is.
- TypeScript runs on Node.js with `--experimental-transform-types`. Plain type stripping
  rejects enums and constructor parameter properties. Types are never checked, and the
  flag is experimental, so a Node.js upgrade has to pass the TypeScript probe again.
- GHC's own libraries are in the loader cache, like the JDK's, so the Haskell command
  needs no `LD_LIBRARY_PATH` pinned to a GHC patch version.
