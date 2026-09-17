"""Til matritsasi: e'lon qilingan versiya judge image'idagi haqiqat bilan mos kelishini tekshiradi.

Nega kerak: platforma foydalanuvchiga "Python 3.12" deb ko'rsatsa, judge esa
3.11 ishlatsa, 3.12 sintaksisi tushunarsiz SyntaxError bilan yiqiladi va
foydalanuvchi buni o'z kodidan deb o'ylaydi. Buni faqat har tilda o'z
versiyasini chop etadigan dastur ishga tushirib bilib bo'ladi.

Ishlatish:  python3 check_languages.py [image]
"""

from __future__ import annotations

import ast
import pathlib
import shlex
import subprocess
import sys
from typing import Any

# Hisobotdagi `✓` Windows'da quvurga yozilganda `cp1252` ga sig'maydi va
# skript o'z natijasini chop etayotib quladi — sabab va batafsil izoh
# `tools/_console.py` da. Guard shu yerda takrorlanadi: bu fayl `tests/`
# ichida va `tools/` ni import qilmaydi.
for _stream in (sys.stdout, sys.stderr):
    if (getattr(_stream, "encoding", "") or "").lower().replace("-", "") != "utf8":
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass

REPO = pathlib.Path(__file__).resolve().parents[2]
CATALOG = REPO / "apps/api/problems/languages.py"

#: Har til o'z runtime versiyasini chop etadi — e'londan mustaqil manba.
#:
#: Keyed by the exact language code: with dozens of languages a prefix match
#: picks the wrong probe (`c` would catch `cpp23` and `csharp14`). The file name
#: comes from the catalog, so a probe runs under the same name as a submission.
#:
#: An entry is `(source, parse, *extra)`. `extra` are shell lines run after the
#: program, for compilers whose version a program cannot print (rustc); `parse`
#: then reads the last line.
PROBES: dict[str, tuple[Any, ...]] = {
    "cpp23": (
        '#include <cstdio>\nint main(){printf("%ld\\n", __cplusplus);return 0;}\n',
        lambda out: {"202302": "23", "202100": "2b", "201703": "17", "201402": "14"}.get(
            out.strip().rstrip("L")[:6], out.strip()
        ),
    ),
    "py313": (
        "import sys\nprint('%d.%d' % sys.version_info[:2])\n",
        lambda out: out.strip(),
    ),
    "java21": (
        'public class Main{public static void main(String[] a){'
        'System.out.println(System.getProperty("java.version").split("\\\\.")[0]);}}\n',
        lambda out: out.strip(),
    ),
    "c17": (
        '#include <stdio.h>\nint main(void){printf("%ld\\n", __STDC_VERSION__);return 0;}\n',
        lambda out: {"201710": "17", "202311": "23", "201112": "11"}.get(
            out.strip().rstrip("L")[:6], out.strip()
        ),
    ),
    "csharp14": (
        # `p?.X = 1` is C# 14 syntax: an older compiler refuses the probe outright.
        "class P{int X; static void Main(){P p = new P(); p?.X = 1;"
        "System.Console.WriteLine(System.Environment.Version.Major + p.X - 1);}}\n",
        lambda out: {"10": "14 (.NET 10)"}.get(out.strip(), out.strip()),
    ),
    "js24": (
        'console.log(process.versions.node.split(".")[0]);\n',
        lambda out: f"(Node.js {out.strip()})",
    ),
    "rust185": (
        'fn main() { println!("ok"); }\n',
        lambda out: ".".join(out.strip().splitlines()[-1].split()[1].split(".")[:2]),
        "rustc --version",
    ),
    "go124": (
        'package main\n\nimport (\n\t"fmt"\n\t"runtime"\n)\n\nfunc main() { fmt.Println(runtime.Version()) }\n',
        lambda out: ".".join(out.strip().removeprefix("go").split(".")[:2]),
    ),
    "php84": (
        '<?php echo PHP_MAJOR_VERSION, ".", PHP_MINOR_VERSION, "\\n";\n',
        lambda out: out.strip(),
    ),
    "kotlin24": (
        'fun main() { println("${KotlinVersion.CURRENT.major}.${KotlinVersion.CURRENT.minor}") }\n',
        lambda out: out.strip(),
    ),
    "pascal322": (
        "begin\n  writeln({$I %FPCVERSION%});\nend.\n",
        lambda out: "(Free Pascal " + ".".join(out.strip().split(".")[:2]) + ")",
    ),
    "ruby33": (
        'puts RUBY_VERSION.split(".")[0, 2].join(".")\n',
        lambda out: out.strip(),
    ),
    "haskell96": (
        "import Data.Version (showVersion)\nimport System.Info (compilerVersion)\n\n"
        "main :: IO ()\nmain = putStrLn (showVersion compilerVersion)\n",
        lambda out: f"(GHC {out.strip()})",
    ),
    "r45": (
        'cat(R.version$major, ".", strsplit(R.version$minor, ".", fixed = TRUE)[[1]][1], "\\n", sep = "")\n',
        lambda out: out.strip(),
    ),
    "swift60": (
        # compiler(), not swift(): Swift 6 compiles in Swift 5 language mode by default.
        '#if compiler(>=6.1)\nprint("6.1 or newer")\n#elseif compiler(>=6.0)\nprint("6.0")\n'
        '#else\nprint("older than 6.0")\n#endif\n',
        lambda out: out.strip(),
    ),
    "perl540": (
        'printf("%vd\\n", $^V);\n',
        lambda out: ".".join(out.strip().split(".")[:2]),
    ),
    "d140": (
        'import std.stdio;\n\nvoid main() { writeln("ok"); }\n',
        # "LDC - the LLVM D compiler (1.40.0):"
        lambda out: "(LDC "
        + ".".join(out.strip().splitlines()[-1].split("(")[1].split(")")[0].split(".")[:2])
        + ")",
        "ldc2 --version | head -n 1",
    ),
    "ocaml53": (
        "let () =\n  match String.split_on_char '.' Sys.ocaml_version with\n"
        '  | major :: minor :: _ -> Printf.printf "%s.%s\\n" major minor\n'
        "  | _ -> print_endline Sys.ocaml_version\n",
        lambda out: out.strip(),
    ),
    "ts24": (
        # An enum and a parameter property: plain type stripping refuses both.
        'enum Runtime { Node = "Node.js" }\n'
        "class Probe {\n  constructor(private readonly version: string) {}\n"
        '  label(): string { return `(${Runtime.Node} ${this.version.split(".")[0]})`; }\n}\n'
        "console.log(new Probe(process.versions.node).label());\n",
        lambda out: out.strip(),
    ),
    "dart313": (
        "import 'dart:io';\n\nvoid main() {\n"
        "  print(Platform.version.split(' ').first.split('.').take(2).join('.'));\n}\n",
        lambda out: out.strip(),
    ),
    "scala39": (
        "object Main {\n  def main(args: Array[String]): Unit =\n"
        "    println(classOf[scala.deriving.Mirror].getPackage.getImplementationVersion"
        '.split(\'.\').take(2).mkString("."))\n'
        "}\n",
        lambda out: out.strip(),
    ),
    "vbnet17": (
        "Module Program\n    Sub Main()\n"
        "        System.Console.WriteLine(System.Environment.Version.Major)\n"
        "    End Sub\nEnd Module\n",
        # The program prints the runtime; vbc marks the language version it compiles
        # with "(default)" ("17.13 (default)"; "latest" is a separate keyword line).
        lambda out: "{} (.NET {})".format(
            out.strip().splitlines()[-1].split()[0], out.strip().splitlines()[-2]
        ),
        "/usr/bin/env DOTNET_EnableWriteXorExecute=0 /opt/dotnet/dotnet"
        " /opt/rankwant/dotnet/roslyn/vbc.dll -langversion:? | grep -F '(default)'",
    ),
    "fortran14": (
        "program p\n  use iso_fortran_env\n  print '(a)', compiler_version()\nend program p\n",
        # "GCC version 14.2.0"
        lambda out: "(GFortran " + out.strip().split()[-1].split(".")[0] + ")",
    ),
    "nasm216": (
        "section .data\nmsg db 'ok', 10\nsection .text\nglobal _start\n_start:\n"
        "    mov eax, 1\n    mov edi, 1\n    lea rsi, [rel msg]\n    mov edx, 3\n    syscall\n"
        "    mov eax, 60\n    xor edi, edi\n    syscall\n",
        # "NASM version 2.16.03 compiled on ..."
        lambda out: "(NASM "
        + ".".join(out.strip().splitlines()[-1].split()[2].split(".")[:2])
        + ", x86-64)",
        "nasm -v",
    ),
    "ada14": (
        "with Ada.Text_IO;\nwith GNAT.Compiler_Version;\n\nprocedure Main is\n"
        "   package CV is new GNAT.Compiler_Version;\nbegin\n"
        "   Ada.Text_IO.Put_Line (CV.Version);\nend Main;\n",
        lambda out: "(GNAT " + out.strip().split(".")[0] + ")",
    ),
    "objc14": (
        "#import <Foundation/Foundation.h>\n#include <stdio.h>\n\nint main(void) {\n"
        "    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];\n"
        '    printf("%d\\n", __GNUC__);\n    [pool drain];\n    return 0;\n}\n',
        lambda out: f"(GCC {out.strip()}, GNUstep)",
    ),
    "cobol32": (
        "       IDENTIFICATION DIVISION.\n       PROGRAM-ID. MAIN.\n"
        '       PROCEDURE DIVISION.\n           DISPLAY "ok".\n           STOP RUN.\n',
        # "cobc (GnuCOBOL) 3.2.0"
        lambda out: "(GnuCOBOL "
        + ".".join(out.strip().splitlines()[-1].split()[-1].split(".")[:2])
        + ")",
        "cobc --version | head -n 1",
    ),
    "julia113": (
        'println(VERSION.major, ".", VERSION.minor)\n',
        lambda out: out.strip(),
    ),
    "caml53": (
        "let () =\n  match String.split_on_char '.' Sys.ocaml_version with\n"
        '  | major :: minor :: _ -> Printf.printf "%s.%s\\n" major minor\n'
        "  | _ -> print_endline Sys.ocaml_version\n",
        lambda out: f"(OCaml {out.strip()} toplevel)",
    ),
    "prolog92": (
        ":- initialization(main, main).\n\nmain :-\n"
        "    current_prolog_flag(version_data, swi(Major, Minor, _, _)),\n"
        '    format("~w.~w~n", [Major, Minor]).\n',
        lambda out: f"(SWI-Prolog {out.strip()})",
    ),
    "lua54": (
        'print(_VERSION:match("%d+%.%d+"))\n',
        lambda out: out.strip(),
    ),
    "powershell76": (
        'Write-Output ("{0}.{1}" -f $PSVersionTable.PSVersion.Major, $PSVersionTable.PSVersion.Minor)\n',
        lambda out: out.strip(),
    ),
    "lisp25": (
        '(format t "~a~%" (lisp-implementation-version))\n',
        # "2.5.2.debian"
        lambda out: "(SBCL " + ".".join(out.strip().split(".")[:2]) + ")",
    ),
    "pypy73": (
        'import sys\nprint("%d.%d" % sys.pypy_version_info[:2])\n',
        lambda out: out.strip(),
    ),
    "fsharp10": (
        'printfn "%d (.NET %d)" (typeof<option<int>>.Assembly.GetName().Version.Major)'
        " System.Environment.Version.Major\n",
        lambda out: out.strip(),
    ),
}

#: Keys every catalog entry must have. A missing one would otherwise surface
#: as a KeyError halfway through, after some languages were already reported.
FIELDS = ("code", "name", "version", "source_file", "compile", "run", "processes")


def declared_languages() -> list[dict[str, Any]]:
    """The catalog's LANGUAGES, read without importing Django."""
    tree = ast.parse(CATALOG.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        elif isinstance(node, ast.Assign):
            target, value = node.targets[0], node.value
        else:
            continue
        if isinstance(target, ast.Name) and target.id == "LANGUAGES" and value is not None:
            rows: list[dict[str, Any]] = ast.literal_eval(value)
            for row in rows:
                missing = [f for f in FIELDS if f not in row]
                if missing:
                    raise SystemExit(f"LANGUAGES yozuvida maydon yo'q ({', '.join(missing)}): {row!r}")
            return rows
    raise SystemExit(f"LANGUAGES topilmadi: {CATALOG}")


def probe_for(code: str) -> tuple[Any, ...]:
    if code in PROBES:
        return PROBES[code]
    raise SystemExit(f"'{code}' uchun probe yozilmagan — PROBES ga qo'shing")


def run_in_image(image: str, script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "run", "--rm", "--network=none", "--entrypoint", "sh", image, "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
    )


def main() -> int:
    image = sys.argv[1] if len(sys.argv) > 1 else "rankwant/judge-go:latest"
    failures: list[str] = []

    rows = declared_languages()
    for row in rows:
        code, name, version = row["code"], row["name"], row["version"]
        source, parse, *extra = probe_for(code)
        src = f"/box/{row['source_file']}"
        # `set -e`: a failed compile must fail the check, not fall through to a stale run.
        steps = ["set -e", f"mkdir -p /box && cd /box && cat > {src} <<'EOF'\n{source}EOF"]
        for cmd, redirect in ((row["compile"], " >&2"), (row["run"], "")):
            if cmd:
                rendered = [a.replace("{src}", src).replace("{bin}", "/box/prog") for a in cmd]
                # Quoted per argument: Go's compile is one `sh -c` string with spaces.
                # Compile output goes to stderr: ghc, fpc and dart report progress on
                # stdout, and only the program's own output is parsed.
                steps.append(shlex.join(rendered) + redirect)
        steps.extend(extra)
        proc = run_in_image(image, "\n".join(steps))

        if proc.returncode != 0:
            failures.append(f"{code}: ishga tushmadi\n{proc.stderr.strip()[:400]}")
            continue

        actual = parse(proc.stdout)  # type: ignore[operator]
        if actual != version:
            failures.append(
                f"{code} ({name}): e'lon qilingan {version!r}, image'da {actual!r} — "
                f"foydalanuvchiga noto'g'ri versiya ko'rsatiladi"
            )
        else:
            print(f"  {code:<12} {name} {version} ✓")

    if failures:
        print("\nMos kelmadi:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"\nTil matritsasi mos: {len(declared_languages())} til ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
