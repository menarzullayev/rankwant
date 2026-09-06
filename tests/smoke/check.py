"""Smoke — ko'tarilgan stack asosiy yo'llarda ishlayaptimi.

Compose TARMOG'I ICHIDA ishlaydi (host portlari kerak emas). Eng muhimi
oxirgi tekshiruv: submit → Redis → judge → verdict. Qolgan hamma test
o'tib, shu yo'l uzilgan bo'lsa, platforma ishlamaydi.

Ishlatish:  docker compose ... run --rm smoke
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

API = os.environ.get("API", "http://api:8000/api/v1")
WEB = os.environ.get("WEB", "http://web:3000")
DEADLINE = int(os.environ.get("VERDICT_TIMEOUT", "120"))

SOLUTION = "#include <cstdio>\nint main(){int a,b;scanf(\"%d %d\",&a,&b);printf(\"%d\\n\",a+b);return 0;}\n"

failures: list[str] = []


def check(name: str, fn) -> object | None:
    try:
        result = fn()
    except Exception as exc:  # noqa: BLE001 — smoke har xatoni hisobot qiladi
        failures.append(f"{name}: {type(exc).__name__}: {exc}")
        print(f"  ✗ {name}")
        return None
    print(f"  ✓ {name}")
    return result


def request(path: str, data: dict | None = None, cookie: str = "", base: str = "") -> tuple:
    url = (base or API) + path
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method="POST" if data else "GET")
    if body:
        req.add_header("Content-Type", "application/json")
    if cookie:
        req.add_header("Cookie", cookie)
        # Sessiya bilan yuborilgan POST da DRF CSRF talab qiladi
        token = dict(c.split("=", 1) for c in cookie.split("; ") if "=" in c).get("csrftoken")
        if token and body:
            req.add_header("X-CSRFToken", token)
            req.add_header("Referer", url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode()
        parsed = json.loads(raw) if raw.startswith(("{", "[")) else raw
        return parsed, resp.headers.get_all("Set-Cookie") or []


def main() -> int:
    print("Smoke:")

    problems = check("API masalalar ro'yxatini beradi", lambda: request("/problems/")[0])
    if problems and not problems.get("results"):
        failures.append("masalalar ro'yxati bo'sh — seed ishlamagan")

    check("OpenAPI sxemasi ochiladi", lambda: request("/schema/?format=json")[0])
    check("Qvant do'koni ochiq", lambda: request("/qvant/shop/")[0])

    def web_ssr() -> str:
        html, _ = request("/problems", base=WEB)
        if "A + B" not in html:
            raise AssertionError("SSR masala nomini render qilmadi — web→api uzilgan")
        return html

    check("Web SSR api'dan ma'lumot oladi", web_ssr)

    # ── Kritik yo'l: submit → judge → verdict ────────────────────────
    suffix = str(int(time.time()))
    creds = {
        "username": f"smoke{suffix}",
        "email": f"smoke{suffix}@rankwant.uz",
        "password": "SmokeTest12345",
    }

    check("Ro'yxatdan o'tish", lambda: request("/auth/register/", creds)[0])

    # Register sessiya ochmaydi — alohida login kerak
    cookies = check(
        "Login sessiya beradi",
        lambda: request(
            "/auth/login/", {"username": creds["username"], "password": creds["password"]}
        )[1],
    )
    if not cookies:
        return report()
    session = "; ".join(c.split(";")[0] for c in cookies)

    check("Qvant questlari (autentifikatsiya talab qiladi)",
          lambda: request("/qvant/quests/", cookie=session)[0])

    def submit() -> int:
        payload = {"problem": "a-plus-b", "language": "cpp23", "source_code": SOLUTION}
        body, _ = request("/attempts/", payload, cookie=session)
        return body["id"]

    attempt_id = check("Submit qabul qilindi", submit)
    if attempt_id is None:
        return report()

    def verdict() -> str:
        end = time.time() + DEADLINE
        last = ""
        while time.time() < end:
            body, _ = request(f"/attempts/{attempt_id}/", cookie=session)
            last = body.get("verdict") or body.get("status") or ""
            if last and last not in ("PENDING", "RUNNING", "pending", "running"):
                return last
            time.sleep(2)
        raise TimeoutError(f"{DEADLINE}s ichida verdict kelmadi (oxirgi holat: {last!r})")

    got = check(f"Verdict keldi (judge ishlayapti, ≤{DEADLINE}s)", verdict)
    if got is not None and got != "AC":
        failures.append(f"to'g'ri yechim {got} oldi, AC kutilgandi")

    return report()


def report() -> int:
    if failures:
        print("\nSmoke YIQILDI:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("\nSmoke o'tdi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
