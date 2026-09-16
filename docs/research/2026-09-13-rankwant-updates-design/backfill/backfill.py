# -*- coding: utf-8 -*-
"""Backfill: git tarixidan Updates yozuvlarini yaratish.

Qaror (DECISION-SESSION.md, 10-savol): **aralash** — muhim o'zgarish alohida,
kichik tuzatishlar guruhda. Qaror (14-savol): manba — commit/PR/release.

Bu skript commit'larni **kalit so'z bo'yicha** mavzuli yozuvlarga guruhlaydi.
Filtrlash: `chore`, `test`, `ci`, `docs`, `style`, `refactor`, `merge` —
foydalanuvchiga ko'rinmaydi (qaror: faqat foydalanuvchi sezadigan ish).

Chiqish: `updates.json` — `manage.py load_updates` uni o'qiydi.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "rankwant"
OUT = Path(__file__).resolve().parent / "updates.json"

#: Foydalanuvchiga ko'rinmaydigan commit turlari.
SKIP_TYPES = {"chore", "test", "ci", "docs", "style", "refactor", "merge", "build"}

#: Ichki scope'lar — `fix(ci)` kabi commit'lar turi `fix` bo'lsa ham
#: foydalanuvchiga ko'rinmaydi. Tur bo'yicha filtr buni ushlamaydi.
SKIP_SCOPES = {"ci", "smoke", "e2e", "test", "deps", "build", "lint", "types"}

ENTRIES: list[dict] = [
    # ── 2026-09-06 — fundament ───────────────────────────────────────────
    {
        "date": "2026-09-06",
        "kind": "new",
        "module": "judge",
        "title": "Judge engine tanlandi — Go + nsjail",
        "body": (
            "Ikki nomzod o'lchov bilan sinovdan o'tdi: Go worker (nsjail) va "
            "Python worker (isolate). Izolyatsiya sinovlari, TLE/MLE aniqligi, "
            "fork bomb va tarmoq urinishlari tekshirildi. Go + nsjail yutdi — "
            "14/14 sinov. Qaror ADR-0004 da qayd etilgan."
        ),
        "match": ["bakeoff", "judge-go", "judge-py", "ADR-0004"],
    },
    {
        "date": "2026-09-06",
        "kind": "new",
        "module": "core",
        "title": "Platforma poydevori — backend va frontend",
        "body": (
            "Django + DRF backend (auth, masalalar, tekshiruv, musobaqalar) va "
            "Next.js frontend (SSR, i18n) ishga tushdi. Reyting formulalari "
            "ochiq — har kim hisob-kitobni tekshira oladi."
        ),
        "match": [
            "Django backend for Phase 0",
            "Next.js frontend with SSR",
            "custom test runs",
        ],
    },
    {
        "date": "2026-09-06",
        "kind": "new",
        "module": "qvant",
        "title": "Qvant iqtisodiyoti ishga tushdi",
        "body": (
            "Yopiq loop: Qvant faqat platforma ichida ishlaydi, tashqariga "
            "chiqmaydi. Kunlik streak va Activity reytingi qo'shildi."
        ),
        "match": [
            "Qvant economy, streak and Activity",
            "their own weekly marathon",
        ],
    },
    {
        "date": "2026-09-06",
        "kind": "new",
        "module": "core",
        "title": "Bildirishnomalar, virtual musobaqalar va tavsiyalar",
        "body": (
            "Reyting o'zgarganda yoki masala qayta baholanganda xabar keladi. "
            "Tugagan musobaqani virtual rejimda qayta yechish mumkin. Masala "
            "tavsiyasi va haftalik marafon qo'shildi."
        ),
        "match": ["notifications, virtual contests, recommendations"],
    },
    {
        "date": "2026-09-06",
        "kind": "new",
        "module": "content",
        "title": "O'quv kontenti va sinflar",
        "body": (
            "Maqola ↔ masala bog'lanishi, o'quv rejalari va sinf (classroom) "
            "bo'limi. Mirror musobaqalar — tashqi olimpiadani platformada "
            "qayta o'tkazish."
        ),
        "match": ["Phase 2 - own learning content"],
    },
    # ── 2026-09-07 ───────────────────────────────────────────────────────
    {
        "date": "2026-09-07",
        "kind": "new",
        "module": "profile",
        "title": "Profil sahifasi — reyting tarixi va yechilgan masalalar",
        "body": "Profilda reyting o'zgarishlari grafigi va yechilgan masalalar ro'yxati.",
        "match": ["user profile page with rating history"],
    },
    {
        "date": "2026-09-07",
        "kind": "new",
        "module": "design",
        "title": "Yangi interfeys qobig'i va mehmon sahifasi",
        "body": (
            "Masala shartlari endi Markdown va LaTeX bilan to'liq chiziladi — "
            "formulalar ham. Mehmon uchun alohida landing sahifasi qo'shildi."
        ),
        "match": [
            "render problem statements as Markdown",
            "TailAdmin UI shell",
            "every section of the chosen menu",
        ],
    },
    {
        "date": "2026-09-07",
        "kind": "new",
        "module": "arena",
        "title": "Duel va Arena — 1v1 bellashuvlar",
        "body": (
            "Duel: ikki foydalanuvchi bir xil masalani yechadi, tez yechgan "
            "yutadi. Challenges reytingi qo'shildi. Arena — bir vaqtda ko'p "
            "o'yinchi bellashadigan jonli raund."
        ),
        "match": ["quizzes and live arena rounds", "duels — 1v1 matches"],
    },
    {
        "date": "2026-09-07",
        "kind": "new",
        "module": "contests",
        "title": "Turnirlar, hakatonlar, kalendar va qidiruv",
        "body": (
            "Turnir (nokaut setkasi), hakaton, umumiy kalendar, sayt bo'ylab "
            "qidiruv va algoritm maqolalari qo'shildi."
        ),
        "match": ["tournaments, hackathons, calendar, search"],
    },
    {
        "date": "2026-09-07",
        "kind": "new",
        "module": "core",
        "title": "Boshqaruv paneli — barcha bo'limlar uchun",
        "body": (
            "Xodimlar uchun yagona boshqaruv paneli: masalalar (test yuklash "
            "bilan), musobaqalar, savol banki, testlar, arena, duel, turnir, "
            "hakaton, maqola, reja, topshiriq, do'kon, foydalanuvchi va postlar."
        ),
        "match": ["feat(admin)", "management UI for every entity"],
    },
    # ── 2026-09-08 ───────────────────────────────────────────────────────
    {
        "date": "2026-09-08",
        "kind": "new",
        "module": "design",
        "title": "Vizual uslublar — o'zingizga mosini tanlang",
        "body": (
            "Platforma bir xil ko'rinishda emas: bir nechta uslub va palitra "
            "bor, har foydalanuvchi o'zi tanlaydi."
        ),
        "match": ["user-selectable visual styles", "make clay the default"],
    },
    {
        "date": "2026-09-08",
        "kind": "new",
        "module": "contests",
        "title": "Musobaqada yechish — masalalar va kod yuborish",
        "body": (
            "Musobaqa ichida masalalar ro'yxati va kod yuborish oynasi. "
            "Namuna testlarda darhol sinab ko'rish mumkin."
        ),
        "match": ["list a contest's problems", "code submission UI"],
    },
    {
        "date": "2026-09-08",
        "kind": "new",
        "module": "problems",
        "title": "Masala sahifasi yangilandi",
        "body": (
            "Namuna testlar sahifada ko'rinadi va shu yerda ishga tushiriladi. "
            "Muharrir qurollari va yechish statistikasi qo'shildi. Yechilgan "
            "masalalar belgilanadi."
        ),
        "match": [
            "show sample tests on the problem page",
            "editor tools and solve statistics",
            "mark solved problems",
            "problem sections as top-level tabs",
        ],
    },
    {
        "date": "2026-09-08",
        "kind": "new",
        "module": "problems",
        "title": "Arxiv — filtr, masala kodi va yetti daraja",
        "body": (
            "Masalalar arxivi daraja, mavzu, holat va tartib bo'yicha "
            "filtrlanadi. Har masala kod oldi (masalan `A-100`). Qiyinlik "
            "shkalasi yetti darajaga bo'lindi va arxivga yon panel qo'shildi."
        ),
        "match": [
            "filter the problem archive",
            "problem codes and row-level statistics",
            "seven difficulty levels and an archive sidebar",
            "paginate the archive",
            "finish the archive control bar",
            "show the problem code on the problem page",
            "surface the problem code in the staff API",
            "remap difficulty to KEP",
        ],
    },
    # ── 2026-09-09 ───────────────────────────────────────────────────────
    {
        "date": "2026-09-09",
        "kind": "content",
        "module": "problems",
        "title": "KEP.uz arxivi import qilindi",
        "body": (
            "KEP.uz ning ochiq API si orqali masalalar arxivi ko'chirildi — "
            "shartlar, testlar, rasmlar va fayllar bilan. Import qilingan "
            "rasm va fayllar endi bizning saqlashimizda."
        ),
        "match": [
            "import the KEP.uz archive",
            "host the imported images",
            "copy attachments",
        ],
    },
    {
        "date": "2026-09-09",
        "kind": "new",
        "module": "problems",
        "title": "Import modeli, IOI subtask va tashqi checkerlar",
        "body": (
            "Masala modeli tashqi arxivdan import qilishga tayyorlandi. IOI "
            "uslubidagi subtask baholash va tashqi checker dasturlari "
            "qo'llab-quvvatlanadi."
        ),
        "match": ["import-ready problem model, IOI subtask"],
    },
    {
        "date": "2026-09-09",
        "kind": "new",
        "module": "problems",
        "title": "Masala sahifasi: tillar, ovoz, o'xshash masalalar, spoyler",
        "body": (
            "Har masala uchun ruxsat etilgan tillar, ovoz berish va o'xshash "
            "masalalar tavsiyasi. Yechim tahlili (editorial) spoyler darvozasi "
            "ortida — Qvant bilan ochiladi."
        ),
        "match": [
            "per-problem languages, votes, similar problems",
            "set the editorial unlock price",
            "structured statement sections",
            "favourites and problem ratings",
        ],
    },
    {
        "date": "2026-09-09",
        "kind": "new",
        "module": "problems",
        "title": "Arxiv statistikasi — mavzu bo'yicha kuch",
        "body": (
            "Qaysi mavzuda kuchli, qayerda qotib qolganingiz ko'rinadi. Har "
            "masala uchun eng tez qabul qilingan yechim, til bo'yicha."
        ),
        "match": ["show strength per topic", "fastest accepted solution"],
    },
    {
        "date": "2026-09-09",
        "kind": "improved",
        "module": "problems",
        "title": "Namuna testlar va shaxsiy testlar qulaylashdi",
        "body": (
            "Namuna testlar takrorlanuvchi bloklar o'rniga bitta jadvalda. "
            "Bir nechta shaxsiy test saqlanadi — bittasini ustiga yozish "
            "shart emas. Masala haqida xato xabar berish mumkin."
        ),
        "match": [
            "samples as one table",
            "keep several custom tests",
            "report a broken problem",
            "a queue for the problem reports",
        ],
    },
    {
        "date": "2026-09-09",
        "kind": "new",
        "module": "problems",
        "title": "Apostrofsiz qidiruv va yechuvchilar bo'limi",
        "body": (
            "«To'rttalik» ni «torttalik» deb yozsangiz ham topiladi — "
            "apostrof qidiruvga xalaqit bermaydi. Har masala ostida uni "
            "yechganlar ro'yxati."
        ),
        "match": ["search that ignores apostrophes"],
    },
    {
        "date": "2026-09-09",
        "kind": "new",
        "module": "profile",
        "title": "Profil — o'rin, eng yuqori reyting, daraja kesimi",
        "body": "Profilda joriy o'rin, eng yuqori reyting va har darajada nima yechganingiz.",
        "match": ["rank, peak rating, and what you solved at each level"],
    },
    {
        "date": "2026-09-09",
        "kind": "new",
        "module": "problems",
        "title": "Urinishlar oqimi va to'liq attempt sahifasi",
        "body": (
            "Urinishlar oqimini filtrash va kod uzunligini ko'rish. To'liq "
            "attempt sahifasi, o'quv reja jarayoni va hamjamiyat bloki."
        ),
        "match": [
            "filter the stream, and show how long the code was",
            "full attempt page, study-plan progress",
            "everyone's attempts, statement font size",
        ],
    },
    {
        "date": "2026-09-09",
        "kind": "security",
        "module": "qvant",
        "title": "Qvant auditi va judge qutqaruvi",
        "body": (
            "Har bir hamyon ledger bilan solishtiriladi — bittalab emas, "
            "ommaviy tekshiruv. Judge javob bermay qolgan urinishlar "
            "avtomatik qutqariladi."
        ),
        "match": ["audit every wallet against the ledger", "rescue attempts the judge never"],
    },
    # ── 2026-09-10 ───────────────────────────────────────────────────────
    {
        "date": "2026-09-10",
        "kind": "new",
        "module": "design",
        "title": "O'nta til — to'liq",
        "body": (
            "Interfeys o'nta tilga to'liq o'girildi: o'zbek, rus, ingliz, "
            "qozoq, qirg'iz, tojik, turk, ispan, xitoy va qoraqalpoq. "
            "To'liqlikni CI darvozasi ushlab turadi."
        ),
        "match": ["ten languages, complete", "translate API errors from their code"],
    },
    {
        "date": "2026-09-10",
        "kind": "new",
        "module": "core",
        "title": "Google, GitHub va Telegram bilan kirish",
        "body": (
            "Uch provayder orqali bir bosishda kirish. Provayderlarni "
            "sozlamalardan ulash va uzish mumkin."
        ),
        "match": [
            "sign in with Google, GitHub and Telegram",
            "connect and disconnect providers",
            "connect Telegram from settings",
        ],
    },
    {
        "date": "2026-09-10",
        "kind": "new",
        "module": "core",
        "title": "Parol tiklash va huquqiy sahifalar",
        "body": (
            "Parolni tiklash tokeni yaratiladi va ishlatiladi. Shartlar va "
            "maxfiylik sahifalari nashr etildi."
        ),
        "match": [
            "issue and consume password reset tokens",
            "publish the terms and privacy",
            "expose the password reset endpoints",
        ],
    },
    {
        "date": "2026-09-10",
        "kind": "new",
        "module": "profile",
        "title": "Hisobni o'chirish va ma'lumotni eksport qilish",
        "body": (
            "Hisobni o'chirish va o'z ma'lumotlaringizni yuklab olish. "
            "O'chirilganda taxallus anonimlashtiriladi."
        ),
        "match": ["delete their account and export their data"],
    },
    {
        "date": "2026-09-10",
        "kind": "new",
        "module": "infrastructure",
        "title": "Email — bitta provayder emas, zanjir",
        "body": (
            "Bepul planlar kunlik kvota qo'yadi, shuning uchun to'rt "
            "provayder zanjir bo'lib ishlaydi: biri yiqilsa keyingisiga "
            "o'tadi. Har yuborish qaysi provayder ishlaganini yozib boradi."
        ),
        "match": ["provider chain instead of one provider", "build the account messages ADR-0015"],
    },
    {
        "date": "2026-09-10",
        "kind": "new",
        "module": "design",
        "title": "Yangi brend belgisi",
        "body": (
            "Bitta manba fayldan barcha formatdagi ikonkalar generatsiya "
            "qilinadi. BIMI logo ham tayyor — DMARC qat'iy bo'lganda ishlaydi."
        ),
        "match": ["adopt the summit mark", "traced summit mark the single source", "BIMI logo"],
    },
    {
        "date": "2026-09-10",
        "kind": "improved",
        "module": "judge",
        "title": "Verdiktlar tarjima qilindi, checker va rejudge",
        "body": (
            "Har bir verdikt o'nta tilga tarjima qilindi, ishlamay qolgan "
            "verdiktlar ulandi, Runtime Error ikkiga bo'lindi. Special va "
            "scorer masalalar uchun checker dasturi. Ommaviy rejudge buyrug'i."
        ),
        "match": [
            "translate every verdict",
            "supply the checker program",
            "batch rejudge command",
            "let staff set the checker",
        ],
    },
    {
        "date": "2026-09-10",
        "kind": "improved",
        "module": "problems",
        "title": "Testi yo'q 870 masala olib tashlandi",
        "body": (
            "Arxivda testi bo'lmagan masalalar bor edi — ular yechilmaydi. "
            "Endi masalada test yo'qligi aytiladi va yuborish rad etiladi."
        ),
        "match": ["withdraw the 870 problems that have no tests", "say when a problem has no tests"],
    },
    {
        "date": "2026-09-10",
        "kind": "improved",
        "module": "contests",
        "title": "Reyting jadvalida o'z qatoringizni ko'rasiz",
        "body": (
            "Top 500 tashqarisida qolsangiz ham o'z natijangiz ko'rinadi — "
            "musobaqada ham, arenada ham. IOI musobaqalari endi masala soni "
            "bo'yicha emas, ball bo'yicha reytinglanadi."
        ),
        "match": [
            "outside the top 500 see their own row",
            "show a player their own rank below the top 500",
            "rank IOI contests by points",
        ],
    },
    # ── 2026-09-11 ───────────────────────────────────────────────────────
    {
        "date": "2026-09-11",
        "kind": "improved",
        "module": "design",
        "title": "Profil va sozlamalar qayta qurildi",
        "body": (
            "Profil ikki ustunli tuzilishga o'tdi, har tab alohida sahifa. "
            "Sozlamalar bo'limlarga bo'lindi. Kirish sahifalari soddalashtirildi "
            "va ro'yxatdan o'tishda maydon jonli tekshiriladi."
        ),
        "match": [
            "split settings into sections",
            "rebuild the profile as two columns",
            "strip the sign-in pages down",
            "answer while the signup form is being typed",
            "rebuild the signup and login pages",
            "mobile-only failures on the auth pages",
        ],
    },
    {
        "date": "2026-09-11",
        "kind": "new",
        "module": "profile",
        "title": "Unvonlar, rollar, onlayn holat va yutuqlar",
        "body": (
            "Reytingga qarab unvon beriladi va ism unvon rangida ko'rinadi. "
            "Profil rollari, onlayn holat va darajali yutuqlar qo'shildi."
        ),
        "match": [
            "titles, profile roles, online status",
            "colour names by title",
        ],
    },
    {
        "date": "2026-09-11",
        "kind": "new",
        "module": "profile",
        "title": "Sertifikatlar, maktab katalogi va tumanlar",
        "body": (
            "Musobaqa sertifikatlari (xitoy ismlari ham to'g'ri chiziladi). "
            "Maktab katalogi, tumanlar, murabbiy va ijtimoiy havolalar. "
            "Kuzatuvchilar jadvali va maktab tanlagichi."
        ),
        "match": [
            "certificates, school catalog, districts",
            "certificates tab, followers table",
            "Chinese names on certificates",
            "show social links on the profile card",
        ],
    },
    {
        "date": "2026-09-11",
        "kind": "new",
        "module": "profile",
        "title": "Ommaviy profil, faollik kalendari va jamoalar",
        "body": (
            "Ommaviy profil statistikasi, faollik kalendari va musobaqa "
            "tarixi. Jamoalar endpointlari ham qo'shildi."
        ),
        "match": ["add profile, account settings and teams endpoints", "public profile stats"],
    },
    {
        "date": "2026-09-11",
        "kind": "infrastructure",
        "module": "infrastructure",
        "title": "rankwant.uz ga ko'chdik",
        "body": "Platforma yangi domenga ko'chdi.",
        "match": ["prepare the move to rankwant.uz"],
    },
    # ── 2026-09-12 ───────────────────────────────────────────────────────
    {
        "date": "2026-09-12",
        "kind": "infrastructure",
        "module": "infrastructure",
        "title": "Tunnel uzilsa — texnik ishlar sahifasi",
        "body": (
            "Cloudflare Tunnel uzilganda foydalanuvchi xom xato o'rniga "
            "tushunarli «texnik ishlar» sahifasini ko'radi. Preview'ni "
            "tizimlar orasida topshirish va yuklashda avtomatik ko'tarish."
        ),
        "match": [
            "maintenance page when the preview tunnel",
            "hand the preview over between",
            "cover the old rankwant.bugvector.uz host",
            "bring the preview up at boot",
        ],
    },
    # ── 2026-09-13 ───────────────────────────────────────────────────────
    {
        "date": "2026-09-13",
        "kind": "new",
        "module": "profile",
        "title": "Davlat va maktab — bosqichma-bosqich so'rash",
        "body": (
            "Davlat va maktab darhol talab qilinmaydi — foydalanuvchi "
            "tayyor bo'lganda so'raladi, rozilik bilan. Qidiriladigan "
            "davlat tanlagichi va bayroqlar."
        ),
        "match": [
            "progressive geo collection",
            "nudge existing users to add country",
            "searchable country selector",
            "country flags via SVG",
            "show flags in profile card",
        ],
    },
    {
        "date": "2026-09-13",
        "kind": "new",
        "module": "core",
        "title": "Maktab katalogi API va telefon raqami",
        "body": (
            "Maktab katalogini to'ldirish uchun boshqaruv API si. Profilga "
            "ixtiyoriy telefon raqami — hech qachon ommaviy ko'rinmaydi."
        ),
        "match": ["school catalog API", "optional phone number"],
    },
    {
        "date": "2026-09-13",
        "kind": "new",
        "module": "core",
        "title": "Ro'yxatdan o'tish emailga qurildi",
        "body": (
            "Kirish va ro'yxatdan o'tish endi email asosida. Telegram "
            "kirishi eski widgetdan OIDC ga ko'chdi. Taxalluslar ASCII bilan "
            "cheklangan, o'xshashlari rad etiladi."
        ),
        "match": [
            "rebuild register and login around email",
            "move Telegram login off the legacy widget",
            "restrict usernames to ASCII",
            "allow Cyrillic handles",
            "require a unique email",
        ],
    },
    {
        "date": "2026-09-13",
        "kind": "new",
        "module": "design",
        "title": "SEO va ulashish — ikonkalar, og:image, canonical",
        "body": (
            "Brend ikonkalari, ijtimoiy tarmoq uchun og:image, canonical "
            "havolalar va sitemap. Kirishdan keyin foydalanuvchi qaytgan "
            "sahifaga tushadi."
        ),
        "match": [
            "wire brand icons, og:image",
            "sitemap, robots and link previews",
            "add a skip link",
        ],
    },
    {
        "date": "2026-09-13",
        "kind": "new",
        "module": "core",
        "title": "Voronka tahlili va A/B mexanizmi",
        "body": (
            "Ro'yxatdan o'tish voronkasi dashboard'i va A/B sinov mexanizmi — "
            "qaysi o'zgarish ishlayotganini o'lchash uchun."
        ),
        "match": ["funnel dashboard, plus the A/B"],
    },
    {
        "date": "2026-09-13",
        "kind": "new",
        "module": "core",
        "title": "Yangiliklar bo'limi ishga tushdi",
        "body": (
            "Platformadagi har o'zgarish endi shu yerda yozib boriladi — "
            "nima o'zgargani, qaysi turda va qaysi bo'limda. Har yozuv "
            "o'nta tilda."
        ),
        "match": ["add the platform changelog module"],
    },
    # ── Tuzatishlar (guruhlangan) ────────────────────────────────────────
    {
        "date": "2026-09-13",
        "kind": "fixed",
        "module": "design",
        "title": "Interfeys tuzatishlari",
        "body": (
            "Bir hafta davomida interfeysda topilgan nuqsonlar tuzatildi: "
            "telefonda sarlavha toshib ketardi, ajratgich chizig'i ba'zi "
            "joyda ko'rinmasdi, kirish sahifalarida faqat mobil qurilmada "
            "chiqadigan xatolar bor edi."
        ),
        "match": ["fix(web)", "fix(ui)", "fix(a11y)"],
    },
    {
        "date": "2026-09-13",
        "kind": "fixed",
        "module": "core",
        "title": "API va deploy tuzatishlari",
        "body": (
            "API tomonidagi nuqsonlar tuzatildi: Activity ommaviy profilda "
            "ko'rinmasdi, mavzu ota-onasi slug bo'lishi kerak edi, demo "
            "akkauntlarda parol tasodifiy qilindi, anonim limit soatlik "
            "oynaga o'tdi. Deploy tomonida esa konteyner eskirmasligi "
            "tekshiriladi."
        ),
        "match": ["fix(api)", "fix(deploy)"],
    },
    {
        "date": "2026-09-13",
        "kind": "performance",
        "module": "core",
        "title": "Tezlik va barqarorlik yaxshilandi",
        "body": (
            "Masalalar arxivi va reyting sahifalari tezlashtirildi: "
            "so'rovlar kamaydi, ortiqcha hisob-kitoblar olib tashlandi."
        ),
        "match": ["perf("],
    },
    {
        "date": "2026-09-13",
        "kind": "fixed",
        "module": "contests",
        "title": "Musobaqa, tekshiruv va Qvant tuzatishlari",
        "body": (
            "Musobaqada yuborilgan yechimlar natijaga qo'shilmasdi va "
            "jadval bo'sh qolardi. Tekshiruv tomonida e'lon qilingan til "
            "versiyalari judge obrazi bilan mos kelmasdi, yuborishlar "
            "umuman tekshirilmasdi. Qvant hisob-kitobida ham nuqsonlar "
            "topildi va tuzatildi."
        ),
        "match": [
            "fix(contests)",
            "fix(judge)",
            "fix(qvant)",
            "fix(problems)",
        ],
    },
    # ── Xavfsizlik va tezlik (guruhlangan) ───────────────────────────────
    {
        "date": "2026-09-09",
        "kind": "fixed",
        "module": "problems",
        "title": "Arxiv va import tuzatishlari",
        "body": (
            "Import qilingan masalalarda bir nechta nuqson topildi va "
            "tuzatildi: Markdown ba'zi belgilarni chizmasdi, formulalarda "
            "ko'rinmas bo'shliq qolardi, namuna testlar CRLF bilan "
            "saqlanardi, bo'sh teglar filtr panelini to'sib qo'yardi. "
            "Arxivda esa ikki mavzu tanlansa «yoki» emas «va» bo'yicha "
            "filtrlanadi, «qotib qolgan» havolasi esa haqiqatan filtrlaydi."
        ),
        "match": ["fix(import)", "fix(archive)"],
    },
    # ── Xavfsizlik va tezlik (guruhlangan) ───────────────────────────────
    {
        "date": "2026-09-13",
        "kind": "fixed",
        "module": "core",
        "title": "Barqarorlik — keshlar va bir vaqtli so'rovlar",
        "body": (
            "Bir nechta nozik nuqson tuzatildi: kesh yoki saqlash xizmati "
            "yiqilganda butun sayt to'xtab qolardi; yechim tahlili olti "
            "so'rov bir vaqtda kelganda olti marta haq olardi; test "
            "mukofoti bir vaqtli yuborishda ikki marta berilardi; arenada "
            "reyting jadvali cheklanmagan edi."
        ),
        "match": [
            "fix(storage)",
            "fix(search)",
            "fix(editorial)",
            "fix(quizzes)",
            "fix(arena)",
            "fix(problem)",
            "fix(admin)",
            "cache outage",
        ],
    },
    {
        "date": "2026-09-10",
        "kind": "security",
        "module": "core",
        "title": "Xavfsizlik tuzatishlari",
        "body": (
            "Bir nechta jiddiy kamchilik yopildi: Next.js kritik CVE li "
            "versiyalarda edi; sinfni o'quvchi o'zi o'chira olar va qo'shilish "
            "kodini ko'ra olardi; boshqaruv yuzasi PAT ni qabul qilardi; "
            "ijtimoiy callback `state`siz qabul qilinardi; email shablon "
            "izohlari xat matniga tushib qolardi."
        ),
        "match": [
            "upgrade Next.js off versions with critical CVEs",
            "students could delete a class",
            "reject API tokens on the staff surface",
            "reject a social callback that carries no state",
            "stop leaking template comments",
            "close three gaps in registration",
        ],
    },
    {
        "date": "2026-09-13",
        "kind": "performance",
        "module": "core",
        "title": "Tezlik — sessiya serverda o'qiladi",
        "body": (
            "Sessiya endi serverda o'qiladi, mehmon uchun ortiqcha 401 "
            "so'rovi olib tashlandi. Har sahifa ochilishida bitta ortiqcha "
            "so'rov kamaydi."
        ),
        "match": ["read the session on the server", "widen the anonymous throttle"],
    },
]


def load_commits() -> list[dict]:
    out = subprocess.run(
        ["git", "log", "--reverse", "--format=%ad|%h|%s", "--date=short"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    rows = []
    for line in out.stdout.splitlines():
        date, sha, subject = line.split("|", 2)
        m = re.match(r"^([a-z]+)(\(([^)]*)\))?!?:", subject)
        ctype = m.group(1) if m else "other"
        scope = (m.group(3) or "") if m else ""
        rows.append(
            {"date": date, "sha": sha, "subject": subject, "type": ctype, "scope": scope}
        )
    return rows


def main() -> int:
    commits = load_commits()
    usable = [
        c
        for c in commits
        if c["type"] not in SKIP_TYPES and c["scope"] not in SKIP_SCOPES
    ]
    used: set[str] = set()
    result = []

    for entry in ENTRIES:
        refs = [
            c["sha"]
            for c in usable
            if any(k.lower() in c["subject"].lower() for k in entry["match"])
        ]
        used.update(refs)
        result.append(
            {
                "released_at": entry["date"],
                "kind": entry["kind"],
                "module": entry["module"],
                "title": entry["title"],
                "body": entry["body"],
                "source_repo": "menarzullayev/rankwant",
                "source_refs": refs,
                "locale": "uz",
            }
        )

    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    orphan = [c for c in usable if c["sha"] not in used]
    (Path(__file__).resolve().parent / "orphans.txt").write_text(
        "\n".join(f"{c['date']}|{c['sha']}|{c['subject']}" for c in orphan),
        encoding="utf-8",
    )
    print(f"yozuvlar: {len(result)}")
    print(f"qamralgan commit: {len(used)} / {len(usable)}")
    print(f"qamralmagan: {len(orphan)}")
    by_kind: dict[str, int] = {}
    by_module: dict[str, int] = {}
    for r in result:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
        by_module[r["module"]] = by_module.get(r["module"], 0) + 1
    print("turlar:", dict(sorted(by_kind.items(), key=lambda x: -x[1])))
    print("modullar:", dict(sorted(by_module.items(), key=lambda x: -x[1])))
    if orphan:
        print("\nqamralmagan commit'lar (birinchi 20):")
        for c in orphan[:20]:
            print(f"  {c['date']} {c['sha']} {c['subject'][:72]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
