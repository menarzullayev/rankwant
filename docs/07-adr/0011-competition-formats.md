# ADR-0011: Yangi musobaqa formatlari va savol banki

**STATUS:** accepted (2026-09-07)
**Ta'siri:** [04-prd](../04-prd/README.md) 🔒 va [05-domain-model](../05-domain-model/README.md) 🔒 kengaytiriladi

## Muammo

Raqobatchi tahlili (RoboContest, Codeforces, KEP) va menyu sessiyasida
product owner **barcha bo'limlar kerak** deb qaror qildi. PRD'da bo'lmagan
to'rt format va bitta yangi model paydo bo'ldi.

## Qaror

| Format | Model | Reytingga ta'siri | Qvant |
| ------ | ----- | ----------------- | ----- |
| **Testlar** (P2-6) | `quizzes.Quiz` → savol banki | yo'q | birinchi yakunlashda |
| **Arena** — jonli taymerli raund | `arena.ArenaRound` | yo'q | ishtirok uchun, ≥1 to'g'ri javob |
| **Duel** — 1v1 | `duels.Duel` | **Challenges** (klassik Elo, [ADR-0006](0006-rating-model.md)) | g'olibga |
| **Chempionat** — contest seriyasi | `tournaments.Tournament` | bosqich contestlari orqali (o'zi emas) | yo'q |
| **Hakaton** — loyiha | `hackathons.Hackathon` | yo'q (odam baholaydi) | yo'q |

Umumiy tamoyillar:

1. **Savol banki alohida** — bitta savol testda ham, arenada ham.
2. **Arena joriy savoli server vaqtidan** — mijoz taymeri yo'q, oldindan
   ko'rib bo'lmaydi.
3. **Duel Attempt'ga FK qo'shmaydi** — natija vaqt oralig'idagi AC'lardan.
4. **Chempionat formulasi ochiq** (principle #2):
   `ball = koeffitsient × (ishtirokchilar − o'rin + 1)`.
5. **Reyting faqat masala va musobaqadan** (04-prd) — Arena, Hakaton, Test
   reytingga tegmaydi; Duel esa allaqachon PRD'dagi Challenges.

## Oqibatlar

- 05-domain-model'ga 12 ta yangi model; Challenges reytingi ommaviy
  profilda ochildi (fazali ochilish Phase 3 bosqichi).
- `QvantTransaction.Reason` ga `quiz`, `arena`, `duel` qo'shildi.
- Uchta yangi beat task: `arena.finalize_due`, `duels.finalize_due`
  (contest bilan bir xil naqsh).
- Menyu: [10-operations/menu.md](../10-operations/menu.md).
