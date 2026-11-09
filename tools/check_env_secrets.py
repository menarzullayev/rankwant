#!/usr/bin/env python3
"""Refuse a public-stack env file whose secrets are missing, known or weak.

The base compose file falls back to `dev`, `devdevdev` and `judge-ro-dev`
so a local or CI stack starts without an env file. Those values live in a
public repository, so the public stack must never run on them (ADR-0044).
`docker-compose.public.yml` already refuses an EMPTY value (`${VAR:?}`),
but compose cannot compare values, so a copied default passed silently:
measured 2026-11-10, production ran on all three defaults until they were
rotated that day.

The known defaults are read from `docker-compose.yml` itself
(`${NAME:-default}`), so a new fallback added there is refused here
without editing this file.

Usage:  check_env_secrets.py <env-file>
Exit:   0 every secret is set, unknown and long enough
        1 a secret is missing, a known default or too short
        2 the env file (or docker-compose.yml) could not be read

Values are never printed — only the key and the reason.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import _console

# Without this the `✓` crashes under a pipe on Windows and the deploy
# preflight reads the crash as a refusal (exit 1) on a healthy env file.
_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent

#: Secrets the public stack reads from the env file.
SECRETS = ("POSTGRES_PASSWORD", "MINIO_ROOT_PASSWORD", "JUDGE_S3_SECRET")

#: Shorter than this is refused even when the value is not a known default.
MIN_LENGTH = 16

#: Values refused regardless of what the compose file says.
ALWAYS_REFUSED = {"", "dev", "devdevdev", "judge-ro-dev", "postgres", "password", "changeme", "minioadmin"}


def compose_defaults(compose: str) -> set[str]:
    """Every `${NAME:-default}` fallback the base compose file gives a secret."""
    found: set[str] = set()
    for name in SECRETS:
        for match in re.finditer(r"\$\{" + name + r":-([^}]*)\}", compose):
            found.add(match.group(1))
    return found


def parse_env(text: str) -> dict[str, str]:
    """Last assignment wins, as in `docker compose --env-file`."""
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def problems(env: dict[str, str], refused: set[str]) -> list[str]:
    found = []
    for name in SECRETS:
        if name not in env:
            found.append(f"{name}: yo'q")
        elif env[name] in refused:
            found.append(f"{name}: ochiq repodagi standart qiymat")
        elif len(env[name]) < MIN_LENGTH:
            found.append(f"{name}: {MIN_LENGTH} belgidan qisqa")
    return found


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("ishlatish: check_env_secrets.py <env-file>", file=sys.stderr)
        return 2
    try:
        text = Path(argv[1]).read_text(encoding="utf-8")
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    except OSError as exc:
        print(f"✗ o'qilmadi: {exc.filename}", file=sys.stderr)
        return 2
    refused = ALWAYS_REFUSED | compose_defaults(compose)
    found = problems(parse_env(text), refused)
    if found:
        for line in found:
            print(f"✗ {line}")
        print("  Yangi qiymat: docs/10-operations/runbooks/secrets-rotation.md")
        return 1
    print(f"✓ {len(SECRETS)} ta sir o'rnatilgan, standart emas, kamida {MIN_LENGTH} belgi")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
