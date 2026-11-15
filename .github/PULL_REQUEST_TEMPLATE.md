## Nima o'zgardi

<!-- Qisqa tavsif. Nima uchun — «nima» dan muhimroq. -->

## Bog'liq hujjat

<!-- ADR raqami, `docs/decisions/` fayli yoki hujjat havolasi. Issue ishlatilmaydi. -->

## Tekshiruv

CLAUDE.md § Ish uslubi bo'yicha:

- [ ] Tegilgan qismning testi **mahalliy yashil** (CI nimani yurgizmasa, uni o'zim yurgizdim)
- [ ] Murakkab o'zgarish (mantiq, xavfsizlik, migratsiya, judge) — merge'dan oldin diff'ni `/code-review` bilan ko'rib chiqdim
- [ ] Endpoint yoki serializer o'zgargan bo'lsa — OpenAPI sxemasi yangilandi
- [ ] Yangi muhit o'zgaruvchisi `.env.example` ga yozildi
- [ ] Saidakbar aka qarorini o'zgartirgan bo'lsam — aniq tasdiq bor va `docs/decisions/` yangilandi
- [ ] Merge'dan keyin deploy va jonli sahifa tekshiriladi (`deploy tugadi: <sha>`)

## Xavfsizlik

- [ ] Foydalanuvchi kodi ishlaydigan yo'lga tegmadim, **yoki** tegdim va `tests/security` yangilandi
- [ ] Secret, token yoki credential qo'shmadim
