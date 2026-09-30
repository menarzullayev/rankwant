# AI Gateway — modul chegarasi (D6 · Phase 0 skeleti)

Bu papka — AI qatlamining **yagona uyi**. Phase 0 da faqat **skelet** va
uning darvozasi bor; AI Gateway **runtime**i (LLM klienti, provider'lar,
prompt'lar, endpoint'lar — 0033–0035) **Phase 3** ga tegishli va bu yerda
**yo'q**.

## Nima uchun bu modul "monolit" (D6)

Owner qarori (D6): AI Gateway — **monolit Python modul** `apps/api/ai/`.
Bu ataylab Django app **emas**: `models.py`, `migrations/`, `apps.py`
yo'q va `INSTALLED_APPS` ga qo'shilmaydi. Sabab — AI qatlami keyinchalik
alohida xizmatga ajratilishi mumkin; u bugun DB sxemasiga yopishsa,
ajratish imkonsiz bo'ladi.

## Chegara kontrakti

`tools/check_ai_boundary.py` statik (AST) darvozasi quyidagilarni
**taqiqlaydi**:

| Taqiq | Naqsh | Sabab |
|---|---|---|
| Django model importi | `from <app>.models import …` · `from .models import …` · `import <app>.models` | AI qatlami DB sxemasini bilmasin |
| Django DB qatlami | `django.db` · `django.contrib.*` | DB/ORM'ga bog'lanish ajratishni buzadi |
| Baza manzili | `DATABASE_URL` satri (env o'qish ham) | AI qatlami bazaga ulanishni bilmasin |
| Testdata o'qish | `open(…)` · `Path(…)` · `*.read_*()` ichida `testdata` · `fixtures/` · `*.json` | testdata runtime bog'liqligi bo'lmasin |

Darvoza `apps/api/ai/**/*.py` ni skanerlaydi. Buzilish bo'lsa har biri
`fayl:satr — sabab` ko'rinishida chiqadi va skript `exit 1` beradi.
Toza bo'lsa `exit 0`. O'qib bo'lmasa `exit 2` — bu hech qachon "toza"
deb o'qilmaydi.

Runtime tomoni `apps/api/tests/test_ai_boundary.py` da yopiladi: `ai`
paketini import qilganda `sys.modules` ga birorta `*.models` moduli
**tushmasligi** shart.

## Nima uchun salbiy test majburiy

Bugun `apps/api/ai/` deyarli bo'sh — darvoza "yashil", lekin bu
**vakuumli yashil**: o'lchanadigan kod yo'q. Shuning uchun
`tools/check_negative.py` ichidagi `neg_ai_boundary` guruhi vaqtinchalik
fayl yaratib, taqiqlangan import kiritadi va darvoza `exit 1`
qaytarishini **talab qiladi**. Shundagina "hech qachon yiqilmaydigan
tekshiruv" emasligi isbotlanadi.

## Pretsedent

`services/judge-go/main.go` da `DATABASE_URL` uchun aynan shunday guard
bor: judge hosti bazaga ulanishni bilmaydi. Bu modul shu qoidani Python
tomonida takrorlaydi.

**STATUS:** AI Gateway skeleti (D6 · WP5) — tayyor. Chegara statik va
runtime tomondan majburlanadi; runtime Phase 3 da qo'shiladi.
