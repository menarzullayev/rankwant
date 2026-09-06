# ADR-0009: Monorepo

**STATUS:** accepted (2026-09-06)
**Ta'siri:** [ADR-0003](0003-stack-django-next.md) dagi «uch repo» qarori almashtiriladi

## Muammo

[ADR-0003](0003-stack-django-next.md) oqibatlar bo'limida `rankwant-api`, `rankwant-web`, `rankwant-judge` — uchta alohida repo yozilgan edi. Kod yozish boshlanishidan oldin bu qayta ko'rib chiqildi.

## Variantlar

| # | Variant | OpenAPI kontrakt | CI | Xavfsizlik ajratish |
| - | ------- | ---------------- | -- | ------------------- |
| 1 | **Monorepo** | ✅ bir PR da ko'rinadi | 1 ta | repo darajasida yo'q |
| 2 | 3 ta repo | ⚠️ integratsiyada bilinadi | 3 ta | ✅ |
| 3 | Monorepo + judge alohida | ✅ | 2 ta | ✅ judge uchun |

## Tanlov

**Variant 1 — monorepo `rankwant`.**

## Sabab

- **DoD talabi:** [09](../09-development-plan/README.md) «OpenAPI schema diff har PR da» deydi. `apps/api` va `apps/web` bir repoda bo'lsa, kontrakt buzilishi **PR da** ko'rinadi; alohida repolarda esa integratsiya vaqtida, ya'ni kech bilinadi.
- **Bake-off:** [ADR-0004](0004-judge-engine.md) ikki nomzodni bir vaqtda talab qiladi (`services/judge-go`, `services/judge-py`) — bir repoda ularni bir xil CI va bir xil sinov to'plami bilan solishtirish tabiiy.
- **Kichik jamoa:** atomik o'zgarish (model → API → UI) bitta PR da.
- **Repo tuzilishi ≠ deploy tuzilishi.** Xavfsizlik chegarasi **hostlarda** ([06](../06-architecture/README.md) 🔒), repoda emas — judge baribir alohida hostga, kiruvchi portsiz deploy qilinadi.

## Tuzilish

```
rankwant/
├── apps/
│   ├── api/            Django 5.2 + DRF
│   └── web/            Next.js + TS
├── services/
│   ├── judge-go/       nomzod A — Go + nsjail
│   └── judge-py/       nomzod B — Python + isolate
├── docs/               hujjat pipeline (01–10)
├── tests/              e2e, load, security, chaos
├── .github/workflows/  CI/CD
└── docker-compose.yml  local: api + web + postgres + redis + judge
```

## Oqibatlar

- ADR-0003 dagi «Repo tuzilishi: `rankwant-api`, `rankwant-web`, `rankwant-judge`» bandi **bekor**; o'rniga shu ADR
- `06-architecture` servis nomlari yo'l sifatida yangilanadi
- CI path-filter bilan ishlaydi: faqat o'zgargan qism build/test qilinadi
- Kelajakda judge ni ajratish kerak bo'lsa — `git subtree split` bilan mumkin, qaror qaytariladigan

## Bog'liq hujjatlar

- [0003-stack-django-next.md](0003-stack-django-next.md)
- [0004-judge-engine.md](0004-judge-engine.md)
