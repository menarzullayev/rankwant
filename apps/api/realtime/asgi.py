"""`realtime` xizmatining ASGI ilovasi — ADR-0029 §5.

⚠️ **Nega Django middleware ishlatilmaydi.** `api` ning middleware'i sinxron
(`SessionMiddleware`, `AuthenticationMiddleware`, …). Django sinxron
middleware'ni asinxron view bilan bog'lashda view'ni `async_to_sync` orqali
o'raydi, ya'ni u **boshqa event loop**da ishga tushadi. Natijada
`StreamingHttpResponse` ning asinxron generatori yopilgan loop'ga bog'lanib
qoladi va oqim `RuntimeError: Event loop is closed` bilan uziladi.

Shu sababli bu ilova **tor**: middleware zanjiri yo'q, faqat ikki yo'l
(`/api/v1/events/`, `/api/v1/realtime/health/`), qolganiga 404. Sessiya
Django'ning O'Z `SessionStore` i orqali tekshiriladi — ya'ni auth mexanizmi
bitta bo'lib qoladi, faqat chaqiruv nuqtasi boshqa (ADR-0029 §7).
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from http.cookies import SimpleCookie
from typing import Any

from asgiref.sync import sync_to_async
from django.conf import settings
from redis.asyncio import Redis

from realtime import bus

log = logging.getLogger(__name__)

EVENTS_PATH = "/api/v1/events/"
ATTEMPT_EVENTS_RE = re.compile(r"^/api/v1/attempts/(\d+)/events/$")
HEALTH_PATH = "/api/v1/realtime/health/"
REPORT_PATH = "/api/v1/realtime/report/"

#: Heartbeat oralig'i. ⚠️ Sabab aniq: Cloudflare proksisi bo'sh turgan
#: ulanishni ~100 soniyada uzadi, shuning uchun 15 s — xavfsiz zaxira
#: bilan. Bu **izoh** (`:` bilan boshlanadi), hodisa emas: mijoz uni
#: `message` deb o'qimaydi.
HEARTBEAT_S = 15.0

#: Mijoz qayta ulanish oralig'i (ms). Server boshqaradi — brauzer
#: standarti 3000 ms, lekin u Redis/API ni bekorga uyg'otadi.
RETRY_MS = 5000

#: Masala slug — faqat ochiq urinishlar jadvalidagi masalalar.
_PROBLEM_SLUG = re.compile(r"^[a-z0-9-]{1,120}$")

#: Bitta ulanish navbatining chegarasi. ⚠️ Cheksiz bufer — OOM ning eng
#: qisqa yo'li: sekin iste'molchi butun jarayonni yeb qo'yardi.
QUEUE_MAX = 256

#: Shu sondan ko'p hodisa ketma-ket yuborilsa ulanish yopiladi.
#: Sabab bir xil: sekin mijozni ushlab turish emas, qo'yib yuborish.
MAX_EVENTS_PER_CONNECTION = 10_000

#: Foydalanuvchi uchun ochiq ulanish chegarasi (ADR-0029 §8). Oshsa
#: eng eski ulanish yopiladi. Redis'da sanaladi — bir nechta worker
#: bo'lsa ham umumiy.
MAX_CONNECTIONS_PER_USER = 5
#: Kalitning umri. ⚠️ Jarayon yiqilsa `DECR` bajarilmaydi va hisob
#: abadiy shishib qolardi; TTL shuni tozalaydi. Ya'ni hisob **oxir-oqibat
#: izchil**, aniq emas — va bu ataylab.
SLOT_TTL_S = 120

#: Jarayon bo'yicha umumiy chegara. ⚠️ Bu **jarayon** chegarasi, xizmat
#: emas: N worker bilan amaldagi chegara N × shu son. Umumiy hisob
#: Redis'da yuritilmaydi, chunki har ulanish uchun qo'shimcha
#: round-trip qimmat va bu son konfiguratsiya uchun yetarli.
MAX_CONNECTIONS_PER_PROCESS = 2000

_HEADERS = (
    (b"content-type", b"text/event-stream; charset=utf-8"),
    (b"cache-control", b"no-store"),
    #: Proksi buferini o'chiradi. Usiz nginx/Cloudflare javobni
    #: to'plab, oqim «hech narsa kelmayapti» holatiga tushardi.
    (b"x-accel-buffering", b"no"),
    (b"connection", b"keep-alive"),
)

#: Jarayon metrikalari (ADR-0029 §11). Prometheus yo'q, lekin talab
#: qilingan raqamlar shu yerda yuritiladi va `/health/` orqali o'qiladi.
_stats: dict[str, int] = {
    "connections_active": 0,
    "connections_total": 0,
    "connections_rejected": 0,
    "events_delivered": 0,
    "events_replayed": 0,
    "resync_sent": 0,
    "heartbeats": 0,
    "redis_errors": 0,
    "slow_consumer_closed": 0,
    "client_reconnects_reported": 0,
}


def _client() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


def _cookie(scope: dict[str, Any], name: str) -> str | None:
    for key, value in scope.get("headers", []):
        if key == b"cookie":
            jar = SimpleCookie()
            jar.load(value.decode("latin-1"))
            morsel = jar.get(name)
            if morsel is not None:
                return morsel.value
    return None


def _session_user_id(scope: dict[str, Any]) -> int | None:
    """Sessiyadan foydalanuvchi ID sini o'qiydi. Sinxron — `sync_to_async`.

    ⚠️ Kanal nomi shu yerdan olinadi, **mijoz parametridan EMAS**: aks
    holda `?user_id=` bilan begona odamning verdiktini kuzatish mumkin
    bo'lardi (ADR-0029 §7, IDOR).
    """
    from django.contrib.sessions.backends.cached_db import SessionStore

    key = _cookie(scope, settings.SESSION_COOKIE_NAME)
    if not key:
        return None
    session = SessionStore(session_key=key)
    try:
        raw = session.get("_auth_user_id")
    except Exception:
        return None
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _last_event_id(scope: dict[str, Any]) -> int:
    """`Last-Event-ID` — brauzer qayta ulanganda o'zi yuboradi."""
    for key, value in scope.get("headers", []):
        if key == b"last-event-id":
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0
    return 0


def _query(scope: dict[str, Any]) -> dict[str, str]:
    raw = scope.get("query_string", b"").decode("latin-1")
    out: dict[str, str] = {}
    for pair in raw.split("&"):
        if not pair:
            continue
        name, _, value = pair.partition("=")
        out[name] = value
    return out


def _cors_headers(scope: dict[str, Any]) -> tuple[tuple[bytes, bytes], ...]:
    """Split-stack dev: brauzer `:8312`, SSE `:8302` — `Access-Control-*` shart."""
    origin: str | None = None
    for key, value in scope.get("headers", []):
        if key == b"origin":
            origin = value.decode("latin-1")
            break
    if not origin:
        return ()
    allowed = [o.strip() for o in getattr(settings, "CORS_ALLOWED_ORIGINS", None) or []]
    if origin not in allowed:
        return ()
    return (
        (b"access-control-allow-origin", origin.encode("latin-1")),
        (b"access-control-allow-credentials", b"true"),
    )


async def _send(
    scope: dict[str, Any],
    status: int,
    body: bytes = b"",
    extra: tuple[tuple[bytes, bytes], ...] = (),
) -> None:
    await scope["send"](
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"text/plain; charset=utf-8"),
                *_cors_headers(scope),
                *extra,
            ],
        }
    )
    await scope["send"]({"type": "http.response.body", "body": body})


async def _reserve_slot(client: Redis, user_id: int) -> bool:
    key = f"rw:rt:conns:{user_id}"
    try:
        current = await client.incr(key)
        await client.expire(key, SLOT_TTL_S)
        if int(current) > MAX_CONNECTIONS_PER_USER:
            #: Rad etilgan urinish ham INCR qilgan — qaytarib olmasak 503 abadiy.
            await client.decr(key)
            return False
        return True
    except Exception:
        _stats["redis_errors"] += 1
        return False


async def _release_slot(client: Redis, user_id: int) -> None:
    key = f"rw:rt:conns:{user_id}"
    try:
        await client.decr(key)
    except Exception:
        pass


async def _heartbeat_slot(client: Redis, user_id: int) -> None:
    """Ulanish tirik ekan hisob kalitining umrini uzaytiradi."""
    try:
        await client.expire(f"rw:rt:conns:{user_id}", SLOT_TTL_S)
    except Exception:
        pass


async def _events(scope: dict[str, Any]) -> None:
    send = scope["send"]
    receive = scope["receive"]

    user_id = await sync_to_async(_session_user_id, thread_sensitive=True)(scope)
    if user_id is None:
        # ⚠️ Anonim so'rovga YARIM OCHIQ oqim berilmaydi — 401 darhol.
        await _send(scope, 401, b"authentication required\n")
        return

    if _stats["connections_active"] >= MAX_CONNECTIONS_PER_PROCESS:
        _stats["connections_rejected"] += 1
        await _send(scope, 503, b"connection limit reached\n", ((b"retry-after", b"30"),))
        return

    client = _client()
    if not await _reserve_slot(client, user_id):
        _stats["connections_rejected"] += 1
        await _send(scope, 503, b"too many connections\n", ((b"retry-after", b"30"),))
        await client.aclose()
        return

    channels = [bus.user_channel(user_id)]
    query = _query(scope)
    contest = query.get("contest", "")
    if contest.isdigit():
        channels.append(bus.standings_channel(int(contest)))
    problem = query.get("problem", "")
    if _PROBLEM_SLUG.fullmatch(problem):
        channels.append(bus.problem_channel(problem))

    last_id = _last_event_id(scope)
    pubsub = client.pubsub()
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=QUEUE_MAX)
    slow = asyncio.Event()

    async def pump() -> None:
        """Redis xabarlarini navbatga o'tkazadi."""
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                try:
                    queue.put_nowait(message["data"])
                except asyncio.QueueFull:
                    #: Sekin iste'molchi: cheksiz buferdan ko'ra uzish
                    #: yaxshi (ADR-0029 §8).
                    slow.set()
                    return
        except asyncio.CancelledError:
            raise
        except Exception:
            _stats["redis_errors"] += 1
            slow.set()

    async def watch_disconnect() -> None:
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return

    _stats["connections_active"] += 1
    _stats["connections_total"] += 1
    started = time.monotonic()
    delivered = 0
    close_reason = "client_closed"
    pump_task: asyncio.Task[None] | None = None
    watch_task: asyncio.Task[None] | None = None

    try:
        await pubsub.subscribe(*channels)
        await send({"type": "http.response.start", "status": 200, "headers": list(_HEADERS) + list(_cors_headers(scope))})

        async def write(chunk: str) -> None:
            await send({"type": "http.response.body", "body": chunk.encode(), "more_body": True})

        await write(f"retry: {RETRY_MS}\n\n")
        await write(": connected\n\n")

        #: Replay (ADR-0029 §9). Bufer yetarli bo'lmasa `resync` —
        #: mijoz holatni REST dan qayta o'qiydi. Oqim hech qachon
        #: «haqiqat manbasi» bo'lmaydi.
        replayed: list[dict[str, Any]] = []
        gap = False
        if last_id:
            for channel in channels:
                try:
                    items, channel_gap = await bus.replay_after(client, channel, last_id)
                except Exception:
                    _stats["redis_errors"] += 1
                    continue
                replayed.extend(items)
                gap = gap or channel_gap
            replayed.sort(key=lambda item: item["id"])
            for item in replayed:
                await write(_frame(item))
                _stats["events_replayed"] += 1
            if gap:
                await write('event: resync\ndata: {"reason":"buffer_expired"}\n\n')
                _stats["resync_sent"] += 1

        pump_task = asyncio.create_task(pump())
        watch_task = asyncio.create_task(watch_disconnect())

        while True:
            if slow.is_set():
                close_reason = "slow_consumer"
                _stats["slow_consumer_closed"] += 1
                break
            if watch_task.done():
                close_reason = "client_closed"
                break
            try:
                raw = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_S)
            except TimeoutError:
                await write(": ping\n\n")
                _stats["heartbeats"] += 1
                await _heartbeat_slot(client, user_id)
                continue
            await write(raw)
            delivered += 1
            _stats["events_delivered"] += 1
            if delivered >= MAX_EVENTS_PER_CONNECTION:
                #: Juda uzoq yashagan ulanishni yangilash: mijoz `retry`
                #: orqali qaytadi va replay orqali hech narsa yo'qolmaydi.
                close_reason = "recycled"
                break
    except asyncio.CancelledError:
        close_reason = "server_cancelled"
        raise
    except Exception:
        close_reason = "redis_error"
        _stats["redis_errors"] += 1
        log.exception("oqim xatosi: user=%s", user_id)
    finally:
        for task in (pump_task, watch_task):
            if task is not None:
                task.cancel()
        try:
            await pubsub.unsubscribe()
            #: redis-py `aclose` ni tip bilan e'lon qilmagan.
            await pubsub.aclose()  # type: ignore[no-untyped-call]
        except Exception:
            pass
        await _release_slot(client, user_id)
        await client.aclose()  # type: ignore[no-untyped-call]
        _stats["connections_active"] -= 1
        #: Bitta qator — ulanish. ⚠️ Cookie ham, hodisa yuki ham
        #: YOZILMAYDI: verdikt va bildirishnoma mazmuni shaxsiy.
        log.info(
            "realtime ulanish yopildi user=%s sabab=%s davomiylik=%.1fs hodisa=%d",
            user_id,
            close_reason,
            time.monotonic() - started,
            delivered,
        )


def _frame(item: dict[str, Any]) -> str:
    payload = json.dumps(item["data"], ensure_ascii=False)
    return f"id: {item['id']}\nevent: {item['event']}\ndata: {payload}\n\n"


def _payload_attempt_id(raw: str) -> int | None:
    try:
        blob = json.loads(raw)
    except (TypeError, ValueError):
        return None
    data = blob.get("data")
    if not isinstance(data, dict):
        return None
    raw_id = data.get("attempt_id")
    if raw_id is None:
        return None
    try:
        return int(raw_id)
    except (TypeError, ValueError):
        return None


async def _attempt_events(scope: dict[str, Any], attempt_id: int) -> None:
    """Bitta urinish uchun SSE — faqat shu `attempt_id` hodisalari."""
    send = scope["send"]
    receive = scope["receive"]

    user_id = await sync_to_async(_session_user_id, thread_sensitive=True)(scope)
    if user_id is None:
        await _send(scope, 401, b"authentication required\n")
        return

    from judging.models import Attempt

    allowed = await sync_to_async(
        lambda: Attempt.objects.filter(pk=attempt_id)
        .filter(user_id=user_id)
        .exists(),
        thread_sensitive=True,
    )()
    if not allowed:
        await _send(scope, 403, b"forbidden\n")
        return

    if _stats["connections_active"] >= MAX_CONNECTIONS_PER_PROCESS:
        _stats["connections_rejected"] += 1
        await _send(scope, 503, b"connection limit reached\n", ((b"retry-after", b"30"),))
        return

    client = _client()
    if not await _reserve_slot(client, user_id):
        _stats["connections_rejected"] += 1
        await _send(scope, 503, b"too many connections\n", ((b"retry-after", b"30"),))
        await client.aclose()
        return

    channel = bus.user_channel(user_id)
    last_id = _last_event_id(scope)
    pubsub = client.pubsub()
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=QUEUE_MAX)
    slow = asyncio.Event()

    async def pump() -> None:
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                raw = message["data"]
                if _payload_attempt_id(raw) != attempt_id:
                    continue
                try:
                    queue.put_nowait(raw)
                except asyncio.QueueFull:
                    slow.set()
                    return
        except asyncio.CancelledError:
            raise
        except Exception:
            _stats["redis_errors"] += 1
            slow.set()

    async def watch_disconnect() -> None:
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return

    _stats["connections_active"] += 1
    _stats["connections_total"] += 1
    started = time.monotonic()
    delivered = 0
    close_reason = "client_closed"
    pump_task: asyncio.Task[None] | None = None
    watch_task: asyncio.Task[None] | None = None

    try:
        await pubsub.subscribe(channel)
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": list(_HEADERS) + list(_cors_headers(scope)),
            }
        )

        async def write(chunk: str) -> None:
            await send({"type": "http.response.body", "body": chunk.encode(), "more_body": True})

        await write(f"retry: {RETRY_MS}\n\n")
        await write(": connected\n\n")

        replayed: list[dict[str, Any]] = []
        gap = False
        if last_id:
            try:
                items, channel_gap = await bus.replay_after(client, channel, last_id)
            except Exception:
                _stats["redis_errors"] += 1
                items = []
                channel_gap = False
            replayed = [item for item in items if item.get("data", {}).get("attempt_id") == attempt_id]
            gap = channel_gap
            replayed.sort(key=lambda item: item["id"])
            for item in replayed:
                await write(_frame(item))
                _stats["events_replayed"] += 1
            if gap:
                await write('event: resync\ndata: {"reason":"buffer_expired"}\n\n')
                _stats["resync_sent"] += 1

        pump_task = asyncio.create_task(pump())
        watch_task = asyncio.create_task(watch_disconnect())

        while True:
            if slow.is_set():
                close_reason = "slow_consumer"
                _stats["slow_consumer_closed"] += 1
                break
            if watch_task.done():
                close_reason = "client_closed"
                break
            try:
                raw = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_S)
            except TimeoutError:
                await write(": ping\n\n")
                _stats["heartbeats"] += 1
                await _heartbeat_slot(client, user_id)
                continue
            await write(raw)
            delivered += 1
            _stats["events_delivered"] += 1
            if delivered >= MAX_EVENTS_PER_CONNECTION:
                close_reason = "recycled"
                break
    except asyncio.CancelledError:
        close_reason = "server_cancelled"
        raise
    except Exception:
        close_reason = "redis_error"
        _stats["redis_errors"] += 1
        log.exception("attempt oqim xatosi: user=%s attempt=%s", user_id, attempt_id)
    finally:
        for task in (pump_task, watch_task):
            if task is not None:
                task.cancel()
        try:
            await pubsub.unsubscribe()
            await pubsub.aclose()  # type: ignore[no-untyped-call]
        except Exception:
            pass
        await _release_slot(client, user_id)
        await client.aclose()  # type: ignore[no-untyped-call]
        _stats["connections_active"] -= 1
        log.info(
            "attempt oqim yopildi user=%s attempt=%s sabab=%s davomiylik=%.1fs hodisa=%d",
            user_id,
            attempt_id,
            close_reason,
            time.monotonic() - started,
            delivered,
        )


async def _health(scope: dict[str, Any]) -> None:
    """Deploy `--wait` va monitoring uchun (ADR-0029 §11)."""
    client = _client()
    try:
        await client.ping()
        redis_ok = True
    except Exception:
        _stats["redis_errors"] += 1
        redis_ok = False
    finally:
        await client.aclose()
    body = json.dumps({"redis": redis_ok, **_stats}, ensure_ascii=False).encode()
    await scope["send"](
        {
            "type": "http.response.start",
            "status": 200 if redis_ok else 503,
            "headers": [(b"content-type", b"application/json; charset=utf-8")],
        }
    )
    await scope["send"]({"type": "http.response.body", "body": body})


async def _report(scope: dict[str, Any]) -> None:
    """Mijozning qayta ulanish hisoboti (ADR-0029 §11).

    ⚠️ **Nega bu endpoint bor.** Server tomondan hamma ulanish sog'lom
    ko'rinadi: uzilishni birinchi bo'lib **mijoz** sezadi (sekin tarmoq,
    uxlagan noutbuk, proksi). Usiz «realtime ishlayaptimi?» savoliga
    faqat taxmin bilan javob berilardi.

    Yuk **ishonchsiz**: mijoz yuboradi, shuning uchun u faqat hisoblagich.
    Matn ham, shaxsiy ma'lumot ham saqlanmaydi.
    """
    receive = scope["receive"]
    body = b""
    while True:
        message = await receive()
        if message["type"] != "http.request":
            break
        body += message.get("body", b"")
        if not message.get("more_body"):
            break
    try:
        payload = json.loads(body or b"{}")
        reconnects = int(payload.get("reconnects") or 0)
    except (TypeError, ValueError):
        reconnects = 0
    if reconnects > 0:
        _stats["client_reconnects_reported"] += reconnects
    await _send(scope, 200, b"")


async def application(scope: dict[str, Any], receive: Any, send: Any) -> None:
    """Tor ASGI ilova: faqat uch yo'l, qolganiga 404 (ADR-0029 §5)."""
    if scope["type"] == "lifespan":
        #: Uvicorn lifespan protokolini kutadi; usiz u ogohlantiradi.
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
        return
    if scope["type"] != "http":
        return

    scope = {**scope, "send": send, "receive": receive}
    path = scope.get("path", "")
    attempt_match = ATTEMPT_EVENTS_RE.match(path)
    if attempt_match:
        await _attempt_events(scope, int(attempt_match.group(1)))
    elif path == EVENTS_PATH:
        await _events(scope)
    elif path == HEALTH_PATH:
        await _health(scope)
    elif path == REPORT_PATH:
        await _report(scope)
    else:
        await _send(scope, 404, b"not found\n")
