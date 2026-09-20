"""Judge latency — launch gate o'lchovi: p50 < 5 s, p95 < 15 s.

Manba: `docs/09-development-plan/README.md` § "Launch gate — public chiqishdan
oldin" (ochiq band) va ADR-0004 § Baholash mezonlari.

Nima o'lchanadi: yechim yuborilgandan yakuniy verdikt kelguncha o'tgan
**devor vaqti** — submit → Redis navbat → judge → nsjail → verdikt. Bu
foydalanuvchi ko'radigan raqam.

Nima o'lchanmaydi: navbat ostidagi guruhlanish. Standart rejim **ketma-ket**
(`LATENCY_SAMPLES` ta submit birin-ketin), ya'ni bu sof yo'lning vaqti. Gate
sharti ham aynan shuni so'raydi. Yuqori yuklama ostidagi o'lchov boshqa
savol — u alohida qaror bo'ladi.

⚠️ Muhit muhim: bu harness **qaysi muhitga qaratilsa, o'shaning** raqamini
beradi. Nightly uni CI stack'iga qaratadi — bu **regressiya bazasi** (GitHub
runner 4 yadroli, ishlab chiqarish mashinasi emas). Launch gate'dagi
**ishlab chiqarish** raqamini olish uchun o'sha harness'ni ishlab chiqarishga
qarating:

    API=https://rankwant.uz/api/v1 LATENCY_SAMPLES=20 \\
      python tests/latency/check_judge_latency.py

Har ikki holatda ham byudjet bir xil, ya'ni raqamlar taqqoslanadi.

Ishlatish (compose tarmog'i ichida, `docker-compose.ci.yml` → `latency`):

    docker compose -f docker-compose.yml -f docker-compose.ci.yml \\
      --profile latency run --rm latency

Atrof-muhit o'zgaruvchilari:

| O'zgaruvchi | Standart | Ma'nosi |
| --- | --- | --- |
| `API` | `http://api:8000/api/v1` | Qaysi API o'lchanadi |
| `LATENCY_SAMPLES` | `20` | O'lchanadigan submit soni |
| `LATENCY_WARMUP` | `2` | Qizdirish — o'lchanmaydi |
| `LATENCY_P50_MS` | `5000` | Gate byudjeti |
| `LATENCY_P95_MS` | `15000` | Gate byudjeti |
| `LATENCY_PROBLEM` | `a-plus-b` | Seed qilingan masala |
| `LATENCY_LANGUAGE` | `cpp23` | C++ — kompilyatsiya eng qimmat yo'l |
| `VERDICT_TIMEOUT` | `120` | Bitta verdict uchun chegara, soniya |

`LATENCY_SAMPLES=20` ataylab: p95 ma'noli bo'lishi uchun kamida 20 nuqta
kerak (nearest-rank bo'yicha p95 — 20 namunada eng yuqori qiymat).

Foiz hisobi **nearest-rank**: saralangan ro'yxatda `ceil(p/100 * n)`-element.
Interpolatsiya yo'q — kichik namuna uchun sodda va takrorlanadigan.
"""

from __future__ import annotations

import json
import math
import os
import secrets
import sys
import time
import urllib.error
import urllib.request

API = os.environ.get("API", "http://api:8000/api/v1")
SAMPLES = int(os.environ.get("LATENCY_SAMPLES", "20"))
WARMUP = int(os.environ.get("LATENCY_WARMUP", "2"))
BUDGET_P50_MS = int(os.environ.get("LATENCY_P50_MS", "5000"))
BUDGET_P95_MS = int(os.environ.get("LATENCY_P95_MS", "15000"))
PROBLEM = os.environ.get("LATENCY_PROBLEM", "a-plus-b")
LANGUAGE = os.environ.get("LATENCY_LANGUAGE", "cpp23")
DEADLINE = int(os.environ.get("VERDICT_TIMEOUT", "120"))

TERMINAL = ("", "PENDING", "RUNNING", "pending", "running")

SOLUTION = (
    "#include <cstdio>\n"
    'int main(){int a,b;scanf("%d %d",&a,&b);printf("%d\\n",a+b);return 0;}\n'
)

failures: list[str] = []


def request(path: str, data: dict | None = None, cookie: str = "") -> tuple:
    url = API + path
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


def percentile(values: list[float], pct: float) -> float:
    """Nearest-rank foiz. `values` bo'sh bo'lmasin."""
    ordered = sorted(values)
    rank = max(1, math.ceil(pct / 100 * len(ordered)))
    return ordered[rank - 1]


def login() -> str:
    suffix = f"{int(time.time())}{secrets.token_hex(3)}"
    creds = {
        "username": f"latency{suffix}",
        "email": f"latency{suffix}@rankwant.uz",
        # Runtime parol: repoda parolga o'xshash satr qoldirilmaydi.
        "password": secrets.token_urlsafe(24),
        "terms_accepted": True,
    }
    request("/auth/register/", creds)
    _, cookies = request(
        "/auth/login/", {"identifier": creds["username"], "password": creds["password"]}
    )
    if not cookies:
        raise RuntimeError("login sessiya bermadi")
    return "; ".join(c.split(";")[0] for c in cookies)


def one_submission(session: str) -> tuple[float, str]:
    """Bitta submit → verdikt. (millisekund, verdikt) qaytaradi."""
    started = time.monotonic()
    body, _ = request(
        "/attempts/",
        {"problem": PROBLEM, "language": LANGUAGE, "source_code": SOLUTION},
        cookie=session,
    )
    attempt_id = body["id"]
    end = time.monotonic() + DEADLINE
    while time.monotonic() < end:
        body, _ = request(f"/attempts/{attempt_id}/", cookie=session)
        verdict = body.get("verdict") or body.get("status") or ""
        if verdict not in TERMINAL:
            return (time.monotonic() - started) * 1000, verdict
        time.sleep(1)
    raise TimeoutError(f"{DEADLINE}s ichida verdikt kelmadi (attempt {attempt_id})")


def environment() -> None:
    """Raqamni talqin qilish uchun muhitni chop etadi.

    Runner yadrolari va yuklama boshqacha bo'lsa bir xil byudjet turli
    natija beradi — shuning uchun raqam bilan birga yozib qo'yiladi.
    """
    cores = os.cpu_count()
    try:
        load1 = f"{os.getloadavg()[0]:.2f}"
    except (OSError, AttributeError):
        load1 = "n/a"
    print(f"Muhit: {API} · {cores} yadro · load1 {load1}")


def main() -> int:
    print("Judge latency (launch gate: p50 < 5 s, p95 < 15 s):")
    environment()

    body, _ = request("/health/")
    if body.get("status") != "ok":
        print(f"  ✗ bog'liqlik javob bermayapti: {body.get('checks')}", file=sys.stderr)
        return 1

    session = login()
    for _ in range(WARMUP):
        one_submission(session)

    samples: list[float] = []
    verdicts: list[str] = []
    for index in range(1, SAMPLES + 1):
        elapsed_ms, verdict = one_submission(session)
        samples.append(elapsed_ms)
        verdicts.append(verdict)
        print(f"  {index:>3}/{SAMPLES}  {elapsed_ms:>8.0f} ms  {verdict}")

    if not samples:
        print("  ✗ namuna yig'ilmadi", file=sys.stderr)
        return 1

    p50 = percentile(samples, 50)
    p95 = percentile(samples, 95)
    print()
    print(f"Namuna: {len(samples)} · qizdirish: {WARMUP} · til: {LANGUAGE} · masala: {PROBLEM}")
    print(f"  p50 = {p50:.0f} ms   (byudjet {BUDGET_P50_MS} ms)")
    print(f"  p95 = {p95:.0f} ms   (byudjet {BUDGET_P95_MS} ms)")
    print(f"  min = {min(samples):.0f} ms · max = {max(samples):.0f} ms "
          f"· o'rtacha = {sum(samples) / len(samples):.0f} ms")

    wrong = sorted({v for v in verdicts if v != "AC"})
    if wrong:
        failures.append(f"AC bo'lmagan verdiktlar: {', '.join(wrong)} — muhit sog'lom emas")
    if p50 > BUDGET_P50_MS:
        failures.append(f"p50 {p50:.0f} ms > byudjet {BUDGET_P50_MS} ms")
    if p95 > BUDGET_P95_MS:
        failures.append(f"p95 {p95:.0f} ms > byudjet {BUDGET_P95_MS} ms")

    if failures:
        print("\nLatency YIQILDI:", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("\nLatency byudjetga sig'adi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
