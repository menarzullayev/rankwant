# ADR-0025: Rollar — staff guruhlari va obyekt mualliflari

**STATUS:** accepted (2026-09-19, HITL — 3 savol)
**Ta'siri:** `core/staff.py`, `core/staff_views.py`, `core/permissions.py`,
`core/migrations/0021`, `blog/staff_views.py`, `content/staff_views.py`,
`problems/staff_views.py`, `problems/models.py`, `problems/serializers.py`,
`contests/models.py`, `contests/staff_views.py`, `arena/staff_views.py`,
`duels/hackathons/quizzes/tournaments staff_views.py`

## Muammo

Platformada alohida `role` maydoni yo'q — rollar `is_staff`/`is_superuser`
bayroqlari va sinf a'zoligi orqali ifodalanadi. Bu ikkita muammo tug'diradi:

1. **Staff monoliti.** Har `is_staff` foydalanuvchi Qvant balansini ±sozlaydi,
   boshqa foydalanuvchini bloklaydi, masala testlarini yuklaydi va maktab
   katalogini yuritadi. Xodimlar soni oshganda «faqat yordam» xodimiga ham
   barcha kuchlar berilgan bo'ladi.
2. **Tashqi rollar yo'q.** Kontestni faqat xodim o'tkazadi (KEP'da esa ustozlar
   o'z musobaqalarini o'zlashtiradi), masala muallifi esa umuman kodda
   ifodalanmagan — «o'z kontent» strategiyasi (ADR-0005) mualliflarsiz
   masshtablanmaydi.

Mavjud yordamchi mexanizmlar: `ApiToken.Scope` (`read`/`submit`/`contest:manage`
— ADR-0008), `Contest.jury` M2M (ADR-0018), sinf rollari (`STUDENT`/`ASSISTANT`).

## Variantlar

1. **Yagona `role` maydoni** (`role = CharField(choices)`) — oddiy, lekin bitta
   foydalanuvchi bir vaqtda muallif ham, organizator ham bo'la olmaydi va har
   yangi rol = migration + `choices` kengayishi.
2. **Har rol alohida jadval** (`StaffRole`, `ContestOrganizer`,
   `ProblemAuthor`) — moslashuvchan, lekin staff ichidagi differensatsiya uchun
   Django'da allaqachon standart yechim (`Group`) bor va 4 ta jadval +
   barcha tekshiruvlarni qayta yozish arzon emas.
3. **Gibrid** — staff ICHIDA `Group` + permission'lar; tashqi rollar
   OBYEKTGA OID M2M (`Contest.organizers`, `Problem.authors`).

## Tanlov

**3-variant — gibrid** (HITL, 2026-09-19: «barchasi kerak», «gibrid»,
«birdan hammasi» — bosqichlash bo'yicha katta-refaktor xavfi egasi tomonidan
qabul qilindi).

### Guruhlar (staff ichi, `is_staff` ICHIDA bo'linish)

| Guruh | Beriladi | Berilmaydi |
|---|---|---|
| `staff-support` | foydalanuvchilar ro'yxati/ko'rish, `notify`, `broadcast` | Qvant ±, bloklash, maydon tahriri, testlar, katalog, blog |
| `staff-content` | maktab katalogi CRUD (ADR-0017), blog post'lari, content Article/Roadmap | foydalanuvchi boshqaruvi, Qvant, testlar |
| `staff-ops` | foydalanuvchi tahriri (bio, `is_active`), Qvant ±, masala/mavzu/test/report CRUD, arena/contest/duel/hackathon/quiz/tournament staff, analytics, email-kvota | blog/katalog yozuvi (bu content'ning ishi) |

- Superuser har guruhning imkoniyatiga ega (bypass).
- Bare `is_staff` (guruhsiz): faqat staff API O'QISH — list/retrieve.
  Yangi xodimga guruhlarni superuser Django admin'da biriktiradi.
- Seed migration (`core/0021`): 3 guruh yaratiladi va MAVJUD barcha
  `is_staff` foydalanuvchilar uchala guruhga ham qo'shiladi — joriy xodim
  hech narsani yo'qotmaydi. Model permission'lari migration ICHIDA
  biriktirilmaydi (`auth_permission` post_migrate'da paydo bo'ladi —
  o'lchandi: test bazasida DoesNotExist) — ular `core/groups.py` dagi
  idempotent `sync_staff_groups()` orqali post_migrate'da sinxronlanadi.

### Obyekt rollari (tashqi, `is_staff` TALAB QILINMAYDI)

| Rol | Jadval | Huquq | Yo'q |
|---|---|---|---|
| Organizator | `Contest.organizers` M2M | o'z kontestini draft qilib yaratish (`is_public=False`), tahrirlash, qatnashchilar ro'yxati; `contest:manage` PAT scope'i endi ma'noli | nashr (staff-ops), boshqaning kontesti, reyting qo'llash |
| Masala muallifi | `Problem.authors` M2M | o'z masalasini draft qilib yaratish (`is_public=False`), bayonot/editorial tahriri, O'Z draft masalasining testlarini yuklash, o'z editorial'ini ko'rish | nashr (staff-ops), boshqaning masalasi, ommaviy masala testlari |

Muallif/organizator yuzalari: `problems/mine/` va `contests/mine/`
(`IsAuthenticated`; PAT bilan yozish `contest:manage` scope'ida davom etadi).

### O'zgarmas invariantlar

- `is_staff` ma'nosi: admin panel + staff API'ga KIRISH — qoladi.
- `SessionOnly`: staff yuzalari PAT bilan ishlamaydi — qoladi.
- `staff_serializers.py` himoyalari (superuser monopoliyasi, o'zini
  bloklamaslik) — qoladi.
- Editorial tier'lari (`anonymous/free/solved/purchased/staff`, ADR-0013) —
  qoladi; muallif o'z masalasi uchun `"staff"` tier'ini oladi.
- Inline admin amal: hackathon `score_entry` — `is_staff` (alohida yuza emas).

## Sabab

- Gibrid ikkala muammoni ham yechadi: staff ichi farqi Group'ga mos (standart,
  admin paneldan boshqariladi), tashqi rollar ko'p-a'zoli tabiatga ega.
- `Contest.jury` M2M allaqachon shu naqshda ishlaydi — yangi M2M'lar
  mavjud uslubga qo'shiladi.
- Seed migration joriy xodimga ta'sir qilmaydi — regressiya xavfi nolga yaqin.

## Oqibatlar

- Ijobiy: xodim kuchlari bo'linadi (eng kam huquq prinsipi), kontest/masala
  o'sishi xodimsiz masshtablanadi, `contest:manage` scope'i bo'sh qolmaydi.
- Salbiy: har staff amalida bitta guruh so'rovi (`user.groups.filter`) —
  o'lchangan, arzon; birdan joriy etilgani uchun PR katta (egasi xavfni
  qabul qildi); yangi xodimga guruh biriktirish — qo'lda bosqich.
- Neytral: rol maydoni kiritilmadi — kelajakda boshqa rol turlari kerak
  bo'lsa, shu ADR ga qo'shimcha yoziladi.
