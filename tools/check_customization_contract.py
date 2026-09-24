#!/usr/bin/env python3
"""Keep the customization contract and the code in step.

Why this exists. On 2026-09-24 the same defect landed twice in this area:
`themeToggle` reached the client in #244 but never reached the server's accepted
key set, so picking a theme-toggle style made the whole `appearance` write
`400` — the device showed the change, the account never got it. The guard that
should have caught it (`apps/api/tests/test_prefs.py`) had a hand-written key
list that had gone stale, so it passed.

Rules scattered across code comments and ADRs do not stop that. A contract that
is checked against the code does:

  1. every key the client writes must be accepted by the server;
  2. the full-customizer-write test must list every key the client writes —
     a hand-written list is the point, so it must be kept complete;
  3. the contract must list every accepted appearance key;
  4. the contract's declared constants must equal the ones in `prefs.py`;
  5. the agent invariants must be present in `CLAUDE.md`, where agents read them.

Exit code: 0 — clean, 1 — contract and code disagree, 2 — a pattern could not
be found, so nothing was measured.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Windows writes the pipe as `cp1252` and dies on the first `✓`; the reason and
# the measurement live in `tools/_console.py`.
import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent
PREFS = ROOT / "apps/api/core/prefs.py"
CLIENT_TYPE = ROOT / "apps/web/src/features/account/api/account.ts"
APPLY = ROOT / "apps/web/src/lib/theme/apply.ts"
TEST = ROOT / "apps/api/tests/test_prefs.py"
CONTRACT = ROOT / "docs/08-technical-spec/customization-contract.md"
CLAUDE = ROOT / "CLAUDE.md"

#: The invariants that must exist in CLAUDE.md. Matched as substrings of the
#: contract's §7 wording, so a reworded invariant fails loudly instead of
#: silently disappearing.
INVARIANTS = (
    "MUST NOT introduce a new customization setting",
    "MUST NOT add a key to the client",
    "MUST NOT change the precedence of an existing setting",
    "MUST NOT introduce a second persistence mechanism",
    "MUST NOT bypass customization validation",
    "Unknown values MUST have an explicit fallback",
)


class Unmeasured(Exception):
    """A pattern was not found — report it instead of passing."""


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise Unmeasured(f"{path.relative_to(ROOT)}: {exc}") from exc


def literal_tuple(text: str, name: str) -> list[str]:
    """Read `NAME = ("a", "b")` out of a Python module."""
    match = re.search(rf"^{name} = \(([^)]*)\)", text, re.M)
    if match is None:
        raise Unmeasured(f"prefs.py: `{name}` topilmadi")
    return re.findall(r'"([^"]+)"', match.group(1))


def py_constants(text: str) -> dict[str, float]:
    """Flat numeric constants: `NAME = 5` and `A, B, C = 1, 2, 3`.

    Both shapes are used in `prefs.py` — `SIZE_MIN, SIZE_MAX, SIZE_STEP = 75,
    150, 5` is one statement — so a `^NAME = ` search alone would miss two
    thirds of the bounds.
    """
    out: dict[str, float] = {}
    for line in text.splitlines():
        if line[:1].isspace() or "=" not in line:
            continue
        lhs, _, rhs = line.partition("=")
        rhs = rhs.split("#")[0]
        names = [name.strip() for name in lhs.split(",")]
        values = re.findall(r"-?\d+(?:\.\d+)?", rhs)
        if not names or len(names) != len(values):
            continue
        for name, value in zip(names, values):
            if re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
                out[name] = float(value)
    return out


def need(consts: dict[str, float], name: str) -> float:
    if name not in consts:
        raise Unmeasured(f"prefs.py: `{name}` topilmadi")
    return consts[name]


def appearance_keys_from_prefs(text: str) -> set[str]:
    """`APPEARANCE_KEYS` — the literal members plus everything in `CATALOG_KEYS`."""
    match = re.search(r"^APPEARANCE_KEYS = \{(.*?)^\}", text, re.M | re.S)
    if match is None:
        raise Unmeasured("prefs.py: `APPEARANCE_KEYS` topilmadi")
    body = match.group(1)
    keys = set(re.findall(r'"([^"]+)"', body))
    if "*CATALOG_KEYS" in body:
        keys |= set(literal_tuple(text, "CATALOG_KEYS"))
    return keys


def client_written_keys(text: str) -> set[str]:
    """Keys `apply.ts` reads off `appearance` — i.e. what the DOM layer needs."""
    keys = set(re.findall(r"appearance\.([a-zA-Z]+)", text))
    if not keys:
        raise Unmeasured("apply.ts: `appearance.<key>` topilmadi")
    return keys


def client_type_keys(text: str) -> set[str]:
    """Field names of the hand-written `AppearancePrefs` type."""
    match = re.search(r"export type AppearancePrefs = \{(.*?)^\};", text, re.M | re.S)
    if match is None:
        raise Unmeasured("account.ts: `AppearancePrefs` topilmadi")
    keys = set(re.findall(r"^\s{2}([a-zA-Z]+)\??:", match.group(1), re.M))
    if not keys:
        raise Unmeasured("account.ts: `AppearancePrefs` da maydon topilmadi")
    return keys


def test_listed_keys(text: str) -> set[str]:
    """The key list inside `test_customizer_yozuvi_toliq_qabul_qilinadi`."""
    match = re.search(
        r"def test_customizer_yozuvi_toliq_qabul_qilinadi.*?\n        appearance = \{(.*?)\n        \}",
        text,
        re.S,
    )
    if match is None:
        raise Unmeasured("test_prefs.py: `test_customizer_yozuvi_toliq_qabul_qilinadi` topilmadi")
    keys = set(re.findall(r'"([a-zA-Z]+)":', match.group(1)))
    if not keys:
        raise Unmeasured("test_prefs.py: test ro'yxatida kalit topilmadi")
    return keys


def contract_listed_keys(text: str) -> set[str]:
    """First backticked cell of every table row — the contract's key tables."""
    keys: set[str] = set()
    for line in text.splitlines():
        if line.startswith("| `"):
            first = re.match(r"\| `([a-zA-Z]+)`", line)
            if first:
                keys.add(first.group(1))
    if not keys:
        raise Unmeasured("contract: jadval qatorlaridan kalit topilmadi")
    return keys


def contract_constants(text: str) -> dict[str, str]:
    match = re.search(r"<!-- contract-constants -->\s*```contract\n(.*?)```", text, re.S)
    if match is None:
        raise Unmeasured("contract: `contract-constants` bloki topilmadi")
    out: dict[str, str] = {}
    for line in match.group(1).strip().splitlines():
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def numbers(value: str) -> list[float]:
    return [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", value)]


def main() -> int:
    problems: list[str] = []
    try:
        prefs = read(PREFS)
        accepted = appearance_keys_from_prefs(prefs)
        written = client_written_keys(read(APPLY))
        declared = client_type_keys(read(CLIENT_TYPE))
        tested = test_listed_keys(read(TEST))
        contract = read(CONTRACT)
        listed = contract_listed_keys(contract)
        constants = contract_constants(contract)
        claude = read(CLAUDE)
    except Unmeasured as exc:
        print(f"✗ O'lchab bo'lmadi — {exc}")
        return 2

    # 1. What the client writes must be accepted by the server. This is the rule
    #    whose absence cost us the themeToggle defect.
    for label, keys in (("apply.ts", written), ("AppearancePrefs", declared)):
        missing = sorted(keys - accepted)
        if missing:
            problems.append(
                f"{label} yozadigan kalitlar serverda yo'q: {missing} — "
                "`prefs.py` ning `APPEARANCE_KEYS`/`CATALOG_KEYS` iga qo'shing, "
                "aks holda BUTUN `appearance` yozuvi 400 bo'ladi"
            )

    # 2. The hand-written test list must cover what the client writes. It is
    #    hand-written on purpose (deriving it from the server would be a
    #    tautology), so completeness has to be checked here.
    stale = sorted((written | declared) - tested)
    if stale:
        problems.append(
            f"`test_customizer_yozuvi_toliq_qabul_qilinadi` ro'yxati eskirgan — "
            f"yetishmaydi: {stale}"
        )

    # 3. The contract must list every accepted key.
    undocumented = sorted(accepted - listed)
    if undocumented:
        problems.append(f"contract jadvalida yo'q kalitlar: {undocumented}")

    # 4. Declared constants must equal the code.
    consts = py_constants(prefs)
    checks = (
        ("schema_version", [need(consts, "SCHEMA_VERSION")]),
        (
            "size",
            [need(consts, "SIZE_MIN"), need(consts, "SIZE_MAX"), need(consts, "SIZE_STEP")],
        ),
        ("scale", [need(consts, "SCALE_MIN"), need(consts, "SCALE_MAX")]),
        ("template_max", [need(consts, "TEMPLATE_MAX")]),
        ("template_name_max", [need(consts, "TEMPLATE_NAME_MAX")]),
    )
    for key, expected in checks:
        if key not in constants:
            problems.append(f"contract: `{key}` doimiysi e'lon qilinmagan")
        elif numbers(constants[key]) != expected:
            problems.append(
                f"contract: `{key}` = {constants[key]!r}, kodda esa {expected} — hujjat eskirdi"
            )

    for key, tuple_name in (
        ("fonts", "FONTS"),
        ("densities", "DENSITIES"),
        ("visions", "VISIONS"),
        ("motions", "MOTIONS"),
        ("effects", "EFFECTS"),
    ):
        expected = literal_tuple(prefs, tuple_name)
        if key not in constants:
            problems.append(f"contract: `{key}` ro'yxati e'lon qilinmagan")
        elif constants[key].split() != expected:
            problems.append(f"contract: `{key}` = {constants[key]!r}, kodda esa {expected}")

    # 5. The invariants must be where agents read them.
    for invariant in INVARIANTS:
        if invariant not in contract:
            problems.append(f"contract: invariant yo'q — {invariant!r}")
        if invariant not in claude:
            problems.append(f"CLAUDE.md: invariant yo'q — {invariant!r}")

    if problems:
        print(f"✗ Customization contract: {len(problems)} ta nomuvofiqlik")
        for problem in problems:
            print(f"  - {problem}")
        print(
            "\nTuzatish: `docs/08-technical-spec/customization-contract.md` va kodni"
            " BIRGA yangilang. Qaysi biri haqiqat ekani muhim emas — ikkalasi mos"
            " bo'lishi shart."
        )
        return 1

    print(
        f"✓ Customization contract kod bilan mos — "
        f"{len(accepted)} qabul qilinadigan kalit, {len(written)} klient yozadigan, "
        f"{len(INVARIANTS)} invariant"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
