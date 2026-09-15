#!/usr/bin/env python3
"""UI tarjimalari TO'LIQ ekanini tekshiradi.

`uz` — manba: kalitlar shundan olinadi. Har bir til o'sha kalitlarning
HAMMASINI, bo'sh bo'lmagan qiymat bilan berishi shart.

TypeScript ham buni ushlaydi (`Record<MessageKey, string>`), lekin u
bo'sh satrni yoki tarjimasiz qoldirilgan o'zbekcha nusxani ko'rmaydi —
shuning uchun bu tekshiruv alohida turadi va CI da ishlaydi.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES_DIR = ROOT / "apps/web/src/i18n/locales"
INDEX = ROOT / "apps/web/src/i18n/messages.ts"
SOURCE = "uz"
#: Manba bilan bir xil qolishi ATAYIN bo'lgan kalitlar.
#:
#: Bir xillikni xato deb hisoblash muhim — u odatda tarjima qilishni
#: unutganni bildiradi. Lekin haqiqiy tasodiflar ham bor, shuning uchun
#: har biri shu yerda YOZMA ravishda tasdiqlanadi.
#:
#: `*` — brend va reyting nomlari: ular hech qaysi tilda tarjima
#: qilinmaydi (Codeforces «Div. 2» ni ham tarjima qilmaydi).
UNTRANSLATED_OK: dict[str, set[str]] = {
    "*": {
        "nav.qvant", "qvant.title", "leaderboard.skills", "leaderboard.contest",
        "leaderboard.activity", "leaderboard.streak", "leaderboard.challenges",
        "nav.arena", "auth.email", "hackathon.demo", "settings.channelTelegram",
        # Updates: modul nomi — atoqli nom, hech qaysi tilda tarjima qilinmaydi.
        "update.module.qvant",
        # Shablon nomlari — atoqli nom. "Aurora", "Konsol", "Jurnal" kabi
        # so'zlar bir qancha tillarda aynan yoziladi va bu TO'G'RI; ularni
        # majburan o'girish sun'iy ko'rinardi.
        "customizer.template.classic",
        "customizer.template.console",
        "customizer.template.journal",
        "customizer.template.focus",
        "customizer.template.aurora",
        # Uslub NOMLARI (`layout/styles.ts`) — atoqli ot. "Dashboard",
        # "Flat", "Material", "Editorial", "Terminal" va Glassmorphism /
        # Neumorphism / Claymorphism / Aurora hech qaysi tilda o'girilmaydi
        # (ingliz tilida shunday yoziladi, boshqalarida ham asl holida
        # qoladi). Izohlari (`style.*.hint`) esa HAR tilda tarjima
        # qilinadi — faqat `.label` shu ro'yxatda.
        "style.dashboard.label",
        "style.flat.label",
        "style.material.label",
        "style.editorial.label",
        "style.terminal.label",
        "style.glass.label",
        "style.neu.label",
        "style.clay.label",
        "style.aurora.label",
        # «Neo-brutalizm» — o'zlashma atama: o'zbek, qoraqalpoq va turk
        # tillarida bir xil yoziladi.
        "style.brutal.label",
        # «Blog» — o'zlashma so'z: o'zbek, ingliz, turk, ispan va
        # qoraqalpoq tillarida bir xil yoziladi (rus/ukrain tillarida
        # «Блог»). Majburan o'girish sun'iy ko'rinardi.
        "external.blog",
        # «Arena» — xalqaro o'zlashma: ingliz, turk, ispan, qoraqalpoq va
        # o'zbek tillarida bir xil yoziladi.
        "admin.section.arena",
        # «Virtual» — xalqaro o'zlashma: ingliz, ispan va qoraqalpoq
        # tillarida aynan shu shaklda yoziladi. `kaa` da bu so'z allaqachon
        # qabul qilingan (`contest.virtual` = "Virtual baslaw",
        # `profile.virtual` = "Virtual"), ya'ni majburan o'girish til
        # qoidasini buzardi.
        "admin.label.flag.virtual",
        # Quyidagilar MATN EMAS, identifikator: belgi, xalqaro qisqartma
        # va til kodi. Tarjima qilinsa ma'nosi buziladi, shuning uchun
        # kalit orqali o'tadi-yu, qiymati hamma tilda bir xil qoladi.
        "admin.label.text.num",      # "#" — ustun belgisi
        "admin.label.text.acmIcpc",  # musobaqa platformasi nomi
        "admin.label.text.ioi",      # olimpiada nomi
        "admin.label.lang.uz",
        "admin.label.lang.ru",
        "admin.label.lang.en",
        "admin.help.languageCodes",  # "uz / ru / en" — kodlar ro'yxati
    },
    # Qoraqalpoq tili o'zbek tiliga eng yaqini — xalqaro o'zlashmalar
    # ikkalasida ham aynan bir xil yoziladi.
    "kaa": {
        # "Navigatsiya" — rus tilidan olingan va qaraqalpoqchada ham shunday
        # yoziladi. Majburan o'girish sun'iy ko'rinardi (xuddi `nav.menu`
        # va `settings.language` kabi qo'shnilari).
        "customizer.nav",
        "nav.leaderboard", "contests.rated", "leaderboard.title", "qvant.balance",
        "nav.menu", "auth.password", "navGroup.lab", "navGroup.campus",
        "navGroup.platform", "nav.classroom", "nav.duels", "nav.tournaments",
        "nav.formulas", "attempts.verdict", "attempts.language",
        "tournament.points", "hackathon.score", "hackathon.repo",
        "settings.nav.profile", "profile.ratingColumn", "profile.tab.rating",
        "settings.company", "settings.effect.none", "settings.language",
        "settings.password", "settings.technologies", "settings.website",
        # Unvon zinapoyasi va daraja nomlari — xalqaro fizika atamalari.
        "level.expert", "level.master", "title.kvark", "title.foton", "title.elektron",
        "title.proton", "title.atom", "title.molekula", "title.kristal", "title.galaktika",
        "profile.reason.duel", "profile.virtual",
        # Qoraqalpoqchada ham shunday: o'zlashma so'zlar.
        "role.champion", "profile.online", "tier.bronze",
        "profile.tab.certificates", "cert.title", "cert.id", "leaderboard.school",
        # Updates: qoraqalpoqcha o'zbekchaga eng yaqin til — "tezlik",
        # "reyting", "profil", "dizayn" ikkalasida ham bir xil yoziladi.
        "update.kind.performance", "update.kind.design",
        "update.module.ratings", "update.module.profile", "update.module.design",
        # Masala sahifasi: "Statistika" qoraqalpoqchada ham aynan shunday
        # yoziladi — majburan o'girish sun'iy ko'rinardi.
        "problem.tab.stats",
        # Admin bo'limlari: qoraqalpoqcha o'zbekchaga eng yaqin til —
        # "Traektoriya" va "Analitika" o'zlashma, ikkalasida bir xil.
        "admin.section.roadmaps",
        "admin.section.analytics",
        # «Keyingi» — qoraqalpoqchada o'zbekchadagi bilan bir xil yoziladi.
        "pager.next",
        # Xuddi shu sabab: masala urinishlari sahifasidagi «Keyingi →».
        # `pager.next` bilan bir xil holat — ikkalasi ham ko'rib chiqildi.
        "problem.nextPage",
        # «Kod, belgi» va «testsiz» — qoraqalpoqcha o'zbekchadagi bilan
        # aynan bir xil yoziladi. Majburan o'girish sun'iy ko'rinardi.
        "problem.solvers.codeColumn", "problems.noTests",
        # «Algoritm» — qoraqalpoqchada ham shu shaklda yoziladi
        # (`nav.algorithms` = "Algoritmler"), ya'ni ildiz bir xil.
        "admin.label.text.problemExample",
        # Qoraqalpoq tili o'zbekchaga eng yaqin: quyidagilar ikkalasida
        # ham AYNAN shunday yoziladi. Har biri ko'rib chiqildi —
        # majburan o'girish sun'iy ko'rinardi.
        "admin.label.text.category",   # "Kategoriya"
        "admin.label.text.code",       # "Kod"
        "admin.label.text.language",   # "Til"
        "admin.label.text.message",    # "Xabar"
        "admin.label.text.module",     # "Modul"
        "admin.label.text.standard",   # "Standart"
        "admin.label.text.username",   # "Login"
        "admin.label.text.version",    # "Versiya"
        "admin.label.text.who",        # "Kim"
        "admin.label.status.rejectedShort",  # "Rad etildi"
        "admin.text.eventSessions",    # "... sessiya ..."
        # Texnik atamalar va brend — qoraqalpoqcha ham asl holida.
        "admin.label.text.asset",
        "admin.label.text.bio",
        "admin.label.text.checker",
        "admin.label.text.email",
        "admin.label.text.qvant",
        "admin.label.text.repo",
        "admin.label.text.slug",
        # Bo'lim nomlari va badge'lar ham ikkalasida bir xil yoziladi.
        "admin.title.duels", "admin.title.hackathons", "admin.title.tournaments",
        "admin.text.badgeRated", "admin.text.badgeRepo", "admin.text.badgeDemo",
        "admin.text.addVariant", "admin.text.variant",
        "problem.stats.title",   # "Statistika · {slug}"
        "submit.testTooltip",    # birlik va ajratgich bir xil
    },
    # Ingliz tili: «Duel» kabi so'zlar inglizchadan o'zlashgan, ya'ni
    # tarjima AYNAN o'sha so'z bo'ladi. Quyidagilar ham shunday —
    # o'zbekcha interfeysda allaqachon inglizcha yozilgan atamalar.
    "en": {"nav.duels", "level.master", "title.proton", "title.atom",
           "profile.reason.duel", "profile.virtual", "admin.label.flag.virtual",
           "admin.label.text.asset", "admin.label.text.bio",
           "admin.label.text.checker", "admin.label.text.email",
           "admin.label.text.flag", "admin.label.text.interactive",
           "admin.label.text.qvant", "admin.label.text.repo",
           "admin.label.text.slug", "admin.help.ownerRepo",
           "admin.label.shopCategory.streakFreeze",
           "admin.label.shopCategory.usernameBadge",
           "admin.text.addVariant", "admin.text.variant",   # "Variant" — atama
           "admin.text.contestSlug", "admin.title.page",
           "admin.text.badgeSuperuser", "admin.text.badgeRepo",
           "admin.text.badgeDemo",
           # "{index}: {verdict} · {time} ms" — birlik va ajratgich bir xil.
           "submit.testTooltip"},
    # Turk tilida ham «Profil» — o'zbekcha bilan harfma-harf bir xil.
    # Turk tili: bu so'zlar turkchada ham AYNAN shunday yoziladi
    # ("kim" = кто, "kod" = код, "standart" = стандарт).
    "tr": {"settings.nav.profile", "title.foton", "title.elektron", "title.proton",
           "title.atom", "title.kristal", "update.module.profile",
           "admin.label.text.code", "admin.label.text.qvant",
           "admin.label.text.slug", "admin.label.text.standard",
           "admin.label.text.who", "admin.text.badgeDemo",
           # `problems.noTests` = "testsiz" — turkchada ham aynan shunday.
           "problems.noTests",
           "submit.testTooltip"},
    # Ispan tilida ham «Virtual».
    "es": {"profile.virtual", "admin.label.flag.virtual",
           "admin.label.text.qvant", "admin.label.text.slug",
           "admin.text.badgeDemo", "submit.testTooltip"},
    # Xitoy tili: platforma valyutasining nomi — brend, o'girilmaydi.
    "zh": {"admin.label.text.qvant"},
}
#: Kalit tirnoqli ham, tirnoqsiz ham bo'lishi mumkin: prettier `quoteProps`
#: sozlamasi bilan oddiy identifikatorlardan tirnoqni olib tashlaydi va
#: faqat tirnoqlisini qidirgan tekshiruv o'sha kalitni JIMGINA o'tkazib
#: yuborardi — o'lchandi, 161 o'rniga 160 ta kalit ko'rindi.
PAIR = re.compile(r'^\s*(?:"([^"]+)"|([A-Za-z_$][\w$]*)):\s*"((?:[^"\\]|\\.)*)",\s*$', re.M)


def load(path: Path) -> dict[str, str]:
    return {
        quoted or bare: value
        for quoted, bare, value in PAIR.findall(path.read_text(encoding="utf-8"))
    }


def declared_locales() -> list[str]:
    block = re.search(r"export const LOCALES = \[(.*?)\] as const;", INDEX.read_text(), re.S)
    if block is None:
        sys.exit("messages.ts da LOCALES topilmadi")
    return re.findall(r'"([a-z-]+)"', block.group(1))


def main() -> int:
    codes = declared_locales()
    if SOURCE not in codes:
        sys.exit(f"manba til {SOURCE!r} LOCALES da yo'q")

    source = load(LOCALES_DIR / f"{SOURCE}.ts")
    if not source:
        sys.exit(f"{SOURCE}.ts bo'sh yoki o'qib bo'lmadi")

    problems: list[str] = []
    for code in codes:
        path = LOCALES_DIR / f"{code}.ts"
        if not path.exists():
            problems.append(f"{code}: fayl yo'q ({path.name})")
            continue
        values = load(path)
        missing = [k for k in source if k not in values]
        extra = [k for k in values if k not in source]
        blank = [k for k, v in values.items() if not v.strip()]
        allowed = UNTRANSLATED_OK["*"] | UNTRANSLATED_OK.get(code, set())
        same = [
            k
            for k, v in values.items()
            if code != SOURCE and k not in allowed and v == source.get(k)
        ]
        for nom, rows in (("yetishmaydi", missing), ("ortiqcha", extra), ("bo'sh", blank)):
            if rows:
                problems.append(f"{code}: {len(rows)} kalit {nom} — {rows[:5]}")
        if same:
            problems.append(f"{code}: {len(same)} kalit tarjimasiz (uz bilan bir xil) — {same[:5]}")

    # ⚠️ Bu yerda ILGARI erta `return 1` bor edi: paritet buzilsa qolgan
    # qoidalar umuman ishlamasdi. Natijada bitta uzilish ikki bosqichda
    # ochilardi — avval paritet tuzatiladi, keyin navbatdagi qoida
    # qizaradi. Endi hammasi BIR o'tishda yig'iladi.
    problems += check_usage(source)
    problems += check_templates(source)
    problems += check_server_registry()
    problems += check_key_shape(source)
    problems += check_country_locales()
    problems += check_country_table_coverage()
    problems += check_review_sheets()

    if problems:
        print("i18n to'liq emas:")
        for row in problems:
            print(f"  {row}")
        return 1

    templates = len(template_keys())
    print(
        f"Tekshirildi: {len(codes)} til × {len(source)} kalit "
        f"+ {templates} shablon oila — to'liq ✓"
    )
    return 0

#: `t(locale, "kalit")` — kalit qo'lda yozilgan joylar. Shablon satrlari
#: (`t(locale, `prefix.${x}`)`) bu yerga tushmaydi: ular statik emas.
#:
#: Birinchi argument ATAYLAB erkin: `t(locale, …)` ham, `t(useLocale(), …)`
#: ham uchraydi. Ilgari faqat `[A-Za-z_.]+` olinardi, ya'ni funksiya
#: chaqiruvi bilan boshlangan satr **jimgina o'tkazib yuborilardi** —
#: salbiy test shuni tutdi (`python tools/check_negative.py`). Endi qavs
#: va nuqtadan iborat har qanday ifoda qabul qilinadi.
CALL_RE = re.compile(r'\bt\(\s*[A-Za-z_$][\w$]*(?:\(\s*\))?(?:\s*\.\s*[\w$]+)*\s*,\s*"([a-zA-Z0-9_.]+)"')
#: Kalitlar qaysi fayllarda qidiriladi. ⚠️ `pathlib.glob` qavs
#: kengaytmasini (`*.{ts,tsx}`) QO'LLAB-QUVVATLAMAYDI — u bash xususiyati.
#: Bir marta shu xato qilingan edi: glob hech narsa topmagan, tekshiruv
#: esa «to'liq ✓» deb turgan (salbiy test tutdi).
SOURCE_SUFFIXES = (".ts", ".tsx")
SOURCE_DIR = ROOT / "apps/web/src"


def _source_files() -> list[Path]:
    """Tekshiriladigan manba fayllar — `i18n/` katalogidan tashqari.

    ⚠️ `pathlib.glob` qavs kengaytmasini (`*.{ts,tsx}`) QO'LLAB-
    QUVVATLAMAYDI — u bash xususiyati. Bir marta shu xato qilingan edi:
    glob hech narsa topmagan, tekshiruv esa «to'liq ✓» deb turgan
    (salbiy test tutdi). Shu sababli kengaytmalar ALOHIDA aylanadi.
    """
    files = [p for suffix in SOURCE_SUFFIXES for p in SOURCE_DIR.rglob(f"*{suffix}")]
    files = [p for p in files if "i18n" not in p.parts]
    if not files:
        # Ko'r bo'lib qolmasin: fayl topilmasa bu XATO.
        raise SystemExit(f"i18n: manba fayllar topilmadi ({SOURCE_DIR})")
    return files


def used_keys() -> dict[str, list[str]]:
    """Kodda `t(locale, "...")` bilan chaqirilgan kalitlar → fayllar."""
    found: dict[str, list[str]] = {}
    for path in _source_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for key in CALL_RE.findall(text):
            found.setdefault(key, []).append(path.name)
    return found


def check_usage(source: dict[str, str]) -> list[str]:
    """Har ishlatilgan kalit manbada bor bo'lsin.

    Aks holda foydalanuvchi xom kalit nomini ko'radi — `t()` zaxirasi
    kalitning o'zini qaytaradi.
    """
    missing = sorted(key for key in used_keys() if key not in source)
    return [f"ishlatilgan, lekin manbada yo'q: {key}" for key in missing[:10]]


#: `t(locale, `prefix.${expr}`)` — kalit qismi SHABLON satridan yasaladi.
#:
#: Nega kerak (13-band): `CALL_RE` faqat qo'lda yozilgan kalitlarni
#: ko'radi, shablon satrlari esa **statik emas**. Natijada
#: `customizer.template.${item.id}` uchun `customizer.template.aurora`
#: yo'q bo'lsa ham tekshiruv yashil turardi — foydalanuvchi esa xom
#: kalit ko'rardi. Aynan shu sinf bir marta panelda 9 ta xom kalit
#: bergan edi.
#:
#: Shablonni TO'LIQ hal qilib bo'lmaydi (qiymat ish vaqtida ma'lum),
#: lekin qamrovni TEKSHIRISH mumkin: prefiksga mos BARCHA kalitlar
#: ro'yxatga olinadi va har bir `` `prefiks.${x}` `` uchun shablondan
#: oldin va keyin keladigan matn bo'yicha mos kalit borligi talab
#: qilinadi.
TEMPLATE_CALL = re.compile(r"\bt\([^()]*,\s*(`[^`]+`)\s*\)")
TEMPLATE_RE = re.compile(
    r"`([a-zA-Z0-9_.]*)\$\{[^}]+\}([a-zA-Z0-9_.]*)`",
)


def template_keys() -> dict[str, list[str]]:
    """Shablon kalitlar → fayllar. Faqat `t(...)` ichidagilar."""
    found: dict[str, list[str]] = {}
    for path in _source_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for call in TEMPLATE_CALL.finditer(text):
            template = call.group(1)
            # Faqat kalitga o'xshagan shablonlar: `foo.${x}` / `${x}`.
            for prefix, suffix in TEMPLATE_RE.findall(template):
                if not prefix and not suffix:
                    continue
                key = f"{prefix}*{suffix}"
                found.setdefault(key, []).append(path.name)
    return found


def check_templates(source: dict[str, str]) -> list[str]:
    """Har bir shablon kalit uchun mos kalit HAQIQATAN mavjud bo'lsin."""
    problems: list[str] = []
    for template, files in sorted(template_keys().items()):
        prefix, suffix = template.split("*", 1)
        # Prefiks va suffiksga mos kalitlar (suffiks bo'sh bo'lsa — hammasi).
        matches = [
            key
            for key in source
            if key.startswith(prefix) and (not suffix or key.endswith(suffix))
        ]
        # Kalit prefiksning O'ZI bo'lmasin: `customizer.tab` mos kelmaydi.
        matches = [key for key in matches if key != prefix.rstrip(".")]
        if not matches:
            problems.append(
                f"shablon kalitga mos kalit yo'q: `{template}` ({', '.join(files)})"
            )
    return problems


def check_server_registry() -> list[str]:
    """Server BARCHA tillarni ro'yxatga olishini tekshiradi.

    ⚠️ Nega kerak: bir marta `registerMessages` ichiga shartsiz
    `registry.clear()` qo'yilgan edi va `messages.server.ts` dagi tsikl
    faqat OXIRGI tilni qoldirardi. Natijada SSR'da o'nlab xom kalit
    chiqdi (`home.start`, `nav.contests`, …) — holbuki lint, types,
    build va shu tekshiruvning o'zi YASHIL turgan edi (o'lchandi,
    brauzerda). Bu statik nazorat o'sha sinfni qaytaradi.
    """
    path = ROOT / "apps/web/src/i18n/messages.server.ts"
    if not path.exists():
        return [f"messages.server.ts topilmadi ({path})"]
    text = path.read_text(encoding="utf-8")

    problems: list[str] = []
    # 1. Tsikl `evict` bermasdan chaqirishi shart.
    #
    #    ⚠️ Uchinchi argumentni NOMI bo'yicha emas, MAVJUDLIGI bo'yicha
    #    tekshiramiz: uni `true`, `1`, yoki `evict` deb yozish mumkin.
    #    Faqat `evict` so'zini qidirish o'lik tekshiruv bo'lardi —
    #    birinchi yozganimda aynan shunday bo'ldi va salbiy test tutdi.
    calls = re.findall(r"registerMessages\(([^)]*)\)", text)
    if not calls:
        problems.append("messages.server.ts: registerMessages chaqiruvi yo'q")
    for args in calls:
        if len([a for a in args.split(",") if a.strip()]) > 2:
            problems.append(
                "messages.server.ts: serverda uchinchi argument berilmasin "
                "(`evict` faqat klient uchun — aks holda bir til qoladi)"
            )
            break
    # 2. O'nta tilning hammasi `ALL` da bo'lishi shart.
    #    Yozuv qisqa shaklda (`uz,`) ham, to'liq shaklda (`uz: uz,`) ham
    #    bo'lishi mumkin — ikkalasi ham qabul qilinadi.
    block = re.search(r"const ALL[^{]*\{(.*?)\n\};", text, re.S)
    if block is None:
        problems.append("messages.server.ts: `ALL` lug'ati topilmadi")
    else:
        codes = re.findall(
            r"^\s*([a-z]{2,3})\s*(?::|,)", block.group(1), re.M
        )
        if len(codes) != 10:
            problems.append(
                f"messages.server.ts: `ALL` da {len(codes)} til bor, 10 kutilgan"
            )
    return problems


def check_key_shape(source: dict[str, str]) -> list[str]:
    """Har kalit `namespace.name` shaklida bo'lishini talab qiladi.

    ⚠️ Nega kerak: `empty` kaliti bir vaqtlar PREFIKSSIZ edi va 10 tilda
    ham, 34 chaqiruvda ham shunday ishlatilardi. U ishlardi
    (`MessageKey = keyof typeof uz` uni to'g'ri tip qiladi), lekin
    qolgan 1344 kalitdan farqli edi — umumiy qisqa nom to'qnashuvga moyil
    va `grep '"empty"'` kabi qidiruvlar prefiksli kalitlarni topmaydi.

    Kalit `common.empty` ga ko'chirilgach istisno ro'yxati OLIB TASHLANDI:
    endi qoida istisnosiz, ya'ni kelajakda yana prefikssiz nom qo'shilsa
    CI darhol qizaradi. Istisno qo'shishdan oldin o'ylab ko'ring —
    prefiksli nom deyarli har doim to'g'riroq.
    """
    problems: list[str] = []
    for key in sorted(source):
        if "." in key:
            continue
        problems.append(
            f"uz.ts: `{key}` prefikssiz — kalit `namespace.name` shaklida "
            f"bo'lsin (masalan `common.{key}`)"
        )
    return problems


def check_country_locales() -> list[str]:
    """Har til mamlakat nomini o'z tilida olishini tekshiradi.

    ⚠️ Nega kerak: `lib/countries.ts` jadvalni faqat uz/ru uchun
    ishlatardi va qolgan tillar `Intl.DisplayNames` ga tushardi. Node
    o'lchovi bu to'g'ri deb ko'rsatdi — lekin **brauzer** `kaa`, `kk`,
    `ky`, `tg` uchun hudud ma'lumotini bermaydi va inglizchaga tushadi:
    qoraqalpoqcha UI da "Germany" chiqardi (o'lchandi, Chrome'da).

    ⚠️ Node bilan o'lchash ALDAMCHI: Node `kk`/`ky`/`tg` uchun ruscha
    qaytaradi, Chrome yo'q. Shuning uchun bu tekshiruv **manba kodni**
    o'qiydi — ICU qobiliyatini emas — va jadval qamrovini talab qiladi.

    Qoida: ICU ma'lumoti YO'Q tillar `CYRILLIC` yoki `LATIN_UZ` da
    bo'lishi shart. ICU ma'lumoti BOR tillar (en, tr, zh, es va boshqalar)
    jadvalga tushmasligi kerak — aks holda tarjima buziladi (`tr` ni
    qo'shganda "Almanya" o'rniga "Germaniya" chiqqan edi).
    """
    path = ROOT / "apps/web/src/lib/countries.ts"
    if not path.exists():
        return [f"countries.ts topilmadi ({path})"]
    text = path.read_text(encoding="utf-8")

    #: Brauzerda ICU hudud ma'lumoti YO'Q tillar (Chrome'da o'lchandi).
    ICU_MISSING = {"uz", "kaa", "kk", "ky", "tg"}
    #: ICU bor tillar — jadval ularga TEGMASLIGI shart.
    ICU_OK = {"en", "tr", "zh", "es"}

    def listed(name: str) -> set[str] | None:
        m = re.search(rf"const {name}: Locale\[\] = \[(.*?)\];", text, re.S)
        if m is None:
            return None
        return set(re.findall(r'"([a-z]{2,3})"', m.group(1)))

    cyrillic = listed("CYRILLIC")
    latin = listed("LATIN_UZ")
    if cyrillic is None or latin is None:
        return ["countries.ts: CYRILLIC yoki LATIN_UZ ro'yxati topilmadi"]

    covered = cyrillic | latin
    problems: list[str] = []

    missing = sorted(ICU_MISSING - covered)
    if missing:
        problems.append(
            f"countries.ts: {missing} jadvalda yo'q — brauzerda mamlakat "
            f"nomi inglizcha chiqadi"
        )
    broken = sorted(covered & ICU_OK)
    if broken:
        problems.append(
            f"countries.ts: {broken} jadvalga tushgan, holbuki ICU ularni "
            f"o'zi tarjima qiladi — nom buziladi"
        )
    return problems


def check_country_table_coverage() -> list[str]:
    """Jadval `CODES` dagi HAR kodni qoplashi shart.

    ⚠️ Nega kerak: `check_country_locales()` faqat RO'YXATLARNI tekshiradi
    ("qaysi til qaysi guruhda"). Jadvalning o'zi to'liqmi — hech qayerda
    qo'riqlanmagan edi. Bitta kod tushib qolsa `countryName()` jimgina ICU
    ga tushadi va o'sha til uchun **inglizcha** nom chiqadi — aynan
    tuzatilgan xato qaytadi.

    O'lchandi: `CODES` 249, jadval 249, farq 0. Bu qoida shu tenglikni
    ushlab turadi.
    """
    countries = ROOT / "apps/web/src/lib/countries.ts"
    names = ROOT / "apps/web/src/lib/country-names.ts"
    for p in (countries, names):
        if not p.exists():
            return [f"{p.name} topilmadi ({p})"]

    ctext = countries.read_text(encoding="utf-8")
    m = re.search(r'const CODES\s*=\s*\n?\s*"(.*?)"\.split', ctext, re.S)
    if m is None:
        return ["countries.ts: CODES ro'yxati topilmadi"]
    codes = set(m.group(1).split())

    ntext = names.read_text(encoding="utf-8")
    rows: dict[str, tuple[str, str]] = {}
    for r in re.finditer(
        r'"([A-Z]{2})":\s*\[\s*"([^"]*)"\s*,\s*"([^"]*)"\s*\]', ntext
    ):
        rows[r.group(1)] = (r.group(2), r.group(3))

    problems: list[str] = []
    missing = sorted(codes - rows.keys())
    if missing:
        problems.append(
            f"country-names.ts: {len(missing)} kod jadvalda yo'q "
            f"({', '.join(missing[:8])}{'…' if len(missing) > 8 else ''}) — "
            f"bu tillarda nom inglizcha chiqadi"
        )
    extra = sorted(rows.keys() - codes)
    if extra:
        problems.append(
            f"country-names.ts: {extra} jadvalda bor, lekin CODES da yo'q — "
            f"o'lik qator"
        )
    # Bo'sh qiymat ham inglizchaga tushish bilan barobar: jadval topiladi,
    # lekin `""` qaytadi va UI da mamlakat nomi ko'rinmaydi.
    blank = sorted(c for c, (a, b) in rows.items() if not a.strip() or not b.strip())
    if blank:
        problems.append(
            f"country-names.ts: {blank[:8]} qatorida bo'sh qiymat — "
            f"UI da nom ko'rinmaydi"
        )
    return problems


def check_review_sheets() -> list[str]:
    """Ko'rib chiqish varaqlari joriy lug'atga mos bo'lsin.

    ⚠️ Nega kerak: varaqlar `docs/08-technical-spec/i18n-review/` da yotadi
    va ona tilida so'zlashuvchi odam ularni **qo'lda** o'qiydi. Ular
    lug'atdan orqada qolsa, odam allaqachon o'zgargan matnni ko'rib
    chiqadi — natija behuda va bundan ham yomoni, tasdiqlanmagan matn
    "tekshirilgan" degan taassurot qoldiradi.

    Tekshiriladi: varaq bormi, kalitlar soni lug'atga tengmi, eski
    (ko'chirilgan) kalit qolmaganmi.
    """
    sheets = ROOT / "docs/08-technical-spec/i18n-review"
    if not sheets.exists():
        return [f"i18n-review papkasi topilmadi ({sheets})"]

    source = LOCALES_DIR / f"{SOURCE}.ts"
    if not source.exists():
        return [f"manba lug'at topilmadi ({source})"]
    # Manbadagi `"kalit":` yozuvlari — varaqdagi qatorlar soni shunga teng.
    want = len(re.findall(r'^\s+"([\w.]+)":\s', source.read_text(encoding="utf-8"), re.M))

    problems: list[str] = []
    for code in ("kk", "ky", "tg", "kaa"):
        path = sheets / f"{code}.md"
        if not path.exists():
            problems.append(f"i18n-review/{code}.md yo'q")
            continue
        text = path.read_text(encoding="utf-8")
        got = len(re.findall(r"^\|\s+`", text, re.M))
        if got != want:
            problems.append(
                f"i18n-review/{code}.md: {got} qator, lug'atda {want} kalit — "
                f"varaq eskirgan, qayta yaratish kerak"
            )
        # Ko'chirilgan kalit: `empty` bir vaqtlar prefikssiz edi.
        if re.search(r"^\|\s+`empty`", text, re.M):
            problems.append(
                f"i18n-review/{code}.md: eski `empty` kaliti qolgan — "
                f"`common.empty` bo'lishi kerak"
            )
    return problems


if __name__ == "__main__":
    raise SystemExit(main())