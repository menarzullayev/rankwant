# ADR 0042 — Module boundary (dependency rules)

**STATUS:** accepted
**Sana:** 2026-09-29
**Tasdiqlagan:** Saidakbar (owner)
**Manba:** D7 (ADR 0042 dependency policy) · `owner-decision-closure-matrix-2026-09-29.md`
**Ta'sir doirasi:** Phase 0
**Dalil:** `tools/check_architecture.py` (statik gate, mavjud) · `tools/architecture-allowlist.txt` (`# jami: 111` — grandfather yozuvlar) · `apps/api/arena/services.py` · `apps/api/judging/serializers.py` · `apps/api/ratings/services.py` · `apps/api/classroom/serializers.py` · `tools/check_security_boundary.py` (faqat compose chegarasini o'lchaydi)

## 1. Muammo

`apps/api/` ichida app'lar bir-birining `models` modulini import qiladi (`arena/services.py`, `judging/serializers.py`, `ratings/services.py`, `classroom/serializers.py`). Bu **yashirin bog'liqlik**: `check_security_boundary.py` faqat compose chegarasini o'lchaydi, Python import chegarasini **emas**. Oqibat: drift; AI chegarasi (ADR 0036) ham himoyasiz qoladi.

## 2. Variantlar

1. Faqat hujjat qoidasi.
2. To'liq paket ajratish (katta refactor).
3. Import allowlist + `check_architecture.py` (inkremental).

## 3. Tanlov

**Variant 3** (D7) — **grandfather + ratchet**:
- Qoida: bir app boshqa app'ning `models` modulini import qilmasin (`from <boshqa_app>.models import ...` · `import <boshqa_app>.models`).
- Istisno: `migrations/`, `tests/` va `core` (umumiy poydevor — unga tayanish ruxsat).
- Bugungi buzilishlar `tools/architecture-allowlist.txt` da **grandfather** qilingan (`# jami: 111`); gate ular uchun yashil (exit 0).

## 4. Sabab

To'liq paket ajratish (variant 2) katta refactor va Phase 0 ni bloklaydi. Hujjat qoidasi (variant 1) majburlanmaydi. Import allowlist inkremental: bugungi holat qotiriladi, yangi buzilish darhol to'siladi. Ratchet allowlist'ni **faqat qisqartiradi** — importni tuzatgan odam yozuvini ham o'chirishi shart, aks holda gate `exit 1` beradi.

## 5. Oqibatlar

- `tools/check_architecture.py` + `tools/architecture-allowlist.txt` (111 yozuv).
- **Yangi** taqiqlangan import → CI **qizil** (exit 1).
- Allowlist'da bor, lekin repo'da endi **mavjud bo'lmagan** yozuv → exit 1 (o'lik yozuv, ratchet).
- O'qib bo'lmasa → exit 2 (hech qachon «toza» deb o'qilmaydi).
- Salbiy test (`neg_architecture`) majburiy.

## 6. Qaytarilishi

Oson (statik qoida + allowlist). Allowlist Phase 0 da o'rnatiladi; keyingi fazalarda faqat qisqaradi.

## 7. Tasdiq

- `tools/check_architecture.py` + allowlist fayli mavjud; gate **exit 0**.
- **Yangi** taqiqlangan import → CI **qizil**.
- Allowlist'da mavjud buzilishlar soni **yozilgan** (`# jami: 111`).
- **Ratchet** mavjud — o'lik allowlist yozuvi ham `exit 1`.

## 8. Bog'liq hujjatlar

- D7 — `owner-decision-closure-matrix-2026-09-29.md`
- `acceptance-criteria-lock-2026-09-29.md` — WP6 bloki
- Blueprint §21 (ADR 0042) · §24 (Phase 0 done-condition ⑤)
- `phase0-reconciliation-table-2026-09-29.md` — 4-qator (faza nomuvofiqligi)
- ADR 0036 (AI data boundary) · ADR 0033 (AI Gateway)

**STATUS:** ADR 0042 — accepted. Phase 0; grandfather (111 yozuv) + ratchet; yangi import → CI qizil.
