#!/usr/bin/env python3
"""Upsert the RankWant guest HTML Cache Rule.

Guest GET `/`, `/login`, `/register`, `/terms`, `/privacy` (uz-forced) plus
HITL problems-al: GET `/problems` empty-query, locale-aware. Eligible +
respect origin TTL. Session / `rw_locale` / `rw:markup` / RSC stay out.

Usage:
    python tools/cf_guest_cache_apply.py          # upsert
    python tools/cf_guest_cache_apply.py --check  # rule present and matches JSON

Do not PUT the whole ruleset from scratch — other cache rules must survive.

Exit: 0 ok, 1 rule missing/mismatch (--check), 2 unread (token/network).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import cf_route_audit as cf  # noqa: E402

ZONE_NAME = "rankwant.uz"
PHASE = "http_request_cache_settings"
RULE_FILE = ROOT / "cf-guest-cache-rule.json"


def _fail(message: str, code: int = 2) -> None:
    print(message)
    raise SystemExit(code)


def access_token() -> str:
    """API token from env / `.env.public`, else wrangler OAuth."""
    env = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if env:
        return env
    env_path = Path(os.environ.get("RANKWANT_ENV_FILE") or ROOT.parent / ".env.public")
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("CLOUDFLARE_API_TOKEN="):
                value = line.split("=", 1)[1].strip().strip("'\"")
                if value:
                    return value
    return cf.access_token()


def desired_rule() -> dict:
    try:
        return json.loads(RULE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail(f"{RULE_FILE.name} o'qilmadi: {exc}")
    raise AssertionError("unreachable")


def api(method: str, path: str, token: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        f"{cf.API}{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": cf.UA,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode()[:500]
        if exc.code in (401, 403):
            _fail(f"API ruxsat bermadi ({exc.code}): {payload}")
        if method == "GET" and exc.code == 404:
            return {"success": False, "result": None, "errors": [{"code": 404}]}
        _fail(f"API xatosi {method} {path} ({exc.code}): {payload}")
    except OSError as exc:
        _fail(f"Tarmoq xatosi {path}: {exc}")
    raise AssertionError("unreachable")


def zone_id(token: str) -> str:
    zones = {
        row["name"]: row["id"]
        for row in api("GET", "/zones?per_page=50", token)["result"]
    }
    if ZONE_NAME not in zones:
        _fail(f"Zona topilmadi: {ZONE_NAME}")
    return zones[ZONE_NAME]


def entrypoint(token: str, zid: str) -> dict | None:
    payload = api(
        "GET",
        f"/zones/{zid}/rulesets/phases/{PHASE}/entrypoint",
        token,
    )
    if not payload.get("success"):
        return None
    return payload["result"]


def rule_payload(spec: dict) -> dict:
    return {
        "ref": spec["ref"],
        "description": spec["description"],
        "expression": spec["expression"],
        "action": spec["action"],
        "enabled": spec["enabled"],
        "action_parameters": spec["action_parameters"],
    }


def matches(live: dict, spec: dict) -> bool:
    params = live.get("action_parameters") or {}
    vary = params.get("vary") or {}
    accept = (vary.get("headers") or {}).get("accept-language") or {}
    languages = accept.get("languages") or []
    return (
        live.get("action") == "set_cache_settings"
        and live.get("enabled") is not False
        and live.get("expression") == spec["expression"]
        and params.get("cache") is True
        and (params.get("edge_ttl") or {}).get("mode") == "respect_origin"
        and (params.get("browser_ttl") or {}).get("mode") == "respect_origin"
        and (vary.get("default") or {}).get("action") == "passthrough"
        and accept.get("action") == "normalize"
        and "uz" in languages
        and "ru" in languages
    )


def is_guest_html_rule(rule: dict, spec: dict) -> bool:
    if rule.get("ref") == spec["ref"]:
        return True
    if rule.get("id") and rule.get("id") == spec.get("id"):
        return True
    if rule.get("action") != "set_cache_settings":
        return False
    expression = rule.get("expression") or ""
    return (
        'http.request.uri.path eq "/"' in expression
        and "/login" in expression
        and "/privacy" in expression
    )


def upsert(token: str, zid: str, spec: dict) -> None:
    current = entrypoint(token, zid)
    wanted = rule_payload(spec)
    if current is None:
        created = api(
            "POST",
            f"/zones/{zid}/rulesets",
            token,
            {
                "name": "Zone-level Cache Settings Ruleset",
                "kind": "zone",
                "phase": PHASE,
                "rules": [wanted],
            },
        )
        if not created.get("success"):
            _fail(f"Ruleset yaratilmadi: {created}")
        print(f"✓ {ZONE_NAME}: cache ruleset + mehmon HTML qoidasi yaratildi")
        return

    rules = list(current.get("rules") or [])
    replaced = False
    for i, rule in enumerate(rules):
        if is_guest_html_rule(rule, spec):
            kept = dict(wanted)
            if rule.get("id"):
                kept["id"] = rule["id"]
            # CF error 20142: cannot replace an empty/id ref with a new string.
            if rule.get("ref"):
                kept["ref"] = rule["ref"]
            else:
                kept.pop("ref", None)
            rules[i] = kept
            replaced = True
            break
    if not replaced:
        rules.append(wanted)

    updated = api(
        "PUT",
        f"/zones/{zid}/rulesets/{current['id']}",
        token,
        {"rules": rules},
    )
    if not updated.get("success"):
        _fail(f"Ruleset yangilanmadi: {updated}")
    action = "yangilandi" if replaced else "qo'shildi"
    print(f"✓ {ZONE_NAME}: mehmon HTML cache qoidasi {action} (boshqa cache qoidalari saqlanadi)")


def check(token: str, zid: str, spec: dict) -> int:
    current = entrypoint(token, zid)
    if current is None:
        print("✗ Cache ruleset yo'q — mehmon HTML qoidasi qo'llanilmagan")
        return 1
    for rule in current.get("rules") or []:
        if is_guest_html_rule(rule, spec):
            if matches(rule, spec):
                print(f"✓ {ZONE_NAME}: mehmon HTML cache qoidasi jonli va JSON bilan bir xil")
                return 0
            print("✗ Mehmon HTML cache qoidasi bor, lekin JSON dan farq qiladi")
            return 1
    print("✗ Mehmon HTML cache qoidasi (ref=rankwant_guest_html_cache) yo'q")
    return 1


def main() -> int:
    spec = desired_rule()
    token = access_token()
    zid = zone_id(token)
    if "--check" in sys.argv:
        return check(token, zid, spec)
    upsert(token, zid, spec)
    return check(token, zid, spec)


if __name__ == "__main__":
    raise SystemExit(main())
