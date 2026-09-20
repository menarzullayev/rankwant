#!/usr/bin/env python3
"""The deployed boundary, derived from the compose chain the deploy uses.

`tools/deploy.sh` runs

    docker compose -p rankwant --env-file .env.public \\
      -f docker-compose.yml -f docker-compose.public.yml ...

The overlay uses `ports: !reset []` to **delete** a published port and
`ports: !override [...]` to replace it. Reading `docker-compose.yml` alone
therefore says MinIO is published on `9000:9000` — it is not. Measured
2026-09-21: `curl 127.0.0.1:9000/minio/health/live` → `HTTP 000`, and
`docker ps` shows `9000/tcp` with no host mapping. A conclusion drawn from the
base file alone was wrong once already; this script exists so it cannot be
wrong quietly.

Stdlib only — this runs in CI's `Docs and contract integrity` job, which
installs nothing. The parse is cross-checked against the engine itself:
`docker compose -p rankwant -f docker-compose.yml -f docker-compose.public.yml
config` resolves to exactly two published ports, both `127.0.0.1` (measured
2026-09-21, same day).

Exit codes: 0 the boundary holds, 1 a rule is violated, 2 a file could not be
parsed — never treated as "fine".
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent

#: The chain the deploy uses, in order. The overlay is last and wins.
CHAIN = ("docker-compose.yml", "docker-compose.public.yml")

#: docs/06 § Xavfsizlik chegarasi (locked 2026-09-06): the judge host holds no
#: DB credential. Parsed as KEYS, not searched as text — the judge block
#: carries a comment explaining why `DATABASE_URL` is absent, so a substring
#: search would report the opposite of the truth.
FORBIDDEN_JUDGE_ENV = ("DATABASE_URL", "DJANGO_SECRET_KEY", "POSTGRES_PASSWORD")

#: Every published port must be bound here. The Cloudflare Tunnel is the only
#: way in; a host-wide binding would bypass the tunnel and the edge rules.
LOOPBACK = "127.0.0.1"

#: Services that must publish nothing at all once the chain is merged.
INTERNAL_ONLY = ("judge", "postgres", "redis", "minio")

# `minio:` carries a trailing comment (`# S3/R2 o'rniga local`) — a service key
# regex that only allows trailing whitespace silently merged the `redis` and
# `minio` blocks, and the run stopped with exit 2 rather than guessing.
_SERVICE = re.compile(r"^  ([A-Za-z0-9_-]+):\s*(?:#.*)?$")
_PORTS = re.compile(r"^    ports:\s*(.+?)\s*$")
_ENV = re.compile(r"^    environment:\s*$")
_ENV_KEY = re.compile(r"^      ([A-Za-z_][A-Za-z0-9_]*):")
_ENV_PAIR = re.compile(r"^\s*-?\s*([A-Za-z_][A-Za-z0-9_]*)=")
_QUOTED = re.compile(r"'([^']*)'|\"([^\"]*)\"")


def _services(text: str) -> dict[str, str]:
    """Split the `services:` block into name → block text."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.rstrip() == "services:"), None)
    if start is None:
        raise ValueError("no top-level `services:` key")
    out: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines[start + 1 :]:
        if line and not line.startswith(" "):
            break  # next top-level key ends the block
        match = _SERVICE.match(line)
        if match:
            current = match.group(1)
            out[current] = []
            continue
        if current is not None:
            out[current].append(line)
    return {name: "\n".join(body) for name, body in out.items()}


def _published(block: str) -> list[str]:
    """The `ports:` mappings of one service, or `[]` when it declares none.

    Raises `ValueError` on a form this parser does not understand — an
    unreadable boundary must stop the run, not pass it.
    """
    found = [m.group(1) for line in block.splitlines() if (m := _PORTS.match(line))]
    if not found:
        return []
    if len(found) > 1:
        raise ValueError(f"`ports:` declared twice in one service: {found!r}")
    raw = found[0]
    # `!reset []` deletes what the earlier file published; `!override [...]`
    # replaces it. Both are Compose extensions, not YAML we can trust blindly.
    if raw.startswith("!reset"):
        rest = raw[len("!reset") :].strip()
        if rest != "[]":
            raise ValueError(f"`!reset` with a non-empty list: {raw!r}")
        return []
    body = raw[len("!override") :].strip() if raw.startswith("!override") else raw
    if not (body.startswith("[") and body.endswith("]")):
        raise ValueError(f"`ports:` is not an inline list: {raw!r}")
    return [a or b for a, b in _QUOTED.findall(body)]


def _declares_ports(block: str) -> bool:
    """Whether the block has a `ports:` key at all — `!reset []` counts.

    Per line, not `re.search(block)`: the pattern is anchored, and without
    `re.MULTILINE` a search over the joined block matches only at offset 0.
    That mistake made the overlay's `!reset []` invisible, so the base file's
    `5432:5432` survived the merge and the check reported the opposite of the
    truth — with a green-looking table.
    """
    return any(_PORTS.match(line) for line in block.splitlines())


def _env_keys(block: str) -> set[str]:
    """Environment keys of one service — mapping and `- KEY=value` list forms."""
    lines = block.splitlines()
    start = next((i for i, line in enumerate(lines) if _ENV.match(line)), None)
    if start is None:
        return set()
    keys: set[str] = set()
    for line in lines[start + 1 :]:
        if not line.startswith("      ") and line.strip():
            break
        if (m := _ENV_KEY.match(line)) and not line.lstrip().startswith("-"):
            keys.add(m.group(1))
            continue
        if (m := _ENV_PAIR.match(line)) and line.lstrip().startswith("-"):
            keys.add(m.group(1))
    return keys


def _mapping(raw: str) -> str | None:
    """`127.0.0.1:8301:8000` → `127.0.0.1`; `5432:5432` → None."""
    parts = raw.split(":")
    # A loopback mapping has three parts; `3000:3000` has two and binds wide.
    if len(parts) >= 3 and parts[0] == LOOPBACK:
        return parts[0]
    return None


def main() -> int:
    try:
        files = {name: (ROOT / name).read_text(encoding="utf-8") for name in CHAIN}
        merged: dict[str, list[str]] = {}
        for name in CHAIN:
            for service, block in _services(files[name]).items():
                if _declares_ports(block) or service not in merged:
                    merged[service] = _published(block)
    except (OSError, ValueError) as exc:
        print(f"  ✗ chegara o'qilmadi — o'lchov yo'q: {exc}")
        return 2

    problems: list[str] = []
    for service in INTERNAL_ONLY:
        if service not in merged:
            problems.append(f"{service} servisi zanjirda yo'q")
        elif merged[service]:
            problems.append(f"{service} port nashr etadi: {merged[service]}")
    for service, ports in sorted(merged.items()):
        for raw in ports:
            if _mapping(raw) is None:
                problems.append(f"{service} loopback'da emas: {raw}")

    judge = _services(files[CHAIN[0]]).get("judge", "")
    for key in FORBIDDEN_JUDGE_ENV:
        if key in _env_keys(judge):
            problems.append(f"judge servisiga {key} berilgan")

    published = {s: p for s, p in sorted(merged.items()) if p}
    print(f"  chegara: {len(published)} nashr etilgan port")
    for service, ports in published.items():
        print(f"    {service:10} {', '.join(ports)}")
    if all(not merged.get(s) for s in INTERNAL_ONLY):
        print(f"  ✓ {', '.join(INTERNAL_ONLY)} — nashr etilgan port yo'q")
    for problem in problems:
        print(f"  ✗ {problem}")
    if problems:
        return 1
    print(f"  ✓ hammasi {LOOPBACK} da; tashqi yo'l — Cloudflare Tunnel")
    return 0


if __name__ == "__main__":
    sys.exit(main())
