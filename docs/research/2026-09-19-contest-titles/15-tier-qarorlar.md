# RankWant — 15 pog'onali tier tizimi: qarorlar jurnali

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Bu zinapoya keyin almashtirilgan: amaldagi qaror — 16 pog'ona, 7 rang guruhi (`CLAUDE.md`, 2026-09-20). Foizlar `seed_stress` simulyatsiyasidan, jonli bazadan emas.

> Ish tartibi: har qavat uchun **aniq 4 variant** (tavsif + afzallik +
> kamchilik) taqdim etiladi, Saidakbar aka bittasini tanlaydi, keyin
> keyingi qavatga o'tiladi. 1 → 15 ketma-ket.
>
> Bu fayl — yagona qarorlar manbasi. Har tanlov shu yerga yoziladi,
> keyingi qavat ana shu yozuvga tayanadi.

---

## Umumiy parametrlar (o'lchangan)

| Parametr | Qiymat | Manba |
| --- | --- | --- |
| Boshlang'ich reyting | 1400 | `User.rating_contest` |
| Taqsimot markazi (μ) | 1400 | `seed_stress.py` |
| Standart chetlanish (σ) | 250 | `seed_stress.py` |
| Simulyatsiya | N=100 000, seed 42 | shu jurnal uchun |
| Hozirgi tizim | 9 pog'ona, 18 palitra, `--rw-rank-1…9` | ADR-0018 |
| Maqsad | 15 pog'ona | Saidakbar aka qarori |

**Asosiy formulalar (taklif, 1-qavatdan kelib chiqadi):**

```
birinchi_musobaqa    →  daraja = 0
har_bir_musobaqadan_keyin: daraja += f(ball, o'rin, ishtirokchilar)
minimal_ishtirokchi  →  10
```

---

## Qavat 1 — Asosiy tamoyil

**STATUS: TASDIQLANDI (2026-09-19)** ✅

**Tanlangan tamoyil: MEM — «Hech kim darajasiz qolmaydi»**

### Ta'rif

> **1-qavat — kutish zali emas, harakat davri.** Odam platformaga kirib
> birinchi musobaqani yakunlashi bilan **darhol** unvon oladi. Hech kim
> bir kunda ham darajasiz yurmaydi.

### O'lchangan asos

| Nima o'lchandi | Natija |
| --- | --- |
| Yangi odam birinchi musobaqagacha | unvonsiz (hozirgi holat: `rated_contests <= 0` → `None`) |
| Yangi odamning daraja boshlanishi | **0** — eng pastdan, o'sish hissi bilan |
| 1-qavat qamrovi (0+) | **100.00%** — hamma shu yerdan o'tadi |
| 800+ (2-qavat nomzodi) | 99.20% |
| 1000+ | 94.46% |

### Nega bu tamoyil

- **Eng ko'p odam shu qatlamda.** 1-qavatdan 100% o'tadi — bu tizimning
  «kirish eshigi», va birinchi taassurot shu yerda shakllanadi.
- **Bo'sh ekran — eng qimmat xato.** Yangi odam profiliga kirib
  «daraja yo'q» ko'rsa, qaytib kelish sababi kamayadi.
- **O'sish ko'rinadigan bo'ladi.** 0 dan boshlagan odam birinchi
  musobaqadan keyin 300 ball ko'tarilishini ko'radi — bu MEM dvigateli.

### Qabul qilingan qoidalar

| Qoida | Qiymat | Izoh |
| --- | --- | --- |
| Darajasiz holat muddati | **≤ 1 musobaqa** | Ro'yxatdan o'tish → birinchi yakunlangan musobaqa |
| Daraja boshlanishi | **0** | 1400 emas — 0, o'sish sezilsin |
| Daraja ko'rinishi | **doim ko'rinadi** | Hatto 0 ballda ham unvon bor |
| Unvon olish sharti | **1 yakunlangan reytingli musobaqa** | `rated_contests >= 1` |
| Minimal ishtirokchi | **10** | 10 dan kam bo'lsa musobaqa reytingli hisoblanmaydi |

### Rad etilgan variantlar

| Variant | Nega rad etildi (taxmin) |
| --- | --- |
| Bosiq («faqat yangilar») | 99%+ odam bitta qatorda — ichida farq yo'qoladi |
| Sport (ko'rinmas darvoza) | Yangi odam 2–3 musobaqa «darajasiz» yuradi — MEM effektiga qarshi |
| Ilmiy (eng mayda zarracha) | «Kvark» yangi odamga hech narsa aytmaydi |

### Keyingi qavatga ta'siri

- **2-qavat** 800+ dan boshlanishi mumkin (99.2% qamrov) — nomi
  «o'sishning birinchi ko'rinadigan qadami» bo'lishi kerak.
- 1-qavat **keng** (0–799), ya'ni uning ichida o'sish sezilmaydi.
  Buni qoplash uchun **2-qavatdan boshlab tig'izlik** kiritiladi.

---

## Qavat 1 (davomi) — Reyting chegarasi

**STATUS: TASDIQLANDI (2026-09-19)** ✅

**Tanlangan chegara: `0 – 799`** (2-qavat 800+ dan boshlanadi)

### O'lchangan asos

| Nima o'lchandi | Natija |
| --- | --- |
| 1-qavatda qoladigan (0–799) | **0.80%** |
| 1-qavatdan o'tib ketadigan (800+) | **99.20%** |
| 1000+ (2-qavatdan ham chiqqanlar) | 94.46% |

Ya'ni 1-qavat «yashash joyi» emas — **o'tish davri**. 99.2% odam uni
tez tark etadi, va aynan shu maqsad: yangi odam birinchi musobaqadan
keyin ~1000 ballga chiqib, 2-qavatga o'tganini **darhol** ko'radi.

### Qabul qilingan qoidalar

| Qoida | Qiymat |
| --- | --- |
| 1-qavat chegarasi | `0 ≤ rating < 800` |
| 2-qavat boshlanishi | `800` |
| Daraja boshlanishi | `0` |
| Unvon sharti | `rated_contests >= 1` |
| Minimal ishtirokchi | `10` |

### Rad etilgan variantlar

| Variant | Nega rad etildi |
| --- | --- |
| `0–1199` (migratsiya arzon) | 1200 ball oralig'i juda katta — 0 balli bilan 1199 balli bir xil; MEM effekti zaif. Migratsiya arzonligi uzoq muddatli tizim sifatiga qurbon qilinmasligi kerak. |
| `0–599` (faqat yangilar) | O'lchandi: 0–599 da atigi ~0.1% qoladi — qavat deyarli bo'sh; `600` yumaloq bo'lmagan chegara tabiiy `800/1000` nuqtalarini yo'qotadi. |
| `0–799` + ichki bosqichlar | Tier tizimiga ikkinchi o'lchov qo'shiladi — `titles.py` murakkablashadi, «nechchi qavatdaman» savolida chalkashlik. Kelajakda ko'rib chiqilishi mumkin, hozir emas. |

### Keyingi qavatga ta'siri

- **2-qavat chegarasi `800`** — qat'iy belgilandi.
- 2-qavat tor (800–999, faqat 4.75% odam) — shuning uchun **3-qavat
  ham tor** bo'lishi mumkin, ya'ni quyi qismda tig'izlik davom etadi.
- Ochiq savol (keyingi qavatda): 2-qavat **nomi va rangi**.

---

# YAKUNIY ZINAPOYA — 15 QAVAT (TASDIQLANDI)

**Barcha 15 qavat tasdiqlandi (2026-09-19).** Har qavat uchun ikki qaror
qabul qilindi: **chegara** va **nom** (qavat 2 uchun qo'shimcha **rang**).

| # | Kod | Nom | Oraliq | Keng | Ulush | Izoh |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `nebula` | **Nebula** | 0–799 | 800 | 0.80% | Tug'ilish: gaz va chang buluti |
| 2 | `spark` | **Spark** | 800–999 | 200 | 4.75% | Uchqun — birinchi harakat |
| 3 | `comet` | **Comet** | 1000–1199 | 200 | 15.65% | Kometa — orbitaga chiqqan |
| 4 | `asteroid` | **Asteroid** | 1200–1399 | 200 | 28.73% | Barqaror orbitaga joylashgan |
| 5 | `aurora` | **Aurora** | 1400–1599 | 200 | 28.71% | Qutb yog'dusi — ko'rinish |
| 6 | `moon` | **Moon** | 1600–1799 | 200 | 15.83% | Yo'ldosh — jiddiy daraja |
| 7 | `planet` | **Planet** | 1800–1999 | 200 | 4.70% | Mustaqil sayyora |
| 8 | `giant` | **Giant** | 2000–2199 | 200 | 0.76% | Ulkan sayyora — 4 xonali |
| 9 | `star` | **Star** | 2200–2299 | 100 | 0.06% | Yulduz — termoyadro sintezi |
| 10 | `nova` | **Nova** | 2300–2399 | 100 | 0.02% | Yorqinlashgan yulduz |
| 11 | `pulsar` | **Pulsar** | 2400–2499 | 100 | 0.00% | Neytron yulduz — GM nuqtasi |
| 12 | `quasar` | **Quasar** | 2500–2599 | 100 | 0.00% | Faol galaktika yadrosi |
| 13 | `galaxy` | **Galaxy** | 2600–2799 | 200 | 0.00% | Yulduzlar tizimi |
| 14 | `supernova` | **Supernova** | 2800–2999 | 200 | 0.00% | Portlash hodisasi |
| 15 | `singularity` | **Singularity** | 3000+ | ochiq | 0.00% | Yakkalik — o'lchovsiz cho'qqi |

**Tekshiruv (dastur bilan):** 15 qavat · chegaralar o'sish tartibida ✅ ·
takrorlanmagan ✅ · ulushlar yig'indisi **100.00%** ✅ · faol qavatlar
(**≥0.05%**): **9 ta** ✅

**Kenglik ritmi:** `800 · 200×7 · 100×4 · 200×2 · ochiq`
— quyi yarm keng (o'sish seziladi), o'rta siqilgan (2300–2599, siyrak
hududda aniqlik), yuqori ikkitasi yana keng (miqyos sakrashi).

## Qavat 2 — rang

**STATUS: TASDIQLANDI** ✅ — `--rw-rank-1` (kulrang `#656e81`)

Mavjud token ishlatiladi, 18 palitrada kontrastdan o'tgan — yangi qiymat
kerak emas. Kulrang = «hali shakllanmagan»; 3-qavatga o'tganda rangli
bo'lish **mukofot** sifatida seziladi.

⚠️ **Oqibat:** hozirgi `--rw-rank-1` endi 2-qavatga tegishli bo'ladi.
1-qavat (`Nebula`) rangsiz yoki alohida neytral ton olishi kerak — bu
**keyingi qaror** (rang zinapoyasini qayta taqsimlash).

## Rad etilgan variantlar (barcha qavatlar)

| Qavat | Rad etilgan | Sabab |
| --- | --- | --- |
| 1 nom | Dust | «Chang» — salbiy, kamaytiruvchi ma'no |
| 1 nom | Pulse | `Pulsar` (11-qavat) bilan ildizdosh chalkashlik |
| 1 nom | Seed | Astronomik emas |
| 2 chegara | 300/100/400 keng | Yoki o'sish sezilmaydi, yoki 15 qavatga joy qolmaydi |
| 2 nom | Ember | Cho'g' — so'nish, o'sish emas |
| 2 nom | Comet | Keyinroq 3-qavatga tanlandi |
| 2 nom | Nova | Astronomik xato (nova — portlash, eng pastda turolmaydi) |
| 3 nom | Ember | Tartib xatosi: cho'g' uchqundan keyin kelmaydi |
| 3 nom | Orbit | Jism emas, harakat yo'li |
| 3 nom | Flare | Favqulodda holat ma'nosi |
| 4 nom | Meteor | Kometa qoldig'i — bir xil ildiz, o'sish emas |
| 5 nom | Moon | 6-qavatga tanlandi (fizik tartib: oy sayyoradan keyin) |
| 5 nom | Ember | 2-qavat bilan bog'liqlik, tartib buziladi |
| 6 nom | Planet | 7-qavatga tanlandi (oy → sayyora to'g'ri) |
| 6 nom | Terra, Cinder | Past o'qilish / salbiy ma'no |
| 7 nom | Terra, Giant | Past o'qilish / keyinroq 8-qavatga o'tdi |
| 8 nom | Solstice, Belt, Alien | Tartib xatosi / orqaga qadam / mavzudan tashqari |
| 9 nom | Sun | Quyosh — milliy ramz, siyosiy noziklik |
| 9 nom | Supergiant | 10 harf, `Supernova` bilan chalkashlik |
| 10 nom | Pulsar | Kollaps keyin keladi — keyinroq 11-qavatga o'tdi |
| 10 nom | Corona | Virus assotsiatsiyasi (2020+) |
| 10 nom | Eclipse | Yorug'lik yo'qolishi — salbiy |
| 11 nom | Quasar | Galaktikadan keyin kelishi kerak — 12-qavatga o'tdi |
| 12 nom | Magnetar | `Pulsar` bilan bir xil jism sinfi |
| 13 nom | Cosmos | Butun olam — 15-qavatga tegishli |
| 13 nom | Filament | 9 harf, o'qilish 3/5, «internet to'r» bilan adashtiriladi |
| 14 nom | Zenith, Hypergiant | Jism emas / 10 harf va `Super` ildiz chalkashligi |
| 15 nom | Infinity | Matematik, astronomik emas; brend sifatida band |
| 15 nom | Cosmos, Legend | Brend bilan aralashadi / mavzusiz nom |

## Migratsiya oqibati

| Joy | Nima o'zgaradi |
| --- | --- |
| `apps/api/profiles/titles.py` | `TITLES` — 9 → **15** qator |
| 10 × `i18n/locales/*.ts` | `title.*` — 9 → **15** kalit (60 yangi tarjima) |
| `tools/check_contrast.py:79` | `range(1, 10)` → `range(1, 16)` |
| `globals.css` (18 palitra) | `--rw-rank-1…9` → `…15` — **162 → 270** qiymat |
| `globals.css` | `.rw-band-1…9` → `.rw-band-1…15` |
| `docs/07-adr/0018` | zinapoya jadvali qayta yoziladi (ADR qayta tasdiqlanadi) |
| `docs/08-technical-spec/i18n-review/{kaa,kk,ky,tg}.md` | 9 → 15 qator |

**Nomlar kodda qattiq yozilmagan** (tekshirildi) — `RatingChart.tsx:142`,
`ProfileCard.tsx:41`, `UserName.tsx:9` dinamik. Shu sababli nom
o'zgartirish arzon.
