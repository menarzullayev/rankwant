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

#: ADR-0028 (A-2): the MinIO ROOT password must never be a judge env VALUE.
#: The judge still carries an `S3_SECRET` key — the scoped `judge-ro` user —
#: so the guard is on the value, not the key.
ROOT_SECRET_VALUE = "devdevdev"

#: Every published port must be bound here. The Cloudflare Tunnel is the only
#: way in; a host-wide binding would bypass the tunnel and the edge rules.
LOOPBACK = "127.0.0.1"

#: Services that must publish nothing at all once the chain is merged.
#: `judge-queue` (ADR-0028) — a Redis; `minio-init` is one-shot and dies.
INTERNAL_ONLY = ("judge", "postgres", "redis", "minio", "judge-queue", "minio-init")

# ── ADR-0028: the network layer ──────────────────────────────────────
#: The judge sits alone on an `internal: true` network — no route out, no
#: route to the database network. Parsed from the BASE compose file: the
#: public overlay deletes ports, it does not touch networks.
NETWORK_FILE = "docker-compose.yml"

#: The judge must be on EXACTLY this network, nothing else. A missing
#: `networks:` key means the implicit `default` — the very topology A-1
#: measured on 2026-09-24 (judge → postgres:5432 OPEN).
JUDGE_NET = "judge-net"

#: Both networks: the judge reaches them, so does everyone else. Postgres
#: must NEVER appear here — that would reopen the A-1 path this guards.
BOTH_NETWORKS = ("minio", "judge-queue")

#: Default-network-only services: if one of them joins `judge-net`, the
#: judge can reach it (postgres included). Checked in the merged chain.
DEFAULT_ONLY = ("postgres", "api", "worker", "beat", "web", "migrate")

#: Developer tools live in their own overlay so the deploy chain stays exactly
#: what `docs/06` describes. They must still be declared and loopback-only:
#: `adminer` ran for a day with `Config.Labels == {}`, outside every compose
#: file, and nothing in this repository could see it. A file nothing measures
#: is how that happens — so this file is measured here too.
TOOLS_FILE = "docker-compose.tools.yml"

#: The tools overlay must declare these. Deleting the file, or the service,
#: puts them back outside every check — the original bug.
TOOLS_SERVICES = ("adminer",)

# `minio:` carries a trailing comment (`# S3/R2 o'rniga local`) — a service key
# regex that only allows trailing whitespace silently merged the `redis` and
# `minio` blocks, and the run stopped with exit 2 rather than guessing.
_SERVICE = re.compile(r"^  ([A-Za-z0-9_-]+):\s*(?:#.*)?$")
_PORTS = re.compile(r"^    ports:\s*(.+?)\s*$")
_NETWORKS = re.compile(r"^    networks:\s*(.+?)\s*$")
_ENV = re.compile(r"^    environment:\s*$")
_ENV_KEY = re.compile(r"^      ([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")
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


def _networks(block: str) -> list[str] | None:
    """The `networks:` inline list of one service, or None when undeclared.

    None is meaningful: compose attaches the service to `default`, which is
    exactly what the judge must NOT fall back to silently. An indented
    mapping form (`judge-net:` with sub-keys) or a block list is an unknown
    shape for this parser — it raises, like `_published`, because a network
    boundary this checker cannot read must stop the run, not pass it.
    """
    found = [m.group(1) for line in block.splitlines() if (m := _NETWORKS.match(line))]
    if not found:
        return None
    if len(found) > 1:
        raise ValueError(f"`networks:` declared twice in one service: {found!r}")
    raw = found[0]
    if not (raw.startswith("[") and raw.endswith("]")):
        raise ValueError(f"`networks:` is not an inline list: {raw!r}")
    body = raw[1:-1]
    if not body.strip():
        raise ValueError(f"`networks:` empty list: {raw!r}")
    # Quoted and bare items both occur (`[default, judge-net]`):
    # `_QUOTED` sees only the quoted ones and would report an empty
    # boundary — split on commas and strip quotes instead.
    names = [item.strip().strip("'") for item in body.split(",") if item.strip()]
    if not names:
        raise ValueError(f"`networks:` unparsable items: {raw!r}")
    return names


def _env_keys(block: str) -> set[str]:
    """Environment keys of one service — mapping and `- KEY=value` list forms."""
    return {k for k, _ in _env_pairs(block)}


def _env_values(block: str) -> set[str]:
    """Environment VALUES of one service's mapping form (`KEY: value`)."""
    return {v for _, v in _env_pairs(block) if v}


def _env_pairs(block: str) -> set[tuple[str, str]]:
    """(key, value) pairs of one service — mapping and `- KEY=value` forms.

    Value is the empty string for list-form entries whose value carries no
    `=`, and for mapping entries that only declare a key — that is enough
    for both callers: keys ignore it, values skip it.
    """
    lines = block.splitlines()
    start = next((i for i, line in enumerate(lines) if _ENV.match(line)), None)
    if start is None:
        return set()
    pairs: set[tuple[str, str]] = set()
    for line in lines[start + 1 :]:
        if not line.startswith("      ") and line.strip():
            break
        if (m := _ENV_KEY.match(line)) and not line.lstrip().startswith("-"):
            pairs.add((m.group(1), m.group(2).strip().strip("'\"")))
            continue
        if (m := _ENV_PAIR.match(line)) and line.lstrip().startswith("-"):
            pairs.add((m.group(1), line.split("=", 1)[1].strip().strip("'\"")))
    return pairs


def _mapping(raw: str) -> str | None:
    """`127.0.0.1:8301:8000` → `127.0.0.1`; `5432:5432` → None."""
    parts = raw.split(":")
    # A loopback mapping has three parts; `3000:3000` has two and binds wide.
    if len(parts) >= 3 and parts[0] == LOOPBACK:
        return parts[0]
    return None


def main() -> int:
    problems: list[str] = []
    tools: dict[str, list[str]] = {}
    try:
        files = {name: (ROOT / name).read_text(encoding="utf-8") for name in CHAIN}
        merged: dict[str, list[str]] = {}
        for name in CHAIN:
            for service, block in _services(files[name]).items():
                if _declares_ports(block) or service not in merged:
                    merged[service] = _published(block)
        tools_path = ROOT / TOOLS_FILE
        if tools_path.exists():
            for service, block in _services(tools_path.read_text(encoding="utf-8")).items():
                tools[service] = _published(block)
        else:
            problems.append(f"{TOOLS_FILE} yo'q — vositalar yana e'lon qilinmagan")
    except (OSError, ValueError) as exc:
        print(f"  ✗ chegara o'qilmadi — o'lchov yo'q: {exc}")
        return 2

    for service in INTERNAL_ONLY:
        if service not in merged:
            problems.append(f"{service} servisi zanjirda yo'q")
        elif merged[service]:
            problems.append(f"{service} port nashr etadi: {merged[service]}")
    for service, ports in sorted(merged.items()):
        for raw in ports:
            if _mapping(raw) is None:
                problems.append(f"{service} loopback'da emas: {raw}")

    # Ishlab chiquvchi vositalari: deploy zanjirida EMAS, lekin e'lon qilingan
    # va shu yerda o'lchanadi. Uchta shart — zanjirda takrorlanmasin, porti
    # loopback bo'lsin, va fayl uni haqiqatan e'lon qilsin.
    for service, ports in sorted(tools.items()):
        if service in merged:
            problems.append(
                f"{service} ham {TOOLS_FILE}, ham deploy zanjirida — "
                "ishlab chiquvchi vositasi ishlab chiqarish chegarasida"
            )
        if not ports:
            problems.append(f"{TOOLS_FILE}: {service} port e'lon qilmaydi — ko'rinmas")
        for raw in ports:
            if _mapping(raw) is None:
                problems.append(f"{TOOLS_FILE}: {service} loopback'da emas: {raw}")
    for service in TOOLS_SERVICES:
        if service not in tools:
            problems.append(f"{TOOLS_FILE}: {service} e'lon qilinmagan — nazoratsiz qoladi")

    judge = _services(files[CHAIN[0]]).get("judge", "")
    for key in FORBIDDEN_JUDGE_ENV:
        if key in _env_keys(judge):
            problems.append(f"judge servisiga {key} berilgan")

    # ── ADR-0028: tarmoq qatlami ─────────────────────────────────────
    # Portlar deploy zanjiridan, tarmoqlar esa baza fayldan o'qiladi:
    # overlay tarmoqni o'zgartirmaydi. Asosiy invariya — judge FAQAT
    # `judge-net`da (default = A-1 o'lchangan topologiya, 2026-09-24).
    try:
        net_services = _services(files[NETWORK_FILE])
        judge_nets = _networks(net_services.get("judge", ""))
        if judge_nets != [JUDGE_NET]:
            problems.append(
                f"judge faqat `{JUDGE_NET}` tarmog'ida bo'lishi kerak, "
                f"hozir: {judge_nets or 'default (implicit)'}"
            )
        for name in BOTH_NETWORKS:
            nets = _networks(net_services.get(name, ""))
            if nets is None or set(nets) != {"default", JUDGE_NET}:
                problems.append(
                    f"{name} ikkala tarmoqda bo'lishi kerak "
                    f"(default + {JUDGE_NET}), hozir: {nets or 'default (implicit)'}"
                )
        for name in DEFAULT_ONLY:
            nets = _networks(net_services.get(name, ""))
            if nets is not None and JUDGE_NET in nets:
                problems.append(
                    f"{name} `{JUDGE_NET}` tarmog'ida — postgres yo'li ochiladi!"
                )
        # `internal: true` — judge'dan internetga egress yopilishi sharti.
        raw = files[NETWORK_FILE]
        m = re.search(r"^  judge-net:\s*$\n\s+internal:\s*true\s*$", raw, re.M)
        if not m:
            problems.append("`judge-net` tarmog'i `internal: true` emas")
        # Judge KALITI bo'lishi shart (`judge-ro` useri) — taqiqlangan
        # narsa ROOT QIYMATI (A-2, ADR-0028; `check_compose.py` bilan bir
        # qoida, ikki haqiqat manbasi emas — bitta qiymat, ikki qatlam).
        if ROOT_SECRET_VALUE in _env_values(judge):
            problems.append(
                "judge env'da root MinIO paroli bor (A-2, ADR-0028) — "
                "faqat `judge-ro` useri bo'lishi kerak"
            )
    except ValueError as exc:
        print(f"  ✗ tarmoq qatlami o'qilmadi: {exc}")
        return 2

    published = {s: p for s, p in sorted(merged.items()) if p}
    print(f"  chegara: {len(published)} nashr etilgan port")
    for service, ports in published.items():
        print(f"    {service:10} {', '.join(ports)}")
    if all(not merged.get(s) for s in INTERNAL_ONLY):
        print(f"  ✓ {', '.join(INTERNAL_ONLY)} — nashr etilgan port yo'q")
    if tools:
        print(f"  {TOOLS_FILE} — deploy zanjiridan tashqari:")
        for service, ports in sorted(tools.items()):
            print(f"    {service:10} {', '.join(ports) or '—'}")
    for problem in problems:
        print(f"  ✗ {problem}")
    if problems:
        return 1
    print(f"  ✓ hammasi {LOOPBACK} da; tashqi yo'l — Cloudflare Tunnel")
    return 0


if __name__ == "__main__":
    sys.exit(main())
