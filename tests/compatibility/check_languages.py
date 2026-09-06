"""Til matritsasi: e'lon qilingan versiya judge image'idagi haqiqat bilan mos kelishini tekshiradi.

Nega kerak: platforma foydalanuvchiga "Python 3.12" deb ko'rsatsa, judge esa
3.11 ishlatsa, 3.12 sintaksisi tushunarsiz SyntaxError bilan yiqiladi va
foydalanuvchi buni o'z kodidan deb o'ylaydi. Buni faqat har tilda o'z
versiyasini chop etadigan dastur ishga tushirib bilib bo'ladi.

Ishlatish:  python3 check_languages.py [image]
"""

from __future__ import annotations

import ast
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
SEED = REPO / "apps/api/core/management/commands/seed_demo.py"

#: Har til o'z runtime versiyasini chop etadi — e'londan mustaqil manba.
PROBES = {
    "cpp": (
        "main.cpp",
        '#include <cstdio>\nint main(){printf("%ld\\n", __cplusplus);return 0;}\n',
        lambda out: {"202302": "23", "202100": "2b", "201703": "17", "201402": "14"}.get(
            out.strip().rstrip("L")[:6], out.strip()
        ),
    ),
    "py": (
        "main.py",
        "import sys\nprint('%d.%d' % sys.version_info[:2])\n",
        lambda out: out.strip(),
    ),
    "java": (
        "Main.java",
        'public class Main{public static void main(String[] a){'
        'System.out.println(System.getProperty("java.version").split("\\\\.")[0]);}}\n',
        lambda out: out.strip(),
    ),
}


def declared_languages() -> list[tuple[str, str, str, list[str], list[str]]]:
    """seed_demo dagi LANGUAGES — Django import qilmasdan o'qiydi."""
    tree = ast.parse(SEED.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == "LANGUAGES":  # type: ignore[attr-defined]
            return ast.literal_eval(node.value)
    raise SystemExit(f"LANGUAGES topilmadi: {SEED}")


def probe_for(code: str) -> tuple[str, str, object]:
    for prefix, probe in PROBES.items():
        if code.startswith(prefix):
            return probe
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

    for code, name, version, compile_cmd, run_cmd in declared_languages():
        src, source, parse = probe_for(code)
        steps = [f"mkdir -p /box && cd /box && cat > {src} <<'EOF'\n{source}EOF"]
        for cmd in (compile_cmd, run_cmd):
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
