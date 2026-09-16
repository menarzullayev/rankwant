#!/usr/bin/env python3
"""`.env.example` must document every variable the stack actually reads.

Until 2026-09-17 there was no `.env.example`: `.env.public` (24 keys) was the
only record, `settings.py` read 62 variables, compose passed 26 of them, and a
fresh machine had to reverse-engineer the list. This checker keeps the
template honest:

1. every `${VAR}` in docker-compose*.yml is documented; one without a
   `:-default` must be an active `KEY=` line (the stack cannot start without it);
2. every variable read by settings.py, other API modules, the web app and the
   Go judge is documented (an active line or a `# KEY=` comment);
3. secret-looking keys carry no value in the template;
4. when a local `.env.public` exists, each of its keys is documented.

Exit codes: 0 clean, 1 a rule is broken, 2 a source could not be read.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / ".env.example"
SECRET = re.compile(r"(SECRET|TOKEN|PASSWORD|_API_KEY$|^DJANGO_SECRET_KEY$)")
IGNORED = {"NODE_ENV"}  # set by Node/Next itself


class Unreadable(Exception):
    pass


def read(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    except OSError as exc:
        raise Unreadable(f"{path.relative_to(ROOT)}: {exc}") from exc


def example_keys() -> tuple[dict[str, str], set[str]]:
    active: dict[str, str] = {}
    commented: set[str] = set()
    for line in read(EXAMPLE).splitlines():
        if m := re.match(r"^([A-Z][A-Z0-9_]*)=(.*)$", line):
            active[m.group(1)] = m.group(2).strip()
        elif m := re.match(r"^#\s*([A-Z][A-Z0-9_]*)=", line):
            commented.add(m.group(1))
    return active, commented


def compose_vars() -> dict[str, bool]:
    """Variable -> True when compose gives it no default."""
    found: dict[str, bool] = {}
    files = sorted(ROOT.glob("docker-compose*.yml"))
    if not files:
        raise Unreadable("docker-compose*.yml topilmadi")
    for path in files:
        for m in re.finditer(r"\$\{([A-Z][A-Z0-9_]*)(:?-[^}]*)?\}", read(path)):
            required = m.group(2) is None
            found[m.group(1)] = found.get(m.group(1), False) or required
    return found


def code_vars() -> set[str]:
    names: set[str] = set()
    settings = read(ROOT / "apps/api/config/settings.py")
    names |= set(re.findall(r'\b(?:env|env_bool)\(\s*"([A-Z][A-Z0-9_]*)"', settings))
    for path in sorted((ROOT / "apps/api").rglob("*.py")):
        if "tests" in path.parts or ".venv" in path.parts:
            continue
        names |= set(re.findall(r'os\.(?:environ\.get|getenv)\(\s*"([A-Z][A-Z0-9_]*)"', read(path)))
    for path in sorted((ROOT / "apps/web/src").rglob("*.ts*")):
        names |= set(re.findall(r"process\.env\.([A-Z][A-Z0-9_]*)", read(path)))
    for path in sorted((ROOT / "services").rglob("*.go")):
        names |= set(re.findall(r'os\.Getenv\("([A-Z][A-Z0-9_]*)"\)', read(path)))
    return names - IGNORED


def main() -> int:
    try:
        active, commented = example_keys()
        documented = set(active) | commented
        problems: list[str] = []
        for name, required in sorted(compose_vars().items()):
            if name not in documented:
                problems.append(f"compose `${{{name}}}` .env.example da yo'q")
            elif required and name not in active:
                problems.append(f"compose `${{{name}}}` standartsiz — faol `{name}=` qatori kerak")
        for name in sorted(code_vars() - documented):
            problems.append(f"kod `{name}` ni o'qiydi, .env.example da hujjatlanmagan")
        for name, value in sorted(active.items()):
            if SECRET.search(name) and value:
                problems.append(f"`{name}` sirli kalit — shablonda qiymat bo'lmasligi kerak")
        local = ROOT / ".env.public"
        if local.exists():
            keys = re.findall(r"^([A-Z][A-Z0-9_]*)=", read(local), re.M)
            for name in sorted(set(keys) - documented):
                problems.append(f".env.public dagi `{name}` .env.example da hujjatlanmagan")
            scope = f"+ lokal .env.public ({len(set(keys))} kalit)"
        else:
            scope = "(lokal .env.public yo'q — faqat kod va compose)"
    except Unreadable as exc:
        print(f"✗ Manbani o'qib bo'lmadi — {exc}")
        return 2
    if problems:
        print(f"✗ .env.example: {len(problems)} ta muammo:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"✓ .env.example to'liq: {len(documented)} o'zgaruvchi hujjatlangan {scope}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
