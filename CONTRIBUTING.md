# Hissa qo'shish

## Hujjat birinchi

Bu loyihada **hujjat koddan oldin** keladi. `docs/` dagi bosqichlar 🔒 `locked` bo'lsa — ularni
o'zgartirish uchun **yangi ADR** kerak (`docs/07-adr/`). Bu byurokratiya emas: qulflangan
qaror bir necha hujjatga tarqalgan bo'ladi, ADR esa nima uchun o'zgarganini saqlaydi.

Qaerdan boshlash: [INDEX.md](INDEX.md) → [docs/README.md](docs/README.md)

## Branch va commit

- Branch: `feat/…`, `fix/…`, `chore/…`, `docs/…`
- Commit: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`)
- `main` ga to'g'ridan-to'g'ri push **yopiq** — faqat PR orqali

## Definition of Done

Har PR uchun: [09-development-plan § Definition of Done](docs/09-development-plan/README.md).
PR shabloni shu ro'yxatni avtomatik chiqaradi.

## Test

To'liq strategiya: [docs/10-operations/test-strategy.md](docs/10-operations/test-strategy.md)

Qamrovi **majburiy** bo'lgan to'rt soha — bularsiz PR birlashtirilmaydi:

1. Judge pipeline (submit → verdict)
2. 4 reyting formulasi
3. Qvant ledger
4. Auth va PAT scope

## Xavfsizlik

Foydalanuvchi kodi **faqat** judge hostda ishlaydi. Judge ga tegadigan har qanday o'zgarish
`tests/security/` ni yangilashni talab qiladi.

Zaiflik topsangiz — **ommaviy issue ochmang**, GitHub Security Advisory orqali xabar bering.

## Local ishga tushirish

```bash
docker compose up -d          # postgres + redis + minio
python3 tools/check_docs.py   # hujjat yaxlitligi
```
