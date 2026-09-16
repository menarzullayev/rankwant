# SEO/mahsulot sessiyasi — TEKSHIRILGAN hisobot

> **Bu fayl nima.** Boshqa sessiyaning SEO/mahsulot xulosasi (`SESSION-SUMMARY-
> 2026-09-13-seo-mahsulot.md`) **mustaqil tekshirildi**: har da'vo source kod
> va **jonli sayt** bilan solishtirildi.
>
> **Tekshiruv sanasi:** 2026-09-14, `main` = `33ea38f` (lokal = origin)
> **Usul:** `git merge-base --is-ancestor` · `grep` source · `curl` jonli sayt

---

## 0. Xulosa: bu xulosa **aniq** — oldingi ikkitasidan farqli

Oldingi ikki tekshiruvda jiddiy nomuvofiqlik topilgan edi (marshrutlar
eskirgan, tekshiruv buyrug'i qamrovsiz). **Bu xulosada bunday emas** —
o'lchangan har raqam va har da'vo tasdiqlandi. Faqat **uchta kichik
aniqlik** va **bitta yangi topilma** bor.

---

## 1. Tasdiqlangan da'volar (dalil bilan)

### Git

| Da'vo | Natija |
|---|---|
| HEAD = `33ea38f` | ✅ `git log --oneline -1` |
| 4 commit `main` tarixida | ✅ `710d850` (117 orqada) · `e74af03` (116) · `259d9b6` (115) · `239a321` (114) |
| `git rev-list --count 239a321..main` = **114** | ✅ **aniq 114** |
| Lokal = origin | ✅ |

### Source kod

| Da'vo | Dalil |
|---|---|
| `layout.tsx` da `icons` bor | ✅ `layout.tsx:154` |
| `og:image` / `openGraph` bor | ✅ `layout.tsx:163` |
| `twitter:card` = `summary_large_image` | ✅ `layout.tsx:176` (endi `"summary"` EMAS) |
| `metadataBase` bor | ✅ `layout.tsx:143` |
| `canonical` bor | ✅ `layout.tsx:150` + 11 joyda |
| **`hreflang` YO'Q** | ✅ `alternates` bor, lekin faqat `canonical` — `languages` yo'q |
| **JSON-LD: faqat `Organization` + `WebSite`** | ✅ `Event` va `LearningResource` **yo'q** → **3.2 ochiq** |
| Shriftlar self-host, `preload: false` | ✅ `next/font/google`, `preload: false` (43, 52-qatorlar) |
| **`--rw-font-mono` ta'riflangan, ishlatilmaydi** | ✅ faqat `globals.css:144` da — boshqa havola **0** → **3.4 ochiq** |
| **`Content-Language` / `Vary` app kodida yo'q** | ✅ (topilganlari faqat `.venv` ichida) → **3.3 ochiq** |
| Telefon `PRIVACY_FIELDS` da **yo'q** | ✅ ro'yxat: `email, birth_date, country, school, grade, website, online, coach, social` |
| `default_hidden_fields()` = `["email"]` | ✅ `models.py:32` |
| `phone` ixtiyoriy | ✅ `models.py:123` `CharField(max_length=20, blank=True)` |
| A/B cookie = `rw_exp` | ✅ `lib/experiments.ts:11` `EXP_COOKIE = "rw_exp"` |
| `bimi.svg` mavjud | ✅ `apps/web/public/brand/bimi.svg` |
| 3 ta dinamik og-rasm marshruti | ✅ `contests/[slug]`, `problems/[slug]`, `users/[username]` |

### Jonli sayt (`curl`)

| Da'vo | Natija |
|---|---|
| `fonts.googleapis` = 0 | ✅ **0** |
| `Set-Cookie: rw_exp` | ✅ `rw_exp=geo%3Aa; Max-Age=15552000; SameSite=lax` |
| canonical / manifest / icon / og:image | ✅ 1 / 1 / 1 / 2 |
| JSON-LD jonli | ✅ `Organization` 1 · `WebSite` 1 — **`Event`/`LearningResource` yo'q** |
| 3 dinamik og-rasm | ✅ **uchalasi `200 image/png`** |
| `/api/v1/staff/analytics/` anonim | ✅ **401** |
| `hreflang` jonli | ✅ **0** |

---

## 2. Uchta aniqlik (kichik)

| # | Xulosada | Haqiqat |
|---|---|---|
| **1** | `public/brand/` | **`apps/web/public/brand/`** — monorepo, `web` ilovasi ichida |
| **2** | "5 ta tayyor PNG" | Hozir **6 ta PNG**: `mark-32/96/180/192/512` + **`og-default.png`** (35 KB, keyinroq qo'shilgan). Yana 2 ta SVG + `bimi.svg`. Audit paytida 5 ta edi — hozir o'quvchi 6 topadi |
| **3** | `manifest` | `manifest.ts` — **marshrut** (Next.js Metadata API), statik fayl emas |
| **4** | `docs/` o'zbekcha | `README.md` — **o'zbekcha** ✅; `docs/README.md` — **aralash** (sarlavha inglizcha, matn o'zbekcha) |

---

## 3. ⚠️ YANGI TOPILMA — 3.3 vazifasi uchun hal qiluvchi

Xulosa shunday deydi: *"`Content-Language` + `Vary: Accept-Language`
sarlavhalari. `Vary: Cookie` **qo'shilmasin** — keshni o'chiradi."*

**Bu to'g'ri, lekin chala.** Jonli o'lchov ko'rsatdi — **`Vary` allaqachon
mavjud**:

```
Vary: rsc, next-router-state-tree, next-router-prefetch,
      next-router-segment-prefetch, Accept-Encoding
```

Ya'ni Next.js o'zi `Vary` yozadi. Demak:

- ❌ `Vary: Accept-Language` deb **qayta yozish** → Next.js qiymatlarini
  **yo'q qiladi** → RSC/router keshi buziladi
- ✅ To'g'ri yo'l — mavjud qiymatga **qo'shish** (`Accept-Language` ni
  oxiriga ulash), almashtirish emas

`Content-Language` esa haqiqatan yo'q — uni qo'shish mumkin.

**Kutilayotgan natija (aniqlashtirilgan):** `Vary` da `Accept-Language` bor
**va** Next.js qiymatlari saqlanib qolgan; `Content-Language` qo'shilgan.

---

## 4. Vazifalar — tekshiruvdan keyingi holat

| # | Vazifa | Ustuvorlik | Holat (tekshirildi) |
|---|---|---|---|
| **3.2** | `Event` + `LearningResource` JSON-LD | 🟡 O'rta-yuqori | ✅ **OCHIQ** — jonli saytda ham yo'q. Eng aniq va o'lchanadigan qadam |
| **3.3** | `Content-Language` + `Vary` | 🟡 O'rta | ✅ **OCHIQ** — ⚠️ **qo'shish**, qayta yozish EMAS (§3) |
| **3.1** | `hreflang` — qaror kerak | 🔴 Qaror kutilyapti | ✅ **OCHIQ** — jonli saytda 0 |
| **3.4** | `--rw-font-mono` | 🟢 Past | ✅ **OCHIQ** — ta'riflangan, havola 0 |
| **3.5** | `docs/` + `README` inglizcha | 🟢 Past | ✅ **OCHIQ** — `README.md` o'zbekcha, `docs/` aralash |
| **3.6** | `bimi.svg` DNS + VMC | 🟢 Past | ✅ **OCHIQ** — fayl bor, DNS/sertifikat tashqi |

**Tasdiqlandi:** 4 bosqich tugagan, 12 qarordan 11 tasi bajarilgan —
bajarilmagani **`hreflang`** (qaror kutilyapti).

---

## 5. Xotira papkasidagi uch xulosa — farqi

| Fayl | Ish oqimi |
|---|---|
| `SESSION-SUMMARY-2026-09-13-seo-mahsulot.md` | **SEO/mahsulot** (shu hujjat manbasi) |
| `SESSION-SUMMARY-2026-09-13.md` | Lighthouse / a11y / performance |
| `SESSION-SUMMARY-2026-09-14.md` | CI / ops (runner, MinIO, WSL, zaxira) |

Ular **turli ish oqimlari** — birlashtirmang. Har biri alohida
`rankwant-review/` dagi tekshirilgan nusxaga ega.

---

## 6. Keyingi sessiya uchun boshlang'ich nuqta

1. **`main` HEAD ni o'lchang** — bu fayl `33ea38f` da yozilgan.
2. **3.2** — eng mantiqiy qadam: `contests/[slug]/page.tsx` va
   `problems/[slug]/page.tsx` da `generateMetadata` **bor**, JSON-LD ni
   shu yerga qo'shish mumkin. Natija Google'da o'lchanadi.
3. **3.3** — `Vary` ni **qo'shish**, almashtirmaslik (§3). Salbiy test:
   Next.js qiymatlari hali ham sarlavhada turibdimi.
4. O'lchovsiz xulosa chiqarmang: jonli `curl` — eng arzon dalil.
