"""Audit Cloudflare Worker route settings for `rankwant.uz`.

Prints one TAB-separated line per route: zone, pattern, request_limit_fail_open.

Exit codes
    0 — read ok
    2 — could not read (no token, network, API error). Deliberately distinct
        from "the setting is wrong": exit 2 says NOTHING about site health.

Why the field matters
    The free plan allows 100,000 Worker requests per day and
    `rankwant-maintenance` runs on every request. When the limit is exhausted,
    `request_limit_fail_open=false` closes the site with Cloudflare Error 1027;
    `true` passes the request through to the origin. The default is `false`, so
    a recreated route silently loses the protection.

Test hooks (used by tools/check_negative.py — never in normal runs)
    CF_ROUTE_STUB             newline-separated `zone<TAB>pattern<TAB>bool`
                              printed verbatim instead of calling the API.
    CF_ROUTE_FORCE_UNREADABLE  any value makes the script exit 2, simulating a
                              missing or burned token.

⚠️ OAuth refresh tokens ROTATE
    Cloudflare returns a NEW refresh_token with every successful refresh and
    invalidates the old one. A refresh that is not written back therefore burns
    the credential — the next run fails with `invalid_grant`. We persist the
    rotated token to TOKEN_CACHE (outside the repo, chmod 600).

    If the cached token is also invalid, a browser login is required:
        cd services/maintenance-worker && npx wrangler login
"""

import json
import os
import re
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

WRANGLER_CONFIG = (
    Path.home() / "AppData/Roaming/xdg.config/.wrangler/config/default.toml"
)
#: Written by this script so a rotated refresh token is not lost.
TOKEN_CACHE = Path.home() / ".cloudflared" / "wrangler_refresh.json"

TOKEN_URL = "https://dash.cloudflare.com/oauth2/token"
#: wrangler's public OAuth client id.
CLIENT_ID = "54d11594-84e4-41aa-b438-e81b8fa78ee7"
API = "https://api.cloudflare.com/client/v4"

#: Every zone that carries a rankwant route. A new zone must be added here,
#: otherwise its route is silently unchecked.
ZONES = ("rankwant.uz", "bugvector.uz")

UA = "wrangler/4.0.0"


def _fail(message: str) -> None:
    print(message)
    raise SystemExit(2)


def _toml_value(text: str, key: str) -> str | None:
    m = re.search(rf'^{key}\s*=\s*"([^"]+)"', text, re.M)
    return m.group(1) if m else None


def _save_refresh(token: str, access: str, expires_in: int) -> None:
    TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE.write_text(
        json.dumps(
            {
                "refresh_token": token,
                "access_token": access,
                "expires_at": _now() + expires_in,
            }
        ),
        encoding="utf-8",
    )
    try:
        os.chmod(TOKEN_CACHE, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def _now() -> int:
    import time

    return int(time.time())


def _refresh(refresh_token: str) -> str:
    data = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
        }
    ).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            # Without a User-Agent Cloudflare answers 403 with `error code: 1010`.
            "User-Agent": UA,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        if "invalid_grant" in body:
            _fail(
                "Token yangilanmadi: refresh token bekor qilingan.\n"
                "Brauzerda qayta kirish kerak:\n"
                "  cd services/maintenance-worker && npx wrangler login"
            )
        _fail(f"Token yangilanmadi ({e.code}): {body}")
    except OSError as e:
        _fail(f"Tarmoq xatosi: {e}")

    # Persist the ROTATED refresh token — the old one is now dead.
    new_refresh = payload.get("refresh_token")
    if new_refresh:
        _save_refresh(
            new_refresh, payload["access_token"], payload.get("expires_in", 86400)
        )
    return payload["access_token"]


def access_token() -> str:
    # 1. A cached, still-valid access token wins: no network, no rotation.
    if TOKEN_CACHE.exists():
        try:
            cached = json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached = {}
        if cached.get("access_token") and cached.get("expires_at", 0) > _now() + 60:
            return cached["access_token"]
        if cached.get("refresh_token"):
            return _refresh(cached["refresh_token"])

    # 2. Fall back to wrangler's own config (may be stale or already burned).
    if not WRANGLER_CONFIG.exists():
        _fail(f"wrangler konfiguratsiyasi yo'q: {WRANGLER_CONFIG}")
    text = WRANGLER_CONFIG.read_text(encoding="utf-8")
    refresh = _toml_value(text, "refresh_token")
    if not refresh:
        _fail(
            "refresh_token topilmadi. Brauzerda kirish kerak:\n"
            "  cd services/maintenance-worker && npx wrangler login"
        )
    return _refresh(refresh)


def api(path: str, token: str):
    req = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": UA,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        if e.code in (401, 403):
            _fail(f"API ruxsat bermadi ({e.code}) — token scope'i yetarli emas: {body}")
        _fail(f"API xatosi {path} ({e.code}): {body}")
    except OSError as e:
        _fail(f"Tarmoq xatosi {path}: {e}")
    raise AssertionError("unreachable")


def main() -> int:
    # Test hook: never touch the network when a stub is supplied.
    if os.environ.get("CF_ROUTE_FORCE_UNREADABLE"):
        _fail("Soxta rejim: token yo'q deb hisoblanadi.")
    stub = os.environ.get("CF_ROUTE_STUB")
    if stub is not None:
        rows = [line for line in stub.splitlines() if line.strip()]
        if not rows:
            _fail("Soxta rejim: bo'sh stub — route yo'q.")
        print("\n".join(rows))
        return 0

    token = access_token()

    zones = {z["name"]: z["id"] for z in api("/zones?per_page=50", token)["result"]}
    for name in ZONES:
        if name not in zones:
            _fail(f"Zona topilmadi: {name}")

    rows = 0
    for name in ZONES:
        result = api(f"/zones/{zones[name]}/workers/routes", token)["result"]
        for route in result:
            # An absent field means Cloudflare's documented default of `false`.
            # Do not read it as "unknown": that would hide the exact failure
            # mode this script exists to catch.
            fail_open = route.get("request_limit_fail_open", False)
            print(f"{name}\t{route.get('pattern', '?')}\t{fail_open}")
            rows += 1

    if rows == 0:
        _fail(
            "Hech qanday Worker route topilmadi — route'lar o'chirilgan bo'lishi mumkin."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
