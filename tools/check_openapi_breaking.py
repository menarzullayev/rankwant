#!/usr/bin/env python3
"""`/api/v1/` only grows (decision 2026-10-27). A change that can break a client
that already works is a new version (`/api/v2/`), not an edit.

Compares `apps/api/openapi/schema.yml` with the one on the base branch and
fails on what a working client would trip over:

  * a path or an operation removed;
  * a response schema property removed, or its `type` changed;
  * an enum value removed;
  * a new REQUIRED request parameter on an existing operation.

Components are compared by name, and every operation's response is compared
as the client receives it: per status code, with each `$ref` resolved in its
own schema. Without the second pass a response that switched to a different
component went unseen — both components were still there, unchanged — although
every field the client read could be gone (measured 2026-11-11:
`POST /classrooms/join/` 201 `Classroom` → `JoinResult` dropped every
top-level field and the check printed "only grew"). Where both sides are the
same component the finding is named after the component, so it reads (and is
allowed) exactly like the by-name pass; a response or field that moved to
another component is named after the operation, e.g.
`POST /api/v1/x/ 201 [Old → New].field: property removed`.

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


REF = "#/components/schemas/"


def ref_of(node: Any) -> str | None:
    """The component a node points at: `$ref`, or drf-spectacular's one-item `allOf`."""
    if not isinstance(node, dict):
        return None
    ref = node.get("$ref")
    if isinstance(ref, str) and ref.startswith(REF):
        return ref[len(REF) :]
    parts = node.get("allOf")
    if isinstance(parts, list) and len(parts) == 1:
        return ref_of(parts[0])
    return None


def resolve(node: Any, schemas: dict[str, Any], depth: int = 0) -> tuple[str | None, dict[str, Any]]:
    """The schema a client receives for `node`, and the component it is named after."""
    if not isinstance(node, dict) or depth > 32:
        return None, {}
    ref = node.get("$ref")
    if isinstance(ref, str) and ref.startswith(REF):
        name = ref[len(REF) :]
        return name, resolve(schemas.get(name), schemas, depth + 1)[1]
    parts = node.get("allOf")
    if isinstance(parts, list) and parts:
        if len(parts) == 1:
            return resolve(parts[0], schemas, depth + 1)
        merged: dict[str, Any] = {"properties": {}}
        for part in parts:
            body = resolve(part, schemas, depth + 1)[1]
            merged["properties"].update(body.get("properties") or {})
            for key in ("type", "items", "enum", "additionalProperties"):
                if key in body:
                    merged.setdefault(key, body[key])
        return None, merged
    return None, node


def alternatives(node: Any) -> list[Any] | None:
    if isinstance(node, dict):
        for key in ("oneOf", "anyOf"):
            if isinstance(node.get(key), list):
                return node[key]
    return None


def pair_alternatives(old: list[Any], new: list[Any]) -> list[tuple[Any, Any]]:
    """Match `oneOf`/`anyOf` branches: same component first, then same `type`, then order.

    An old branch with no partner is dropped: a response that can no longer
    take a shape is narrower, which a working client survives.
    """
    pairs: list[tuple[Any, Any]] = []
    taken: set[int] = set()
    rest: list[Any] = []
    for branch in old:
        name = ref_of(branch)
        hit = next((i for i, b in enumerate(new) if i not in taken and name and ref_of(b) == name), None)
        if hit is None:
            rest.append(branch)
        else:
            taken.add(hit)
            pairs.append((branch, new[hit]))
    for branch in rest:
        free = [i for i in range(len(new)) if i not in taken]
        if not free:
            break
        kind = branch.get("type") if isinstance(branch, dict) else None
        hit = next((i for i in free if isinstance(new[i], dict) and new[i].get("type") == kind), free[0])
        taken.add(hit)
        pairs.append((branch, new[hit]))
    return pairs


class ResponseWalk:
    """Compares two response schemas as resolved trees.

    A node that is the same component on both sides is labelled with that
    component's name and walked once (the label does not depend on the
    route there). A node that changed component, or is inline, keeps the
    operation's label, and a changed pair already on the current branch is
    not entered again (recursive components).
    """

    def __init__(self, old: dict[str, Any], new: dict[str, Any], found: list[str]) -> None:
        self.old = (old.get("components") or {}).get("schemas") or {}
        self.new = (new.get("components") or {}).get("schemas") or {}
        self.found = found
        self.same: set[str] = set()
        self.branch: list[tuple[str | None, str | None]] = []

    def node(self, old: Any, new: Any, label: str) -> None:
        old_alts, new_alts = alternatives(old), alternatives(new)
        if old_alts is not None or new_alts is not None:
            for a, b in pair_alternatives(old_alts or [old], new_alts or [new]):
                self.node(a, b, label)
            return
        old_name, old_body = resolve(old, self.old)
        new_name, new_body = resolve(new, self.new)
        if old_name is not None and old_name == new_name:
            if old_name not in self.same:
                self.same.add(old_name)
                self.body(old_body, new_body, old_name)
            return
        if old_name is None and new_name is None:
            self.body(old_body, new_body, label)
            return
        key = (old_name, new_name)
        if key in self.branch:
            return
        self.branch.append(key)
        try:
            self.body(old_body, new_body, f"{label} [{old_name or 'inline'} → {new_name or 'inline'}]")
        finally:
            self.branch.pop()

    def body(self, old: dict[str, Any], new: dict[str, Any], label: str) -> None:
        old_type, new_type = old.get("type"), new.get("type")
        if old_type and new_type and old_type != new_type:
            self.found.append(f"{label}: type {old_type} → {new_type}")
            return  # nothing below it can line up any more
        new_props = new.get("properties") or {}
        for prop, spec in (old.get("properties") or {}).items():
            if prop not in new_props:
                self.found.append(f"{label}.{prop}: property removed")
            else:
                self.node(spec, new_props[prop], f"{label}.{prop}")
        for key, suffix in (("items", "[]"), ("additionalProperties", "{*}")):
            if isinstance(old.get(key), dict) and isinstance(new.get(key), dict):
                self.node(old[key], new[key], f"{label}{suffix}")
        gone = set(old.get("enum") or []) - set(new.get("enum") or [])
        for value in sorted(map(str, gone)):
            self.found.append(f"{label}: enum value '{value}' removed")


def compare_responses(path: str, method: str, old: dict[str, Any], new: dict[str, Any], walk: ResponseWalk) -> None:
    now = new.get("responses") or {}
    for status, response in (old.get("responses") or {}).items():
        if status not in now or not isinstance(response, dict):
            continue  # a status code that is no longer documented is not compared here
        label = f"{method.upper()} {path} {status}"
        content = (now[status] or {}).get("content") or {}
        for ctype, media in (response.get("content") or {}).items():
            if not isinstance(media, dict) or "schema" not in media:
                continue
            if ctype not in content:
                walk.found.append(f"{label}: {ctype} body removed")
                continue
            walk.node(media["schema"], (content[ctype] or {}).get("schema") or {}, label)


def compare(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    found: list[str] = []
    walk = ResponseWalk(old, new, found)
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
            compare_responses(path, method, item[method], now[method], walk)
    old_schemas = walk.old
    new_schemas = walk.new
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
    return list(dict.fromkeys(found))  # both passes name a same-component finding alike


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
