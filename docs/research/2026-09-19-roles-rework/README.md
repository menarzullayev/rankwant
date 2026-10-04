# Rollar tizimi — qayta ko'rib chiqish qarorlari (HITL, 2026-09-19)

> **Arxiv yozuvi.** Repoga 2026-10-04 da ko'chirildi; matn yozilgan kunidagi holatni aks ettiradi. Qaror [ADR-0025](../../07-adr/0025-roles-groups.md) ga aylangan.

**Sessiya:** AskUserQuestion, 3 savol · **Manba tahlili:** rol audit
(`core/models.py`, `core/staff.py`, `core/staff_serializers.py`,
`core/permissions.py`, `classroom/models.py`, `problems/serializers.py`,
`problems/staff_views.py`, ADR-0008/0013/0017)

## Mavjud rollar (audit xulosasi)

| Rol | Qanday ifodalangan | Asosiy vakolat / cheklov |
|---|---|---|
| Anonim mehmon | `AllowAny` endpointlar | ommaviy o'qish; editorial `"anonymous"` — yashirin |
| Ro'yxatdan o'tgan | `IsAuthenticated` | submit, arena/duel, ovoz, editorial `solved`/`purchased` (ADR-0013), PAT scope'lar (`read`/`submit`/`contest:manage`), sinfga a'zolik |
| Murabbiy (sinf) | `Classroom.owner` | o'z sinfi: vazifa, join_code; a'zo yechimlari — faqat `coach_can_view_attempts` roziligi bilan |
| Yordamchi (sinf) | `ClassroomMember.Role.ASSISTANT` | sinf ichida murabbiy yordamchisi |
| O'quvchi (sinf) | `ClassroomMember.Role.STUDENT` | vazifalarni bajarish |
| Xodim (staff) | `is_staff` + `IsAdminUser, SessionOnly` | staff API: foydalanuvchi tahriri, Qvant ±(max 1M, izohli), notify/broadcast, maktab katalogi (ADR-0017), masala testlari, barcha editorial (`"staff"`), analytics; PAT bilan ishlamaydi |
| Superuser | `is_superuser` | `is_staff` berish/olish, xodim/superuser bloklash; boshqa funksiyasi atayin kam |

Himoyalar ( mavjud): o'zini o'zi bloklash taqiqi, xodim boshqa xodimni bloklamaydi,
`is_staff` — superuser monopoliyasi (`core/staff_serializers.py:94-105`).

## Qabul qilingan qarorlar (HITL javoblari)

1. **Barcha taklif etilgan rollar joriy etiladi** — T-4 Support, T-3 Kontent
   moderator, T-1 Musobaqa organizatori, T-2 Masala muallifi.
   Rad etildi: «hozir hech narsa» (YAGNI pozitsiyasi).
2. **Mexanizm — GIBRID:**
   - staff ICHIDAGI differensatsiya → **Django `Group` + permission**lar
     (standart mexanizm, admin paneldan boshqariladi);
   - tashqi rollar → **obyektga oid jadvallar**:
     `Contest.organizers (M2M)`, `Problem.authors (M2M)` — bitta foydalanuvchi
     bir vaqtda muallif ham organizator ham bo'lishi mumkin.
   Rad etildi: yagona `role` CharField (multi-role imkonsiz), hammasi alohida
   jadval (staff ichida Group standarti bor).
3. **Bosqichlash — birdan hammasi:** 4 rol bitta PR seriyasida joriy etiladi.
   ⚠️ Egasi tanlangan xavf: staff API bir vaqtda o'zgaradi; har rol alohida
   o'lchanmaydi. Yengillashtiruvchi: gibrid asos (Group + 2 jadval) bir ADR'da
   belgilanadi, PR'lar rolni tartibda ulaydi (T-4 → T-3 → T-1 → T-2 tartibi
   implement ichida saqlanadi).

## Rollar ta'rifi (joriy etiladigan)

### T-4 Support (Django Group `staff-support`)
- Huquq: foydalanuvchini ko'rish, holat o'qish, `notify`/`broadcast`.
- Yo'q: Qvant ±, bloklash, testlar, katalog, rol berish.

### T-3 Kontent moderator (Django Group `staff-content`)
- Huquq: maktab katalogi (ADR-0017), blog/updates yozish, mazmunni
  yashirish/tuzatish.
- Yo'q: foydalanuvchi bloklash, Qvant, rol berish.

### T-1 Musobaqa organizatori (obyekt: `Contest.organizers`)
- Huquq: o'z kontestini yaratish/tahrirlash, arxivdan masala tanlash,
  qatnashchilar + standings, kontest davrida qatnashchi yechimlari;
  `contest:manage` PAT scope'i bu rol bilan ma'nolanadi.
- Yo'q: boshqaning kontesti, foydalanuvchi boshqaruvi, arxivga yozish.

### T-2 Masala muallifi (obyekt: `Problem.authors`)
- Huquq: o'z masalasini draft qilish (bayonot, testlar, editorial), staffga
  ko'rib chiqishga yuborish.
- Yo'q: nashr (staff), boshqaning masalasi, reytingga ta'sir qiluvchi maydonlar.

## Implementatsiya izohlari

- `is_staff` MA'NOSINI SAQLAYDI: admin panel + staff API'ga kirish — Group'lar
  faqat staff ICHIDA bo'linadi (SessionOnly qat'iy qoladi).
- `staff_serializers.py` dagi himoyalar o'zgarmaydi (superuser monopoliyasi,
  o'zini bloklamaslik).
- Yangi migration'lar: 2 M2M (Contest.organizers, Problem.authors) + Group
  seed (data migration).
- Qoidalar: har rol uchun `check_decisions.py` qoidasi + salbiy testlar;
  editorial tier'lar (`anonymous/free/solved/purchased/staff`) o'zgarmaydi.
- Bu hujjat implementatsiya boshlanganda ADR-00XX sifatida repoga PR orqali
  o'tadi (hujjat → repo, PR orqali — uy qoidasi).
