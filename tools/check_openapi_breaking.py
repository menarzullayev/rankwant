#!/usr/bin/env python3
"""`/api/v1/` only grows (decision 2026-10-27). A change that can break a client
that already works is a new version (`/api/v2/`), not an edit.

Compares `apps/api/openapi/schema.yml` with the one on the base branch and
fails on what a working client would trip over:

  * a path or an operation removed;
  * a response schema property removed, or its `type` changed;
  * an enum value removed;
  * a new REQUIRED request parameter on an existing operation.

Adding paths, operations, optional parameters, properties and enum values is
free. A deliberate exception goes in `tools/openapi-breaking-allow.txt` with a
reason on the line above it, so the exception is reviewed like any other change.

    python tools/check_openapi_breaking.py [--base origin/main | --old <schema.yml>]
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
from typing import Any

import _console
import yaml

_console.force_utf8()

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = "apps/api/openapi/schema.yml"
ALLOW = ROOT / "tools/openapi-breaking-allow.txt"
METHODS = ("get", "put", "post", "delete", "patch", "head", "options")


def load_base(ref: str) -> dict[str, Any] | None:
    shown = subprocess.run(
        ["git", "show", f"{ref}:{SCHEMA}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    return yaml.safe_load(shown.stdout) if shown.returncode == 0 else None


def required_params(op: dict[str, Any]) -> set[tuple[str, str]]:
    return {(p["in"], p["name"]) for p in op.get("parameters", []) if p.get("required")}


def compare(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    found: list[str] = []
    for path, item in (old.get("paths") or {}).items():
        now = (new.get("paths") or {}).get(path)
        if now is None:
            found.append(f"{path}: path removed")
            continue
        for method in METHODS:
            if method not in item:
                continue
            if method not in now:
                found.append(f"{method.upper()} {path}: operation removed")
                continue
            added = required_params(now[method]) - required_params(item[method])
            for where, name in sorted(added):
                found.append(f"{method.upper()} {path}: new required {where} parameter '{name}'")
    old_schemas = (old.get("components") or {}).get("schemas") or {}
    new_schemas = (new.get("components") or {}).get("schemas") or {}
    for name, schema in old_schemas.items():
        now_schema = new_schemas.get(name)
        if now_schema is None:
            continue  # a component nobody references any more is not a wire change
        for prop, spec in (schema.get("properties") or {}).items():
            now_spec = (now_schema.get("properties") or {}).get(prop)
            if now_spec is None:
                found.append(f"{name}.{prop}: property removed")
            elif spec.get("type") and now_spec.get("type") and spec["type"] != now_spec["type"]:
                found.append(f"{name}.{prop}: type {spec['type']} → {now_spec['type']}")
        gone = set(schema.get("enum") or []) - set(now_schema.get("enum") or [])
        for value in sorted(map(str, gone)):
            found.append(f"{name}: enum value '{value}' removed")
    return found


def allowed() -> set[str]:
    if not ALLOW.exists():
        return set()
    lines = (line.strip() for line in ALLOW.read_text(encoding="utf-8").splitlines())
    return {line for line in lines if line and not line.startswith("#")}


def main() -> int:
    if "--old" in sys.argv:  # a schema file instead of a git ref (self-tests)
        old = yaml.safe_load(pathlib.Path(sys.argv[sys.argv.index("--old") + 1]).read_text(encoding="utf-8"))
        ref = "the given file"
    else:
        ref = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else "origin/main"
        old = load_base(ref)
    if old is None:
        print(f"· {ref} has no schema to compare with — skipped")
        return 0
    new = yaml.safe_load((ROOT / SCHEMA).read_text(encoding="utf-8"))
    found = [item for item in compare(old, new) if item not in allowed()]
    if not found:
        print("✓ /api/v1/ only grew")
        return 0
    print("✗ breaking change to /api/v1/ (decision 2026-10-27: a break is /api/v2/):")
    for item in found:
        print("   ", item)
    print(f"  A deliberate exception: add the line above to tools/openapi-breaking-allow.txt, with a reason.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
