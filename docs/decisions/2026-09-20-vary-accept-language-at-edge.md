| Sana | Qaror | Kodda qayerda |
|---|---|---|
| 2026-09-20 | **Vary `Accept-Language` chekkada** (HITL: cf-transform). Next.js 16 in-process `Vary` ni o'chiradi. CF Transform Rule `add` (`set` emas — RSC tokenlari). Mehmon kesh yo'llari (`/`, login, huquqiy) chiqariladi — 100k fragment yo'q. Kesh doirasi kengaytirilmaydi | `tools/cf-vary-accept-language.json`; `tools/cf_vary_apply.py`; `tools/check_decisions.py` → `vary_accept_language_at_edge`; salbiy testlar 2 ta |
