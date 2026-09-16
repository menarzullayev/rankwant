"""5 sahifadan xom (RAW) ma'lumot yig'adi — CDP proxy orqali.

Har sahifa uchun: to'liq HTML, tuzilma JSON'i, skrinshot.
Natija: docs/03-market-research/audit/<NN>-<nom>/ (shu skriptning ota papkasi).
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

PROXY = "http://127.0.0.1:3456"
# Writes next to the imported audit instead of C:\Users\nsn\rankwant-audit, the
# machine-specific folder the data was copied from (removed on 2026-09-17).
OUT = Path(__file__).resolve().parent.parent
EXTRACT = Path(__file__).with_name("audit-extract.js").read_text(encoding="utf-8")

PAGES = [
    ("01-robocontest-register", "https://robocontest.uz/register"),
    ("02-robocontest-login", "https://robocontest.uz/login"),
    ("03-kep-login", "https://kep.uz/login?returnUrl=%2F"),
    ("04-rankwant-login", "https://rankwant.uz/login"),
    ("05-rankwant-register", "https://rankwant.uz/register"),
]


def get(path: str) -> str:
    with urllib.request.urlopen(PROXY + path, timeout=120) as r:
        return r.read().decode("utf-8", "replace")


def post(path: str, body: str) -> str:
    req = urllib.request.Request(
        PROXY + path, data=body.encode("utf-8"), method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", "replace")


def value(raw: str):
    """Proxy `{"value": ...}` qaytaradi — ichini ajratib olamiz."""
    data = json.loads(raw)
    return data.get("value", data)


OUT.mkdir(parents=True, exist_ok=True)
summary = []

for name, url in PAGES:
    folder = OUT / name
    folder.mkdir(exist_ok=True)
    print(f"→ {name}")

    target = json.loads(
        get("/new?url=" + urllib.parse.quote(url, safe=""))
    )["targetId"]

    # Sahifa to'liq yuklanishini kutamiz: SPA'lar (kep.uz) JS bilan
    # chiziladi, ya'ni darhol o'qish bo'sh natija berardi.
    time.sleep(12)

    info = json.loads(get(f"/info?target={target}"))
    (folder / "structure.json").write_text(
        json.dumps(json.loads(value(post(f"/eval?target={target}", EXTRACT))),
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    html = value(post(f"/eval?target={target}", "document.documentElement.outerHTML"))
    (folder / "page.html").write_text(html, encoding="utf-8")

    try:
        get(f"/screenshot?target={target}&file={(folder / 'shot.png').as_posix()}")
        shot = True
    except Exception as exc:  # noqa: BLE001 — skrinshot ixtiyoriy
        print(f"   skrinshot xato: {exc}")
        shot = False

    get(f"/close?target={target}")

    struct = json.loads((folder / "structure.json").read_text(encoding="utf-8"))
    summary.append(
        {
            "folder": name,
            "url": struct.get("url"),
            "title": struct.get("title"),
            "lang": struct.get("lang"),
            "htmlKB": round(len(html.encode("utf-8")) / 1024),
            "nodes": struct.get("counts", {}).get("nodes"),
            "fields": struct.get("counts", {}).get("fields"),
            "buttons": struct.get("counts", {}).get("buttons"),
            "transferKB": struct.get("perf", {}).get("transferKB"),
            "resources": struct.get("perf", {}).get("resources"),
            "externalHosts": list((struct.get("externalHosts") or {}).keys()),
            "shot": shot,
            "info": info.get("title"),
        }
    )
    print(f"   ✓ {struct.get('title')!r} · HTML {summary[-1]['htmlKB']} KB")

(OUT / "summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"\nTayyor: {OUT}")
