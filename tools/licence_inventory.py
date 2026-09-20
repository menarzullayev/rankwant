#!/usr/bin/env python3
"""Dependency licence inventory — the input a lawyer reviews before launch.

`docs/09-development-plan/README.md:81` carries the launch gate "Huquqiy:
litsenziya tahlili yurist tomonidan tasdiqlangan (ADR-0003)". That gate needs an
inventory first, and the inventory has to be reproducible: a hand-written list of
~800 packages is wrong the day after it is written.

Sources read (all in-repo, all pinned):

  * `apps/api/requirements.lock` + `requirements-dev.lock` — uv-compiled pins.
    (`apps/api/uv.lock` is a three-line stub and is deliberately NOT used.)
  * `services/judge-py/uv.lock` — the inactive Python judge, kept by ADR-0004.
  * `apps/web/package-lock.json`, `tests/e2e/package-lock.json` — npm v3.
  * `services/judge-go/go.mod` — the shipped Go judge.
  * the five Dockerfiles — base images, which carry their own licences.

Where the licences come from, and where they do not:

  * **Node** — the lockfile's own `license` field. Measured 2026-09-21: 669 of
    670 entries in `apps/web/package-lock.json` carry it (the 670th is the root
    project entry, which is ours).
  * **Python** — the installed `.venv` distribution metadata, read in the order
    `License-Expression` (PEP 639) → `License:` → `Classifier: License ::`. All
    three shapes occur in this environment (measured on `ast_serialize`,
    `asgiref`, `amqp`). ⚠️ The venv is **gitignored**, so this works only on a
    machine that has run the install — which is exactly why the generated file
    is committed and `--check` never needs the venv.
  * **Go** — nothing offline: `~/go/pkg/mod` does not exist on this machine and
    `go` is not on PATH (measured 2026-09-21). The modules are listed and the
    licence is left UNKNOWN rather than guessed.
  * **Docker base images** — an aggregate, not one licence: `debian:trixie`
    ships GPL and LGPL components. They are listed and flagged, never called
    clean.

Output is generated, never hand-edited:

    docs/research/<date>-licence-inventory/packages.tsv   one row per package
    docs/research/<date>-licence-inventory/README.md      the lawyer's document

`--check` compares the committed `packages.tsv` **name set** against the
lockfiles and exits 1 on drift. It is offline and needs no venv, so CI runs it:
a new dependency then cannot make the inventory silently false. It compares
names, not versions — a version bump of an already-reviewed package does not
fail it, and that limitation is stated in the generated document.

Exit codes: 0 fine, 1 drift (with `--check`), 2 a source could not be read or
parsed — never treated as "fine".
"""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

import _console

_console.force_utf8()

ROOT = Path(__file__).resolve().parent.parent

#: Where the generated record lives. The date is the snapshot's, not "today".
RECORD_DIR = "docs/research/2026-09-21-licence-inventory"

PY_PINS = {
    "api": ("apps/api/requirements.lock", "runtime"),
    "api-dev": ("apps/api/requirements-dev.lock", "dev"),
}
PY_UV = {"judge-py": "services/judge-py/uv.lock"}
NODE_LOCKS = {
    "web": "apps/web/package-lock.json",
    "e2e": "tests/e2e/package-lock.json",
}
GO_MOD = "services/judge-go/go.mod"
DOCKERFILES = (
    "apps/api/Dockerfile",
    "apps/web/Dockerfile",
    "services/judge-go/Dockerfile",
    "services/judge-py/Dockerfile",
    "tools/runner/Dockerfile",
)
#: The venv is gitignored; a missing one is normal and only costs Python licences.
PY_VENV = "apps/api/.venv"

#: Copyleft classes, checked in this order. `LGPL` must be tested before `GPL`
#: or every LGPL package would be reported as strong copyleft — `"GPL-3"` is a
#: substring of `"LGPL-3.0-ONLY"`, and that mistake made the first run of this
#: script report "0 strong, 0 weak" while 50 LGPL/MPL packages sat in the table.
COPYLEFT = (
    ("strong-copyleft", ("AGPL", "GPL-3", "GPL-2", "GPLV3", "GPLV2", "GNU GENERAL PUBLIC")),
    ("weak-copyleft", ("LGPL", "MPL", "MOZILLA PUBLIC", "EPL", "ECLIPSE PUBLIC", "CDDL")),
)
PERMISSIVE = (
    "MIT",
    "BSD",
    "APACHE",
    "ISC",
    "PSF",
    "PYTHON SOFTWARE FOUNDATION",
    "UNLICENSE",
    "ZLIB",
    "0BSD",
    "CC0",
    "BLUEOAK",
    "PUBLIC DOMAIN",
    "HISTORICAL PERMISSION",
)
#: No licence string at all. Kept apart from `other` below: "the metadata says
#: nothing" and "the metadata says something this script does not recognise" are
#: different problems for the reader.
NOTHING = ("", "UNKNOWN", "NONE")


def classify(licence: str) -> str:
    """`strong-copyleft` | `weak-copyleft` | `permissive` | `other` | `unknown`.

    `other` is not a soft `unknown`: it means a licence string exists and needs a
    human eye (`python-dateutil` declares the literal "Dual License",
    `caniuse-lite` declares `CC-BY-4.0` — a content licence on a code
    dependency). Reporting those as UNKNOWN would hide the real string.
    """
    text = licence.upper()
    if not licence.strip() or text in NOTHING:
        return "unknown"
    for kind, markers in COPYLEFT:
        # `(?<!L)GPL` keeps a bare GPL marker from matching inside LGPL/AGPL.
        if any(re.search(rf"(?<!L){re.escape(marker)}", text) for marker in markers):
            return kind
    if any(marker in text for marker in PERMISSIVE):
        return "permissive"
    return "other"


def read(rel: str) -> str:
    try:
        return (ROOT / rel).read_bytes().decode("utf-8").replace("\r\n", "\n")
    except OSError as exc:
        raise SystemExit(f"✗ o'qib bo'lmadi: {rel}: {exc}")


# ── Sources ──────────────────────────────────────────────────────────────


def python_pins() -> list[tuple[str, str, str, str]]:
    """(ecosystem, name, version, scope) from the uv-compiled pins."""
    rows: list[tuple[str, str, str, str]] = []
    for eco, (rel, scope) in PY_PINS.items():
        for line in read(rel).splitlines():
            match = re.match(r"^([A-Za-z0-9._-]+)==([^\s;]+)", line)
            if match:
                rows.append((eco, match.group(1).lower(), match.group(2), scope))
    return rows


def python_uv() -> list[tuple[str, str, str, str]]:
    """(ecosystem, name, version, scope) from `uv.lock` files.

    `uv` writes the project itself into its own lockfile as
    `source = { editable = "." }` — measured: `rankwant-judge-py 0.1.0`. That is
    this repository, not a dependency; listing it would put our own package in
    the lawyer's UNKNOWN register.
    """
    rows: list[tuple[str, str, str, str]] = []
    for eco, rel in PY_UV.items():
        data = tomllib.loads(read(rel))
        for package in data.get("package", []):
            source = package.get("source") or {}
            if source.get("editable") == "." or source.get("virtual") == ".":
                continue
            rows.append((eco, str(package["name"]).lower(), str(package["version"]), "runtime"))
    return rows


def python_licences(venv: Path) -> dict[str, str]:
    """Installed metadata, keyed by normalised distribution name.

    All three shapes occur in this environment, so all three are read, in
    descending order of authority: `License-Expression` (PEP 639, SPDX) →
    `License:` (free text, sometimes `UNKNOWN`) → the OSI classifier.
    """
    found: dict[str, str] = {}
    for meta in venv.glob("**/site-packages/*.dist-info/METADATA"):
        name = expression = legacy = classifier = ""
        for line in meta.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("Name:") and not name:
                name = line[5:].strip()
            elif line.startswith("License-Expression:") and not expression:
                expression = line[19:].strip()
            elif line.startswith("License:") and not legacy:
                value = line[8:].strip()
                if value.upper() not in NOTHING:
                    legacy = value
            elif line.startswith("Classifier: License :: OSI Approved ::") and not classifier:
                classifier = line.rsplit("::", 1)[-1].strip()
        licence = expression or legacy or classifier
        if name and licence:
            found.setdefault(normalise(name), licence)
    return found


def normalise(name: str) -> str:
    """PEP 503 name normalisation — the lockfiles and the metadata disagree.

    Measured: the lockfile says `ast-serialize`, the installed metadata says
    `ast_serialize`. Without this the lookup misses and the package is reported
    UNKNOWN for no reason.
    """
    return re.sub(r"[-_.]+", "-", name).lower()


def node_packages() -> list[tuple[str, str, str, str]]:
    """(ecosystem, name, version, scope) from npm v3 lockfiles."""
    rows: list[tuple[str, str, str, str]] = []
    for eco, rel in NODE_LOCKS.items():
        data = json.loads(read(rel))
        for path, entry in data.get("packages", {}).items():
            if not path:
                continue  # the root entry is this repository, not a dependency
            name = path.rsplit("node_modules/", 1)[-1]
            scope = "dev" if entry.get("dev") else "runtime"
            rows.append((eco, name.lower(), str(entry.get("version", "?")), scope))
    return rows


def node_licences() -> dict[str, str]:
    """Lockfile `license` fields, keyed by lowercased package name."""
    found: dict[str, str] = {}
    for rel in NODE_LOCKS.values():
        data = json.loads(read(rel))
        for path, entry in data.get("packages", {}).items():
            if not path:
                continue
            name = path.rsplit("node_modules/", 1)[-1].lower()
            licence = entry.get("license")
            if isinstance(licence, dict):  # legacy npm shape: {"type": "MIT"}
                licence = licence.get("type")
            if licence:
                found.setdefault(name, str(licence))
    return found


def go_packages() -> list[tuple[str, str, str, str]]:
    """(ecosystem, name, version, scope) from `go.mod`, direct vs indirect."""
    rows: list[tuple[str, str, str, str]] = []
    for line in read(GO_MOD).splitlines():
        match = re.match(r"^\s+([^\s]+)\s+(v[^\s]+)(\s+//\s*indirect)?\s*$", line)
        if match:
            scope = "indirect" if match.group(3) else "direct"
            rows.append(("go", match.group(1).lower(), match.group(2), scope))
    return rows


def docker_images() -> list[tuple[str, str]]:
    """(dockerfile, image) for every `FROM`, in file order."""
    rows: list[tuple[str, str]] = []
    for rel in DOCKERFILES:
        for line in read(rel).splitlines():
            match = re.match(r"^FROM\s+(\S+)", line, re.I)
            if match:
                rows.append((rel, match.group(1)))
    return rows


# ── Assembly ─────────────────────────────────────────────────────────────


def collect(venv: Path) -> tuple[list[dict[str, str]], list[tuple[str, str]]]:
    py_lic = python_licences(venv)
    node_lic = node_licences()

    rows: list[dict[str, str]] = []
    for eco, name, version, scope in python_pins() + python_uv():
        rows.append(
            {
                "ecosystem": f"python/{eco}",
                "name": name,
                "version": version,
                "scope": scope,
                "licence": py_lic.get(normalise(name), ""),
            }
        )
    for eco, name, version, scope in node_packages():
        rows.append(
            {
                "ecosystem": f"node/{eco}",
                "name": name,
                "version": version,
                "scope": scope,
                "licence": node_lic.get(name, ""),
            }
        )
    for eco, name, version, scope in go_packages():
        rows.append(
            {
                "ecosystem": f"{eco}/judge-go",
                "name": name,
                "version": version,
                "scope": scope,
                "licence": "",
            }
        )
    rows.sort(key=lambda row: (row["ecosystem"], row["name"]))
    return rows, docker_images()


def render_tsv(rows: list[dict[str, str]]) -> str:
    lines = ["ecosystem\tname\tversion\tscope\tlicence"]
    lines += [
        "\t".join((r["ecosystem"], r["name"], r["version"], r["scope"], r["licence"] or "UNKNOWN"))
        for r in rows
    ]
    return "\n".join(lines) + "\n"


def _table(rows: list[dict[str, str]]) -> str:
    out = ["| Package | Version | Scope | Licence |", "|---|---|---|---|"]
    out += [
        f"| `{r['name']}` | {r['version']} | {r['scope']} | {r['licence'] or '**UNKNOWN**'} |"
        for r in rows
    ]
    return "\n".join(out)


def render_readme(rows: list[dict[str, str]], images: list[tuple[str, str]]) -> str:
    by_eco: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_eco.setdefault(row["ecosystem"], []).append(row)

    total = len(rows)
    unknown = [r for r in rows if classify(r["licence"]) == "unknown"]
    other = [r for r in rows if classify(r["licence"]) == "other"]
    strong = [r for r in rows if classify(r["licence"]) == "strong-copyleft"]
    weak = [r for r in rows if classify(r["licence"]) == "weak-copyleft"]

    summary = [
        "| Ecosystem | Packages | runtime | dev | classified | needs review | UNKNOWN |",
        "|---|---|---|---|---|---|---|",
    ]
    for eco in sorted(by_eco):
        group = by_eco[eco]
        dev = sum(1 for r in group if r["scope"] == "dev")
        nothing = sum(1 for r in group if classify(r["licence"]) == "unknown")
        odd = sum(1 for r in group if classify(r["licence"]) == "other")
        summary.append(
            f"| `{eco}` | {len(group)} | {len(group) - dev} | {dev} | "
            f"{len(group) - nothing - odd} | {odd} | {nothing} |"
        )
    summary.append(
        f"| **total** | **{total}** | | | **{total - len(unknown) - len(other)}** | "
        f"**{len(other)}** | **{len(unknown)}** |"
    )

    out = [
        "# Dependency licence inventory",
        "",
        f"**Snapshot:** 2026-09-21 · **Packages:** {total} · **Base images:** "
        f"{len(set(image for _, image in images))}",
        "**Generated by:** `python tools/licence_inventory.py` — do not hand-edit.",
        "**Launch gate:** `docs/09-development-plan/README.md:81` — "
        '"Huquqiy: litsenziya tahlili yurist tomonidan tasdiqlangan (ADR-0003)".',
        "",
        "> This is an **inventory**, not a legal opinion. It says which licences the",
        "> pinned dependencies declare and which ones could not be determined. The",
        "> lawyer's sign-off is the launch gate; this file is its input.",
        "",
        "## 1. What this is not",
        "",
        "- Not a legal opinion, and not a statement that any licence is compatible",
        "  with how this platform is used or distributed.",
        "- Not a patent or trademark analysis.",
        "- Not a version-level guarantee: `--check` compares package **names**, so a",
        "  version bump of an already-reviewed package does not fail it. A licence",
        "  can change between versions; re-run the generator after a major bump.",
        "- Not complete for Go: see § 4.",
        "",
        "## 2. Method",
        "",
        "Sources, all pinned in-repo:",
        "",
        "| Source | Ecosystem |",
        "|---|---|",
        "| `apps/api/requirements.lock`, `requirements-dev.lock` | Python, API |",
        "| `services/judge-py/uv.lock` | Python, inactive judge (ADR-0004 keeps it) |",
        "| `apps/web/package-lock.json`, `tests/e2e/package-lock.json` | Node |",
        "| `services/judge-go/go.mod` | Go, shipped judge |",
        "| five `Dockerfile`s | base images |",
        "",
        "Licence resolution, in order of reliability:",
        "",
        "1. **Node** — the lockfile's own `license` field (present on every",
        "   dependency entry, measured 2026-09-21).",
        "2. **Python** — the installed `.venv` distribution metadata, read as",
        "   `License-Expression` → `License:` → `Classifier: License ::`.",
        "   ⚠️ The venv is gitignored; a machine without it produces UNKNOWN for",
        "   every Python package. That is why the output is committed.",
        "3. **Go** — nothing offline; see § 4.",
        "",
        "Reproduce:",
        "",
        "```bash",
        "python tools/licence_inventory.py            # regenerate (needs the venv)",
        "python tools/licence_inventory.py --check    # drift only, offline, CI-safe",
        "```",
        "",
        "## 3. Summary",
        "",
        "\n".join(summary),
        "",
        f"Copyleft: **{len(strong)} strong**, **{len(weak)} weak**. "
        f"Needs a human eye: **{len(other)}**. UNKNOWN: **{len(unknown)}**.",
        "",
    ]

    out += ["## 4. Licences that could not be determined", ""]
    if unknown:
        out += [
            "These are **not** clean — they are unknown. A lawyer reviewing this",
            "document must treat them as open, and the cheapest way to close them is",
            "listed under each group.",
            "",
        ]
        for eco in sorted({r["ecosystem"] for r in unknown}):
            group = [r for r in unknown if r["ecosystem"] == eco]
            out += [f"**`{eco}` — {len(group)} package(s)**", "", _table(group), ""]
        out += [
            "Closing them:",
            "",
            "- **Go** — run `go mod download` once (or `go list -m -json all`) on a",
            "  machine with the toolchain, then add a reader for",
            "  `$(go env GOMODCACHE)/<module>@<version>/LICENSE`.",
            "- **Python** — run the install in `apps/api` (the venv is gitignored),",
            "  then regenerate.",
            "- **Node** — if any appear, the lockfile entry has no `license` field;",
            "  read `node_modules/<name>/package.json` after `npm ci`.",
            "",
        ]
    else:
        out += ["None — every package in every source declared a licence.", ""]

    out += ["## 5. Licences that need a human eye", ""]
    if other:
        out += [
            "A licence string exists, but it is not one this script can classify.",
            "These are **not** UNKNOWN — the declared text is shown, and it is the",
            "text a reviewer has to read. The first run of this generator reported",
            "them as UNKNOWN because `python-dateutil` declares the literal",
            '"Dual License" and `caniuse-lite` declares `CC-BY-4.0` (a content',
            "licence on a code dependency) — both are real answers, not missing ones.",
            "",
        ]
        for eco in sorted({r["ecosystem"] for r in other}):
            group = [r for r in other if r["ecosystem"] == eco]
            out += [f"**`{eco}` — {len(group)} package(s)**", "", _table(group), ""]
    else:
        out += ["None — every declared licence string was recognised.", ""]

    out += ["## 6. Copyleft register", ""]
    if strong or weak:
        out += [
            "Copyleft is the part a lawyer actually needs to see, because it can",
            "attach obligations to distribution. Strong copyleft first.",
            "",
        ]
        for kind, group in (("strong-copyleft", strong), ("weak-copyleft", weak)):
            if not group:
                continue
            out += [f"### {kind} — {len(group)}", "", _table(group), ""]
    else:
        out += ["None found in the pinned set.", ""]

    out += [
        "## 7. Base images",
        "",
        "A base image is an aggregate, not a single licence: `debian:trixie`",
        "contains GPL and LGPL components. These are **not** called clean here;",
        "they are what the image is built from, and the lawyer decides.",
        "",
        "| Dockerfile | Image |",
        "|---|---|",
    ]
    out += [f"| `{rel}` | `{image}` |" for rel, image in images]
    out += [
        "",
        "## 8. Drift guard",
        "",
        "`tools/licence_inventory.py --check` compares the committed",
        "`packages.tsv` name set against the lockfiles and fails when a package is",
        "added or removed. It runs in CI's `Docs and contract integrity` job, so a",
        "new dependency cannot make this document quietly false.",
        "",
        "## 9. Full inventory",
        "",
    ]
    for eco in sorted(by_eco):
        out += [f"### `{eco}` — {len(by_eco[eco])}", "", _table(by_eco[eco]), ""]
    return "\n".join(out)


# ── Drift ────────────────────────────────────────────────────────────────


def committed_names() -> set[tuple[str, str]]:
    path = ROOT / RECORD_DIR / "packages.tsv"
    if not path.exists():
        raise SystemExit(f"✗ {RECORD_DIR}/packages.tsv yo'q — avval generatorsiz ishlatib ko'ring")
    names: set[tuple[str, str]] = set()
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) >= 2:
            names.add((parts[0], parts[1]))
    return names


def check(rows: list[dict[str, str]]) -> int:
    expected = {(r["ecosystem"], r["name"]) for r in rows}
    found = committed_names()
    added = sorted(expected - found)
    removed = sorted(found - expected)
    if not added and not removed:
        print(f"✓ Litsenziya inventari joyida: {len(expected)} paket manbalarga mos")
        return 0
    print("✗ Litsenziya inventari lockfile'lardan chetlashgan — generatorni yurgizing:")
    for eco, name in added:
        print(f"  + qo'shilgan: {eco}/{name}")
    for eco, name in removed:
        print(f"  - olib tashlangan: {eco}/{name}")
    print("  `python tools/licence_inventory.py`")
    return 1


def main(argv: list[str]) -> int:
    venv = ROOT / PY_VENV
    if "--venv" in argv:
        venv = Path(argv[argv.index("--venv") + 1]).resolve()

    rows, images = collect(venv)
    if "--check" in argv:
        return check(rows)

    if not venv.is_dir():
        print(f"⚠ venv topilmadi: {venv}")
        print("  Python litsenziyalari UNKNOWN bo'ladi. Git worktree'da `.venv`")
        print("  yo'q (gitignored) — canonical checkout'ga ishora qiling:")
        print("  --venv C:/Users/nsn/project/cp/rankwant/apps/api/.venv")

    record = ROOT / RECORD_DIR
    record.mkdir(parents=True, exist_ok=True)
    (record / "packages.tsv").write_text(render_tsv(rows), encoding="utf-8")
    (record / "README.md").write_text(render_readme(rows, images), encoding="utf-8")

    unknown = sum(1 for r in rows if classify(r["licence"]) == "unknown")
    strong = sum(1 for r in rows if classify(r["licence"]) == "strong-copyleft")
    print(f"✓ {len(rows)} paket yozildi → {RECORD_DIR}/")
    print(f"  UNKNOWN: {unknown} · strong copyleft: {strong} · base image: {len(images)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
