# Verdikt taxonomy — o'lik kodlar

## Umumiy ma'lumot

`apps/api/judging/verdicts.py` da 23 ta verdikt kodi e'lon qilingan. Ulardan 4 tasi
**o'lik** — ya'ni judge runtime endi ularni chiqarmaydi, lekin tarixiy ma'lumotlar
yaxlitligi uchun enum'da qoladi.

## O'lik kodlar (4 ta)

| Kod | Sabab | Kim qo'yadi | Tarixiy qatorlar |
| --- | --- | --- | --- |
| `RE` | Judge endi `RE_SIGNAL`/`RE_EXIT` chiqaradi | Ilgari judge, hozir hech kim | 18 163 |
| `RATE_LIMITED` | API throttle, judge emas | `AttemptViewSet.throttled` | 0 (yangi) |
| `DENIAL_OF_JUDGEMENT` | Ish yo'qolganida, judge emas | `reap_stuck` vazifasi | 0 (yangi) |
| `TESTING_ABORTED` | Rejudge/hack bekor qilganda, judge emas | `rejudge` buyrug'i, hack dvigateli | 0 (yangi) |

### RE — Runtime Error (LEGACY)

- **So'nggi marta judge chiqargan:** `RE_SIGNAL`/`RE_EXIT` ajratishdan oldin.
- **Almashtiruvchi:** `RE_SIGNAL` (signal bilan o'ldirilgan, masalan segfault) va
  `RE_EXIT` (nolga teng bo'lmagan chiqish kodi).
- **M10 migratsiya:** 18 163 ta tarixiy qator `details` JSON'dagi `signal`/
  `exit_code` kalitlariga qarab qayta yorliqlanadi. Kalit yo'q bo'lsa
  `RE_SIGNAL` ga tushadi (signal xatolar ko'proq uchragan).

### RATE_LIMITED — Submit limiti

- **Hech qachon judge chiqarmagan.** Submit tezligi chegarasidan oshganda
  `AttemptViewSet.throttled` yozadi (429 HTTP javobidan oldin).
- **Maqsad:** Foydalanuvchi "yubordim, qayoqqa ketdi?" deb qolmasligi uchun
  tarixda iz qoladi.

### DENIAL_OF_JUDGEMENT — Infra nosozligi

- **Hech qachon judge chiqarmagan.** `reap_stuck` vazifasi judge navbatdan ishni
  olganidan keyin yiqilganda (deploy, OOM) ish yo'qoladi. Bir marta qayta
  navbatga qo'yiladi; qayta urinish ham qotsa bu verdikt qo'yiladi.
- **IE emas:** `IE` masala sozlamasi xatosini ham bildiradi; operator
  "infra nosozligimi yoki masala buzuqmi?" deb ajrata olmasdi.

### TESTING_ABORTED — Tekshiruv bekor qilindi

- **Hech qachon judge chiqarmagan.** `rejudge` buyrug'i eski natijani bekor
  qilib qayta tekshirishni boshlaganda, yoki hack dvigateli himoyachi
  yechimini bekor qilganda qo'yiladi.
- **Maqsad:** Foydalanuvchi "oldingi natija bekor qilindi, qayta tekshirilmoqda"
  deb tushunishi uchun.

## Verdikt ustuvorligi

Bitta yuborishda bir nechta test har xil verdikt bersa, **birinchi
muvaffaqiyatsiz test** g'olib chiqadi (08-technical-spec § judge). Tartib:

1. `SECURITY_VIOLATION` (eng yuqori)
2. `COMPILE_TIMEOUT`
3. `CE`
4. `RE_SIGNAL` / `RE_EXIT` (eski `RE`)
5. `TLE` / `IDLENESS`
6. `MLE`
7. `OLE`
8. `WA` / `PE`
9. `CHECKER_ERROR`
10. `PARTIAL` (IOI ballashda)
11. `AC` (eng past — hammasi o'tganda)

Bu tartib `services/judge-go/judge.go:classify` da kodlangan.

## Tekshirish

```bash
python tools/check_verdict_codes.py
```

Bu skript API kodlari bilan web/theme/i18n/ikonka mosligini tekshiradi.
O'lik kodlar ham i18n yorlig'i va ikonkaga ega bo'lishi shart (tarixiy
ma'lumotlarni ko'rsatish uchun).
