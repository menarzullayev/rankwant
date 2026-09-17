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
PROBES = {
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


def probe_for(code: str) -> tuple[str, object]:
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
        source, parse = probe_for(code)
        src = row["source_file"]
        steps = [f"mkdir -p /box && cd /box && cat > {src} <<'EOF'\n{source}EOF"]
        for cmd in (row["compile"], row["run"]):
            if cmd:
                rendered = [a.replace("{src}", src).replace("{bin}", "/box/prog") for a in cmd]
                steps.append(" ".join(rendered))
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
            print(f"  {code:<8} {name} {version} ✓")

    if failures:
        print("\nMos kelmadi:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"\nTil matritsasi mos: {len(declared_languages())} til ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
