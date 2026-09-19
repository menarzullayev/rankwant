"""Codeforces foydalanuvchilarini RankWant bazasiga sinxronlash — ADR-0026.

Manba: `user.ratedList` — BITTA so'rov, 974,498 yozuv, ~84 sekund.

`user.info` ATAYLAB ishlatilmaydi. O'lchandi: u `user.ratedList` bilan AYNAN
bir xil 16 maydonni qaytaradi (`set(user.ratedList[0]) ^ set(user.info[0]) == set()`),
lekin 1,949 so'rov talab qiladi (batch chegarasi 500 — 1000 da HTTP 414).
Ya'ni 1,949× ko'proq ish, nol qo'shimcha ma'lumot.

Ishlatish:
    python manage.py sync_codeforces --check
    python manage.py sync_codeforces --fetch
    python manage.py sync_codeforces --dry-run
    python manage.py sync_codeforces --apply

`--dry-run` va `--apply` bir xil tahlilni bajaradi; farqi faqat yozishda.
Ya'ni oldin `--dry-run` qilib ko'rish xavfsiz.

Idempotentlik: takroriy yurish dublikat yaratmaydi. Har yozuv `username`
(registrsiz) bo'yicha solishtiriladi va faqat o'zgargani yoziladi.

Xatolik va dublikat boshqaruvi:
  * Handle formati tekshiriladi (3–30 belgi, `[A-Za-z0-9_.-]`).
  * Feed ichidagi registrsiz dublikat aniqlanadi.
  * `--skip-long` 30 belgidan uzun handle'ni chetlab o'tadi. O'lchandi:
    974,498 ichida bittasi shunday (`73c0d7…7399`, 40 belgi — mashina
    hisobi), ya'ni `handles.MAX_LENGTH` shu bitta yozuv uchun
    kengaytirilmaydi (ADR-0026).
  * Yozish `--batch` bilan bo'linadi, har batch alohida tranzaksiya.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from argparse import ArgumentParser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.handles import MAX_LENGTH as HANDLE_MAX
from core.handles import skeleton
from core.models import User

#: Snapshot `MEDIA_ROOT` yonida emas — u foydalanuvchi kontenti uchun.
#: `BASE_DIR/.sync-cache` image ichida qoladi va konteyner almashganda
#: yo'qoladi; `--fetch` uni qayta yaratadi.
#:
#: ATAYLAB shunday: doimiy volume qo'yilmadi (HITL, 2026-09-19).
#: O'lchandi: keshsiz yuklash 34.4 s, keshli 0.0 s — ya'ni tejamkorlik
#: 33 sekund, kesh hajmi esa 331 MB. Sync qo'lda va kamdan-kam yuriladi,
#: shuning uchun bu nisbat volume va zaxira murakkabligini oqlamaydi.
#: Qayta ko'riladigan bo'lsa — avval shu ikki raqamni qayta o'lcha.
CACHE_DIR = Path(settings.BASE_DIR) / ".sync-cache"

#: `user.` prefiksi SHART. Busiz Codeforces 404 qaytaradi (HTML sahifa,
#: JSON emas) va buyruq "Codeforces API xatosi: HTTP 404" bilan yiqiladi.
#: O'lchandi (2026-09-19): `/api/ratedList` → 404, `/api/user.ratedList` → 200.
BASE_API = "https://codeforces.com/api/user.ratedList"
SNAPSHOT = CACHE_DIR / "ratedList.json"
MANIFEST = CACHE_DIR / "manifest.json"

#: Manzilning `user.` qismi yo'qolsa Codeforces 404 qaytaradi va sabab
#: tushunarsiz bo'ladi. O'lchandi (2026-09-19): prefikssiz manzil bir marta
#: yozilib qoldi, kesh esa xatoni 24 soat yashirdi. Shuning uchun import
#: paytida tekshiriladi — noto'g'ri manzil bilan buyruq umuman yurmaydi.
if "/api/user.ratedList" not in BASE_API:  # pragma: no cover — himoya
    raise RuntimeError(
        f"BASE_API noto'g'ri: {BASE_API!r}. "
        "Codeforces manzili `/api/user.ratedList` bo'lishi shart "
        "(`user.` prefiksisiz 404 qaytaradi)."
    )

#: Codeforces davlat nomi → ISO 3166-1 alpha-2 (`core/country_map.py`).
#: Import qilinmasa xarita bo'sh qoladi va har bir davlat nomi "noma'lum"
#: bo'lib hisobotga tushadi — jim o'tkazib yuborilmaydi.
try:  # pragma: no cover — muhitga bog'liq
    from core.country_map import COUNTRY_MAP
except ImportError:  # pragma: no cover
    COUNTRY_MAP = {}


@dataclass
class Report:
    fetched: int = 0
    parsed: int = 0
    skipped_long: int = 0
    bad_handle: int = 0
    dup_in_feed: int = 0
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    countries_mapped: int = 0
    countries_unknown: set[str] = field(default_factory=set)
    fetch_sec: float = 0.0
    parse_sec: float = 0.0
    write_sec: float = 0.0
    errors: list[str] = field(default_factory=list)

    def show(self, out) -> None:
        out("")
        out("=" * 66)
        out("CODEFORCES SINXRONLASH HISOBOTI")
        out("=" * 66)
        out(f"  Yuklab olindi          : {self.fetched:>10,}")
        out(f"  Tahlil qilindi         : {self.parsed:>10,}")
        out(f"  Uzun handle (o'tkazdi) : {self.skipped_long:>10,}")
        out(f"  Noto'g'ri handle       : {self.bad_handle:>10,}")
        out(f"  Oqimdagi dublikat      : {self.dup_in_feed:>10,}")
        out(f"  Yaratildi              : {self.created:>10,}")
        out(f"  Yangilandi             : {self.updated:>10,}")
        out(f"  O'zgarmagan            : {self.unchanged:>10,}")
        out(f"  Davlat moslandi        : {self.countries_mapped:>10,}")
        out(f"  Noma'lum davlat        : {len(self.countries_unknown):>10}")
        if self.countries_unknown:
            out(f"     namuna: {sorted(self.countries_unknown)[:8]}")
        out("-" * 66)
        out(f"  Yuklash                : {self.fetch_sec:>10.1f} s")
        out(f"  Tahlil                 : {self.parse_sec:>10.1f} s")
        out(f"  Yozish                 : {self.write_sec:>10.1f} s")
        if self.errors:
            out(f"  XATOLAR ({len(self.errors)}):")
            for e in self.errors[:5]:
                out(f"     - {e}")
        out("=" * 66)


def valid_handle(h: Any, max_len: int = HANDLE_MAX) -> bool:
    """O'lchandi: Codeforces handle 3–40 belgi, `[A-Za-z0-9_.-]`."""
    if not isinstance(h, str) or not (3 <= len(h) <= 40):
        return False
    if len(h) > max_len:
        return False
    return all(c.isalnum() or c in "_.-" for c in h)


#: Codeforces'dagi 10 unvon darajasi. O'lchandi: 974,498 yozuvda
#: `rank` faqat shu qiymatlardan birini oladi — IKKI istisnodan tashqari.
TIERS = frozenset(
    {
        "newbie",
        "pupil",
        "specialist",
        "expert",
        "candidate master",
        "master",
        "international master",
        "grandmaster",
        "international grandmaster",
        "legendary grandmaster",
    }
)


def clean_title(value: Any, handle: str, rep: Report) -> str:
    """Unvon nomini tozalaydi.

    O'lchandi: 974,498 yozuvdan 2 tasida Codeforces `rank` maydoniga unvon
    o'rniga TAXALLUSni yozgan — `jiangly` → `"jiangly"`, `tourist` →
    `"tourist"` (ikkisi ham legendary grandmaster). Bu yuqoridagi xato,
    va u tozalanmasa `rank_title` ustunida taxallus paydo bo'lardi.

    Noma'lum qiymat tashlanadi va hisobotga yoziladi — jim o'tkazilmaydi.
    """
    if not isinstance(value, str) or not value:
        return ""
    low = value.strip().casefold()
    if low in TIERS:
        return low[:40]
    rep.errors.append(f"noma'lum unvon: {handle} -> {value!r}")
    return ""


def to_epoch(value: Any) -> datetime | None:
    """Unix timestamp → timezone-aware datetime (yoki `None`)."""
    if not isinstance(value, int) or value <= 0:
        return None
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    except (OSError, OverflowError, ValueError):
        return None


class Command(BaseCommand):
    help = "Codeforces reyting ro'yxatini RankWant bazasiga sinxronlaydi (ADR-0026)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--check", action="store_true", help="Muhitni tekshirish")
        parser.add_argument("--fetch", action="store_true", help="Manbani yuklab olish")
        parser.add_argument(
            "--force-fetch", action="store_true", help="Keshni e'tiborsiz qoldirib qayta yuklash"
        )
        parser.add_argument("--dry-run", action="store_true", help="Yozmasdan hisobot")
        parser.add_argument("--apply", action="store_true", help="Bazaga yozish")
        parser.add_argument(
            "--batch", type=int, default=5000, help="Yozish batch hajmi (default 5000)"
        )
        parser.add_argument(
            "--limit", type=int, default=0, help="Faqat N ta yozuv (sinov uchun)"
        )
        parser.add_argument(
            "--skip-long",
            action="store_true",
            default=True,
            help="30 belgidan uzun handle'ni o'tkazib yuborish (default: yoqilgan)",
        )
        parser.add_argument(
            "--no-skip-long",
            dest="skip_long",
            action="store_false",
            help="Uzun handle'ni ham olish (baza `varchar(150)`, lekin validator rad etadi)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if options["check"]:
            self.cmd_check()
            return

        do_write = options["apply"]
        if not (do_write or options["dry_run"] or options["fetch"] or options["force_fetch"]):
            raise CommandError("Amalni tanlang: --check | --fetch | --dry-run | --apply")

        if not COUNTRY_MAP:
            self.stderr.write(
                "  ⚠️  `core.country_map` topilmadi — davlat kodlari `''` bo'ladi"
            )

        rep = Report()

        # ── 1. Manbani olish ──────────────────────────────────────────
        body, rep.fetch_sec = self.get_snapshot(force=options["force_fetch"] or options["fetch"])

        # ── 2. Tahlil ────────────────────────────────────────────────
        self.stdout.write("  Tahlil qilinmoqda...")
        records = self.parse(body, rep, skip_long=options["skip_long"])
        limit = options["limit"]
        if limit:
            records = records[:limit]
            self.stdout.write(f"  ⚠️  --limit {limit:,}: faqat shu qism ishlanadi")
        self.stdout.write(f"  {len(records):,} yozuv tayyor")

        # ── 3. Baza bilan solishtirish va yozish ─────────────────────
        if do_write or options["dry_run"]:
            self.sync(records, rep, write=do_write, batch=options["batch"])

        rep.show(self.stdout.write)
        if SNAPSHOT.exists():
            self.stdout.write("")
            self.stdout.write(f"  Manba snapshot: {SNAPSHOT}")
            self.stdout.write(f"  Manba hajmi   : {SNAPSHOT.stat().st_size:,} bayt")

    # ── Yordamchilar ─────────────────────────────────────────────────

    def cmd_check(self) -> None:
        self.stdout.write("Muhit tekshiruvi")
        self.stdout.write(f"  Snapshot       : {SNAPSHOT}")
        self.stdout.write(f"  Snapshot mavjud: {SNAPSHOT.exists()}")
        if SNAPSHOT.exists():
            self.stdout.write(f"  Snapshot hajmi : {SNAPSHOT.stat().st_size:,} bayt")
        if MANIFEST.exists():
            m = json.loads(MANIFEST.read_text(encoding="utf-8"))
            self.stdout.write(f"  Oxirgi yuklash  : {m.get('fetched_at')}")
            self.stdout.write(f"  sha256          : {m.get('sha256', '')[:16]}…")
        self.stdout.write(f"  Davlat xaritasi: {len(COUNTRY_MAP)} ta kod")
        self.stdout.write(f"  Handle chegarasi: {HANDLE_MAX} belgi")
        self.stdout.write(f"  Bazadagi User  : {User.objects.count():,}")

    def get_snapshot(self, force: bool) -> tuple[bytes, float]:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        if SNAPSHOT.exists() and not force:
            age_h = (time.time() - SNAPSHOT.stat().st_mtime) / 3600
            if age_h < 24:
                self.stdout.write(f"  Kesh: {SNAPSHOT.name} ({age_h:.1f} soat oldin)")
                return SNAPSHOT.read_bytes(), 0.0

        url = f"{BASE_API}?activeOnly=false&includeRetired=true"
        self.stdout.write(f"  Yuklanmoqda: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "RankWant-Sync/1.0"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                body = r.read()
        except urllib.error.HTTPError as e:
            raise CommandError(f"Codeforces API xatosi: HTTP {e.code}") from e
        except urllib.error.URLError as e:
            raise CommandError(f"Tarmoq xatosi: {e.reason}") from e
        el = time.time() - t0

        SNAPSHOT.write_bytes(body)
        MANIFEST.write_text(
            json.dumps(
                {
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "bytes": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "source": url,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        self.stdout.write(f"  Saqlandi: {len(body):,} bayt, {el:.1f} s")
        return body, el

    def parse(self, body: bytes, rep: Report, skip_long: bool) -> list[dict]:
        t0 = time.time()
        data = json.loads(body)
        if data.get("status") != "OK":
            raise CommandError(f"API status: {data.get('status')} — {data.get('comment')}")

        raw = data["result"]
        rep.fetched = len(raw)
        out: list[dict] = []
        seen: set[str] = set()

        for rec in raw:
            handle = rec.get("handle", "")
            if not isinstance(handle, str) or not (3 <= len(handle) <= 40):
                rep.bad_handle += 1
                continue
            if len(handle) > HANDLE_MAX:
                if skip_long:
                    rep.skipped_long += 1
                    continue
                rep.bad_handle += 1
                continue
            if not all(c.isalnum() or c in "_.-" for c in handle):
                rep.bad_handle += 1
                continue

            key = handle.casefold()
            if key in seen:
                rep.dup_in_feed += 1
                continue
            seen.add(key)

            cname = rec.get("country") or ""
            iso = COUNTRY_MAP.get(cname, "")
            if cname:
                if iso:
                    rep.countries_mapped += 1
                else:
                    rep.countries_unknown.add(cname)

            out.append(
                {
                    "username": handle,
                    # `bulk_create` `save()` ni chaqirmaydi, ya'ni skelet
                    # SHU YERDA hisoblanadi — `uniq_username_skeleton`
                    # cheklovi aks holda buziladi.
                    "username_skeleton": skeleton(handle),
                    "display_name": " ".join(
                        p for p in (rec.get("firstName") or "", rec.get("lastName") or "") if p
                    )[:100],
                    "country": iso,
                    "city": (rec.get("city") or "")[:100],
                    "school": (rec.get("organization") or "")[:150],
                    "rating_contest": rec.get("rating") or 1400,
                    "max_rating_contest": rec.get("maxRating"),
                    "contribution": rec.get("contribution") or 0,
                    "last_seen_at": to_epoch(rec.get("lastOnlineTimeSeconds")),
                    "imported_joined_at": to_epoch(rec.get("registrationTimeSeconds")),
                    "avatar_url": (rec.get("avatar") or "")[:200],
                    "rank_title": clean_title(rec.get("rank"), handle, rep),
                    "max_rank_title": clean_title(rec.get("maxRank"), handle, rep),
                    "friend_count": rec.get("friendOfCount") or 0,
                    "title_photo_url": (rec.get("titlePhoto") or "")[:200],
                }
            )

        rep.parsed = len(out)
        rep.parse_sec = time.time() - t0
        return out

    #: Yoziladigan maydonlar. `date_joined` ATAYLAB yo'q: u RankWant'dagi
    #: ro'yxat sanasi, Codeforces'dagi emas (ADR-0026). Manbadagi sana
    #: faqat YANGI yozuvda `date_joined` o'rniga qo'yiladi.
    UPDATE_FIELDS = (
        "username_skeleton",
        "display_name",
        "country",
        "city",
        "school",
        "rating_contest",
        "max_rating_contest",
        "contribution",
        "last_seen_at",
        "avatar_url",
        "rank_title",
        "max_rank_title",
        "friend_count",
        "title_photo_url",
    )

    def sync(self, records: list[dict], rep: Report, write: bool, batch: int) -> None:
        """Idempotent yozish: mavjudni yangilaydi, yo'qni yaratadi.

        Mavjud qatorlar BITTA so'rovda olinadi — 974,498 ta
        `update_or_create` (har biri alohida so'rov) o'rniga.
        """
        t0 = time.time()
        self.stdout.write("  Baza bilan solishtirilmoqda...")

        existing = {
            u.username.casefold(): u
            for u in User.objects.filter(
                username__in=[r["username"] for r in records]
            ).only("id", "username", *self.UPDATE_FIELDS)
        }
        self.stdout.write(f"  Bazada mavjud: {len(existing):,}")

        to_create: list[User] = []
        to_update: list[User] = []
        now = datetime.now(tz=timezone.utc)

        for rec in records:
            obj = existing.get(rec["username"].casefold())
            if obj is None:
                rep.created += 1
                if write:
                    to_create.append(
                        User(
                            username=rec["username"],
                            username_skeleton=rec["username_skeleton"],
                            display_name=rec["display_name"],
                            country=rec["country"],
                            city=rec["city"],
                            school=rec["school"],
                            rating_contest=rec["rating_contest"],
                            max_rating_contest=rec["max_rating_contest"],
                            contribution=rec["contribution"],
                            last_seen_at=rec["last_seen_at"],
                            # Manbadagi ro'yxat sanasi — import sanasi emas.
                            date_joined=rec["imported_joined_at"] or now,
                            avatar_url=rec["avatar_url"],
                            rank_title=rec["rank_title"],
                            max_rank_title=rec["max_rank_title"],
                            friend_count=rec["friend_count"],
                            title_photo_url=rec["title_photo_url"],
                            # Sinxron qator — KIRA OLMAYDIGAN hisob.
                            # Pochta bo'sh, parol unusable (ADR-0026).
                            email="",
                            is_active=True,
                        )
                    )
                continue

            changed = any(getattr(obj, f, None) != rec.get(f) for f in self.UPDATE_FIELDS)
            if changed:
                rep.updated += 1
                if write:
                    for f in self.UPDATE_FIELDS:
                        setattr(obj, f, rec.get(f))
                    to_update.append(obj)
            else:
                rep.unchanged += 1

        if write:
            for i in range(0, len(to_create), batch):
                chunk = to_create[i : i + batch]
                with transaction.atomic():
                    User.objects.bulk_create(chunk, batch_size=batch)
            if to_update:
                with transaction.atomic():
                    User.objects.bulk_update(to_update, list(self.UPDATE_FIELDS), batch_size=batch)

        rep.write_sec = time.time() - t0
        mode = "Yozildi" if write else "DRY-RUN (yozilmadi)"
        self.stdout.write(
            f"  {mode}: create={rep.created:,} update={rep.updated:,} same={rep.unchanged:,}"
        )
