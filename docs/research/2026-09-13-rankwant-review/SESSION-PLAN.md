# Savol-javob sessiyasi — reja

Sana: 2026-09-13 · Maqsad: ko'rikda topilgan **ochiq savollarni yopish** va
keyingi qadamni belgilash.

## Nima uchun kerak

12 qadamli ko'rik `NOT READY` berdi. Sabablarning bir qismi **men tuzata
olmaydigan** turda:

- ba'zilari **faktik** — javob faqat sizda (fayllar qayerda, kim tasdiqladi)
- ba'zilari **qaror** — faqat inson qabul qiladi (launch tasdig'i, narx)
- ba'zilari **yo'nalish** — mahsulot egasining tanlovi

Shu uchtasi savol-javob sessiyasining predmeti.

## Mavzular — uch guruh

### A. Faktik bo'shliqlar (javob faqat sizda, xarajat nol)

> **A1 QIDIRUV NATIJASI (2026-09-13, javobdan oldin qidirildi).**
>
> Ikki fayl **butun mashinada yo'q**. Qidirildi: workspace (chuqurlik
> cheklovisiz), `C:\Users\nsn` (depth 7), `C:\` (depth 5),
> Desktop/Downloads/Documents/OneDrive, `project.zip`, va matn bo'yicha
> havola qidiruvi. Havola qiluvchi 5 joy: `03/README.md`,
> `03/competitor-summary.md`, `08/README.md`, `docs/README.md`, `INDEX.md`.
>
> Ustiga: havola yo'llari ham **bir-biriga mos emas** — `INDEX.md`
> `../kep-uz-platform-analysis.md` deydi, `docs/README.md` esa
> `Web_Projects/kep-uz-platform-analysis.md`. Ikkalasi ham mavjud emas.
>
> **Ya'ni fayllar yo'qolgan, nusxasi ham yo'q.** Butun TAM/SAM/SOM
> (`~197k`, `~9k`) va KEP endpoint ro'yxati (`102 endpoint`) manbasiz qoldi.
>
> **O'rnini bosadigan manba topildi:** `C:\Users\nsn\rankwant-audit\`
> (1.1 MB, **2026-09-13**). Ichida 5 platforma UI surati
> (`robocontest.uz/register`, `/login`, `kep.uz` login, `rankwant.uz`
> login/register) — har biri `page.html` + `shot.png` + `structure.json`
> (nodes, fields, buttons, tashqi hostlar), plus `XULOSA-VA-REJA.md` (16 KB).
> Repo commitlari `710d850` va `e74af03` shu auditga bog'lanadi — ya'ni bu
> **aynan shu loyiha** haqida.
>
> ⚠️ Lekin bu yangi audit **foydalanuvchi sonlarini o'z ichiga olmaydi** —
> u UI tuzilmasini o'lchaydi. Ya'ni **bozor hajmi raqamlari tiklanmaydi**.

| # | Savol | Nega muhim |
|---|---|---|
| A1 | Yo'qolgan raqamlar bilan nima qilamiz? (qayta tadqiqot / olib tashlash + "tekshirilmagan" belgilash / yangi auditni repo'ga ko'chirish) | Butun TAM/SAM/SOM manbasiz |
| A2 | Approver yozuvi to'g'rimi: **Saidakbar Narzullayev — Repo owner / maintainer**? | 01–09 ga yozdim; xato bo'lsa tuzataman |
| A3 | `rankwant-handoff/` (`.git` siz nusxa, 807 fayl, eskiroq) taqdiri? | Ikki nusxa chalkashlik manbai |

### B. Faqat inson qabul qiladigan qarorlar

| # | Savol | Nega muhim |
|---|---|---|
| B1 | **10 Operations — A yoki B?** | Yagona `BLOCK` ni yopadi |
| B2 | `idea-selection` — asl g'oya qanday tanlangan? | Zanjirning boshi; retroaktiv hujjat uchun xom material |
| B3 | 06 Deployment — muhitlar, hosting, rollback qanday? | Amalda allaqachon muammo bo'lgan bo'shliq |
| B4 | 03 — `Substitutes` va voyaga yetmaganlar regulyatsiyasi: qaysi biri ustuvor? | Ikkalasi ham yo'q, ikkalasi ham jiddiy |

### C. Mahsulot yo'nalishi (ko'rikdan tashqari)

| # | Savol | Nega muhim |
|---|---|---|
| C1 | Keyingi mahsulot qadami nima? Phase 1 davom etadimi? | Ko'rik hujjat haqida; bu — mahsulot haqida |
| C2 | Narx modeli (03 va 04 da qolgan) | P2-3 ni bloklaydi |
| C3 | `web-access` uchun CDP ruxsati yoqilsinmi? | Chrome'da bir marta bosish kerak |

## Savollar tartibi va sababi

| Raund | Mavzular | Sabab |
|---|---|---|
| **1** | A1 · A2 · A3 | Eng arzon. Faktlar keyingi savollarning kontekstini o'zgartirishi mumkin |
| **2** | B1 | **Yagona BLOCK.** Qolganidan oldin yopilishi kerak |
| **3** | B2 · B3 · B4 | Hujjat to'liqligi qarorlari |
| **4** | C1 · C2 · C3 | Eng ochiq, eng erkin. Oldingi javoblardan keyin mazmunliroq bo'ladi |

**Tartib tamoyili:** arzon → qimmat · bloklovchi → bloklamaydigan ·
fakt → qaror → yo'nalish.

## Kutilayotgan javob formati

| Savol turi | Format | Namuna |
|---|---|---|
| **Faktik** (A) | Fayl yo'li · yoki "yo'q" · yoki bir qator | `C:\Users\nsn\analysis\kep-uz-platform-analysis.md` |
| **Tanlov** (B1, B4, C3) | Harf + bir qatorli sabab | `A — chunki xizmat allaqachon ommaviy` |
| **Ro'yxat** (B3) | 3–7 band, har biri bir qator | `Muhitlar: dev (mahalliy), prod (bitta mashina)` |
| **Erkin** (B2, C1, C2) | 2–5 qator matn | — |

**Qoida:** javob qisqa bo'lsa — yaxshi. Men noaniq joyni **qayta so'rayman**,
o'zim to'ldirmayman.

## Sessiya natijasi — format

Har raunddan keyin:

1. **`rankwant-review/SESSION-ANSWERS.md`** — javoblar, sana bilan
2. Javob hujjatga tegishli bo'lsa — **o'sha hujjatga tuzatish** kiritiladi
   (masalan A1 → tahlil fayllari repo'ga ko'chiriladi)
3. Sessiya oxirida **yangi baholar jadvali**: qaysi bosqich `WARN`/`BLOCK` dan
   chiqdi, qaysi biri qoldi

## Nima o'zgarmaydi

- **Tasdiq uydirilmaydi.** B1 da "ha" desangiz — yozaman; demasangiz
  `PENDING` qolaveradi.
- **Javobsiz savol ochiq qoladi.** "Bilmayman" — to'g'ri javob.
- Hujjat mazmuni **sizning** so'zlaringizdan yoziladi, taxminimdan emas.
