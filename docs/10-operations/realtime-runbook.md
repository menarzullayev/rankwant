# Realtime (SSE) — ishlatish qo'llanmasi

👉 Qaror va sabablar: [ADR-0029](../07-adr/0029-realtime-transport.md).

Bu hujjat **ishlatish** uchun: qanday yoqiladi, qanday kuzatiladi, yiqilsa
nima qilinadi.

---

## 1. Tunnel (HOST darajasidagi o'zgarish)

⚠️ **Bu qadam repo'dan tashqarida** — `/etc/cloudflared/config.yml` (Windows:
`%USERPROFILE%\.cloudflared\`). Usiz `realtime` konteyneri ishlaydi, lekin
tashqaridan ko'rinmaydi.

`ingress` ro'yxatiga `web` va `api` dan **oldin** qo'shiladi:

```yaml
ingress:
  - hostname: rankwant.uz
    path: /api/v1/events/*
    service: http://127.0.0.1:8302
  - hostname: rankwant.uz
    path: /api/v1/realtime/*
    service: http://127.0.0.1:8302
  # ... qolgan qatorlar o'zgarmaydi (api → 8301, web → 8300)
```

⚠️ **Tartib muhim**: Cloudflare ingress birinchi mos kelgan qatorni oladi.
`/api/*` qatori yuqorida tursa, oqim `api` ga tushadi va **ishlamaydi** —
`gunicorn` sinxron worker'i ulanishni ushlab qoladi.

Keyin: `sudo systemctl restart cloudflared` (Windows: xizmatni qayta ishga
tushirish).

**Tekshirish:**

```bash
curl -s -o /dev/null -w '%{http_code}\n' -H 'Accept: text/event-stream' \
  https://rankwant.uz/api/v1/events/
# 401 kutiladi (anonim) — bu oqim MANBA ishlayotganini bildiradi.
# 404 → tunnel qatori yo'q. 502 → konteyner ko'tarilmagan.
```

## 2. Kuzatish

**Health** (deploy `--wait` ham shuni kutadi):

```bash
curl -s https://rankwant.uz/api/v1/realtime/health/
# {"redis": true, "connections_active": 3, "connections_total": 41, ...}
# 503 → Redis yetib bo'lmayapti.
```

**Metrikalar** (ADR-0029 §11) — health javobida:

| Kalit | Nima uchun |
| --- | --- |
| `connections_active` | sig'im; to'yinganlikni birinchi ko'rsatadi |
| `connections_total` | oqim hajmi |
| `connections_rejected` | 503 lar — chegara urilgan |
| `events_delivered` | yetkazilgan hodisa |
| `events_replayed` | qayta ulanishda to'ldirilgan |
| `resync_sent` | ⚠️ **bufer yetmagan** holatlar soni |
| `heartbeats` | ulanish tirikligi |
| `redis_errors` | pub/sub sog'lig'i |
| `slow_consumer_closed` | sekin mijoz uzilgan |
| `client_reconnects_reported` | mijoz hisoboti (yagona haqiqiy signal) |

⚠️ **`resync_sent` o'sishi — eng muhim signal.** U «mijoz hodisalarni
yo'qotdi» degani: replay buferi yetmagan. Sabab odatda uzoq uzilish yoki
`REPLAY_MAX` (50) ning kichikligi.

**Loglar:** har ulanish uchun bitta qator —

```
realtime ulanish yopildi user=42 sabab=client_closed davomiylik=118.4s hodisa=7
```

`sabab` qiymatlari: `client_closed` · `slow_consumer` · `recycled` ·
`server_cancelled` · `redis_error`. ⚠️ Cookie ham, hodisa yuki ham
yozilmaydi — verdikt va bildirishnoma mazmuni shaxsiy.

## 3. Sig'im

| | Qiymat |
| --- | --- |
| Bitta ulanish | ≈ bitta asyncio task + 256 lik navbat ≈ o'nlab KB |
| Jarayon chegarasi | 2000 ulanish (`MAX_CONNECTIONS_PER_PROCESS`) |
| Foydalanuvchi chegarasi | 5 ulanish |
| Hozirgi yuklama | **o'lchandi: 0** (2026-09-27) |

⚠️ **Umumiy chegara JARAYON ichida yuritiladi.** `REALTIME_WORKERS=4` bo'lsa
amaldagi chegara 4 × 2000 bo'ladi. Ko'paytirishdan oldin hisobni Redis'ga
ko'chirish kerak.

**Ko'paytirish:** `docker compose ... up -d --scale realtime=N` — sticky
sessiya kerak emas (fan-out Redis pub/sub orqali).

## 4. Nosozlik holatlari

| Belgi | Sabab | Nima qilinadi |
| --- | --- | --- |
| Sahifa yangilanmaydi, `connections_active` 0 | `realtime` ko'tarilmagan | `docker compose ps realtime`; loglarni ko'rish |
| 401 | sessiya cookie yo'q yoki muddati o'tgan | normal — foydalanuvchi kirmagan |
| 503 ketma-ket | chegara urilgan | `connections_active` ni ko'rish; worker qo'shish |
| `resync_sent` tez o'sadi | uzoq uzilishlar yoki kichik bufer | `REPLAY_MAX` ni oshirish yoki sababni topish |
| `redis_errors` o'sadi | Redis nosozligi | Redis sog'lig'ini tekshirish; oqim o'chsa **sayt ishlashda davom etadi** |
| `slow_consumer` ko'p | sekin mijozlar yoki juda katta hodisa | hodisa yukini tekshirish |

⚠️ **Oqim o'chirilsa hech narsa buzilmaydi.** Sahifa qo'lda yangilanadi;
verdiktlar baribir yoziladi (`drain_results` nashrga bog'liq emas).
Shoshilinch holatda: `docker compose ... stop realtime`.

## 5. Tekshirish (qo'lda)

```bash
# 1. Anonim — 401 bo'lishi kerak
curl -si https://rankwant.uz/api/v1/events/ | head -1

# 2. Sessiya bilan oqim ochiladi va heartbeat keladi
#    (brauzerda: DevTools → Network → events/ → EventStream)
```

Brauzerda: **DevTools → Network → `events/` → EventStream** — `connected`,
`: ping` va `verdict` yozuvlari ko'rinadi. Yozuv kelmasa birinchi navbatda
tunnel qatorini (§1) tekshiring.
