"""Inject about.verdicts.* (24 codes × event/cause/example) into all locale TS files."""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCALES = ROOT / "apps/web/src/i18n/locales"

CODES = [
    "pending",
    "running",
    "ac",
    "wa",
    "pe",
    "tle",
    "mle",
    "ole",
    "idleness",
    "ce",
    "compile_timeout",
    "re_signal",
    "re_exit",
    "re",
    "partial",
    "skipped",
    "hacked",
    "wrong_test",
    "checker_error",
    "ie",
    "security_violation",
    "testing_aborted",
    "rate_limited",
    "denial_of_judgement",
]

HEADER = {
    "uz": {
        "about.verdicts.title": "Yechim holati kodlari (24 ta)",
        "about.verdicts.intro":
            "Platformada 24 ta verdict kodi bor. Jadvalda har biri: nima degani, nima qilish kerak va oddiy misol.",
        "about.verdicts.col.num": "№",
        "about.verdicts.col.status": "Holati",
        "about.verdicts.col.event": "Tushuntirish",
        "about.verdicts.col.cause": "Nima qilish kerak",
        "about.verdicts.col.example": "Misol",
    },
    "en": {
        "about.verdicts.title": "Verdict codes (24)",
        "about.verdicts.intro":
            "The platform defines 24 verdict codes. Each row explains the meaning, what to do, and a simple example.",
        "about.verdicts.col.num": "#",
        "about.verdicts.col.status": "Status",
        "about.verdicts.col.event": "Meaning",
        "about.verdicts.col.cause": "What to do",
        "about.verdicts.col.example": "Example",
    },
}

# event / cause / example per code — uz then en in separate dicts below
UZ: dict[str, str] = {}
EN: dict[str, str] = {}

def triple(code: str, uz_e: str, uz_c: str, uz_x: str, en_e: str, en_c: str, en_x: str) -> None:
    UZ[f"about.verdicts.event.{code}"] = uz_e
    UZ[f"about.verdicts.cause.{code}"] = uz_c
    UZ[f"about.verdicts.example.{code}"] = uz_x
    EN[f"about.verdicts.event.{code}"] = en_e
    EN[f"about.verdicts.cause.{code}"] = en_c
    EN[f"about.verdicts.example.{code}"] = en_x

triple(
    "pending",
    "Yuborish navbatda — judge hali boshlamagan.",
    "Kuting; urinishlar sahifasida holat o'zgaradi.",
    "Ko'p yuborish paytida yangi urinish bir necha soniya PENDING bo'ladi.",
    "Submission is queued — judging has not started yet.",
    "Wait; the status updates on your attempts page.",
    "During busy periods a new submit may stay PENDING for a few seconds.",
)
triple(
    "running",
    "Kod kompilyatsiya qilinmoqda yoki testlar bajarilmoqda.",
    "Sahifani tez-tez yangilamang; natija tez orada keladi.",
    "Birinchi testdan oldin RUNNING bir-ikki soniya ko'rinishi mumkin.",
    "Code is compiling or tests are running.",
    "Avoid rapid refresh; the result arrives soon.",
    "You may see RUNNING for a second or two before the first test finishes.",
)
triple(
    "ac",
    "Barcha yashirin testlar o'tdi — yechim qabul qilindi.",
    "Hech narsa tuzatish shart emas; keyingi masalaga o'ting.",
    "A+B masalasida `3 4` kiritsangiz, chiqish `7` bo'lsa — AC.",
    "All hidden tests passed — accepted.",
    "Nothing to fix; move on to the next problem.",
    "On A+B, input `3 4` with output `7` yields AC.",
)
triple(
    "wa",
    "Chiqish kutilgan javobga mos emas (Wrong Answer).",
    "Algoritm va chegaraviy holatlarni tekshiring; namunadan boshlang.",
    "Javob `10` bo'lishi kerak bo'lsa, `9` yoki `10\\n` ortiqcha qator — WA.",
    "Output does not match the expected answer.",
    "Review logic and edge cases; start from the samples.",
    "If the answer should be `10`, output `9` or an extra blank line can be WA.",
)
triple(
    "pe",
    "Format xatosi — ortiqcha/bo'sh joy, noto'g'ri qator yoki belgi.",
    "Chiqishni shartdagidek qiling; ortiqcha probel yoki `\\n` qoldirmang.",
    "Har qator `x y` bo'lishi kerak bo'lsa, oxirida `x y ` — PE.",
    "Presentation error — extra spaces, lines, or characters.",
    "Match the required format exactly; drop trailing spaces or lines.",
    "If each line must be `x y`, a trailing space on `x y ` can be PE.",
)
triple(
    "tle",
    "Vaqt chegarasi (Time Limit) buzildi.",
    "Murakkablikni pasaytiring; sekin tsikl yoki rekursiyani optimallashtiring.",
    "O(n²) tsikl n=10⁵ da TLE; O(n log n) odatda o'tadi.",
    "Time limit exceeded.",
    "Improve complexity; remove slow loops or deep recursion.",
    "An O(n²) loop at n=10⁵ often TLE; O(n log n) usually passes.",
)
triple(
    "mle",
    "Xotira chegarasi (Memory Limit) oshdi.",
    "Massiv hajmini kamaytiring; keraksiz nusxa va katta konteynerlardan qoching.",
    "10⁸ elementli `int` massivi bir necha GB — MLE.",
    "Memory limit exceeded.",
    "Shrink arrays; avoid huge copies and containers.",
    "An array of 10⁸ ints can exceed the limit — MLE.",
)
triple(
    "ole",
    "Chiqish hajmi chegaradan oshdi (Output Limit).",
    "Cheksiz chiqish yoki juda katta matn chop etmang.",
    "Har son uchun alohida qator o'rniga bitta qisqa javob yetadi.",
    "Output limit exceeded.",
    "Do not print unbounded or huge text.",
    "Print one concise answer instead of millions of lines.",
)
triple(
    "idleness",
    "Dastur juda uzoq vaqt hech narsa o'qimaydi/yozmaydi (idleness).",
    "Interaktiv masalalarda kiritmani darhol o'qing; bloklanib qolmang.",
    "Birinchi `read` dan keyin uzoq hisoblashdan oldin javob yozing.",
    "Program idle too long without reading/writing.",
    "In interactive tasks, read promptly; do not block idle.",
    "After the first read, do not compute silently for too long.",
)
triple(
    "ce",
    "Kompilyatsiya xatosi — kod build bo'lmadi.",
    "Xato matnini o'qing; sintaksis, import va Main.java nomini tekshiring.",
    "Java: `class Solution` o'rniga `public class Main` — CE.",
    "Compilation error — the code did not build.",
    "Read the compiler message; check syntax, imports, and Main.java.",
    "Java: `class Solution` instead of `public class Main` — CE.",
)
triple(
    "compile_timeout",
    "Kompilyatsiya vaqt budjetidan oshdi.",
    "Og'ir shablon yoki juda katta faylni soddalashtiring; qayta yuboring.",
    "Juda katta header-only C++ shabloni ba'zan compile timeout beradi.",
    "Compilation exceeded its time budget.",
    "Simplify heavy templates or huge translation units.",
    "Very heavy C++ templates can hit compile timeout.",
)
triple(
    "re_signal",
    "Dastur signal bilan to'xtadi (masalan, segmentation fault).",
    "Indeks, nolga bo'lish, `null` — xavfsizlikni tekshiring.",
    "`a[-1]` yoki `1/0` — RE_SIGNAL.",
    "Program stopped on a signal (e.g. segfault).",
    "Check bounds, division by zero, null access.",
    "`a[-1]` or `1/0` — RE_SIGNAL.",
)
triple(
    "re_exit",
    "Dastur nolga teng bo'lmagan chiqish kodi bilan tugadi.",
    "`System.exit(1)` yoki `abort()` ishlatmang; `return 0` bilan chiqing.",
    "C++ da `exit(1)` o'rniga `return 0` — RE_EXIT.",
    "Program exited with a non-zero code.",
    "Avoid `System.exit(1)` / `abort()`; finish with `return 0`.",
    "In C++, prefer `return 0` over `exit(1)`.",
)
triple(
    "re",
    "Eski umumiy RE kodi (tarixiy yozuvlar).",
    "Yangi urinishlarda odatda RE_SIGNAL yoki RE_EXIT ko'rasiz.",
    "Arxivdagi eski urinishda `RE` qolgan bo'lishi mumkin.",
    "Legacy generic RE (historical records).",
    "New runs usually show RE_SIGNAL or RE_EXIT instead.",
    "Old attempts in the archive may still say RE.",
)
triple(
    "partial",
    "Qisman ball — ba'zi testlar o'tdi (IOI uslubi).",
    "Qaysi testlar o'tganini ko'ring; qolganlar uchun yechimni yaxshilang.",
    "10 testdan 7 tasi to'g'ri — PARTIAL (musobaqa rejimiga bog'liq).",
    "Partial score — some tests passed (IOI-style).",
    "See which tests passed; improve the rest.",
    "7 of 10 tests correct — PARTIAL (depends on contest mode).",
)
triple(
    "skipped",
    "Test o'tkazib yuborildi (maxsus rejim yoki sozlama).",
    "Odatiy masala yuborishida kam uchraydi; staff izohiga qarang.",
    "Ba'zi musobaqalarda validator yiqilganda keyingi test SKIPPED bo'lishi mumkin.",
    "Test was skipped (special mode or configuration).",
    "Rare on normal submits; see staff notes if shown.",
    "Some contest setups skip tests after certain failures.",
)
triple(
    "hacked",
    "Qabul qilingan yechim hack testida yiqildi.",
    "Bu hack/jury jarayoni; oddiy WA emas — shart va cheklovlarni qayta o'qing.",
    "Boshqasining AC kodi maxsus testda WA bo'lsa, asl yechim HACKED bo'lishi mumkin.",
    "An accepted solution failed a hack test.",
    "Part of hack/jury flow — re-read constraints.",
    "Someone's AC failing a generated stress test may become HACKED.",
)
triple(
    "wrong_test",
    "Test yaroqsiz — muammo masala/hakam tomonda.",
    "Sizning kodingiz emas; muallifga xabar bering yoki kuting.",
    "Noto'g'ri checker yoki imkonsiz cheklov — WRONG_TEST.",
    "Invalid test — problem/checker side.",
    "Not your bug; report to authors or wait for a fix.",
    "Broken checker or impossible constraint — WRONG_TEST.",
)
triple(
    "checker_error",
    "Checker (solish) dasturida ichki xato.",
    "Foydalanuvchi aybi emas; qayta urinib ko'ring, muammo davom etsa xabar bering.",
    "Checker crash qilsa — CHECKER_ERROR, WA emas.",
    "Internal error in the checker program.",
    "Not your fault; retry, report if it persists.",
    "If the checker crashes — CHECKER_ERROR, not WA.",
)
triple(
    "ie",
    "Ichki xato (Internal Error) — tizim yoki masala sozlashida muammo.",
    "Kodni o'zgartirish shart emas; biroz kutib qayta yuboring.",
    "Vaqtincha judge nosozligi — IE; keyin o'sha kod AC bo'lishi mumkin.",
    "Internal error — platform or problem configuration.",
    "Your code may be fine; wait and resubmit.",
    "Transient judge issue — IE; same code may later AC.",
)
triple(
    "security_violation",
    "Sandbox xavfsizlik qoidasi buzildi.",
    "Fayl/tarmoq chaqiruvi, chetlab o'tish urinishi — ruxsat etilmagan.",
    "Tashqi fayl ochish yoki `system()` chaqiruvi — SECURITY_VIOLATION.",
    "Sandbox security rule violated.",
    "Forbidden file/network/system calls.",
    "Opening arbitrary files or calling `system()` — SECURITY_VIOLATION.",
)
triple(
    "testing_aborted",
    "Oldingi natija bekor qilindi — qayta tekshiruv boshlandi.",
    "Rejudge yoki hack jarayoni; yangi verdict kelguncha kuting.",
    "Staff rejudge qilganda bir lahza TESTING_ABORTED ko'rinadi.",
    "Previous result revoked — rejudging started.",
    "Rejudge or hack flow; wait for the new verdict.",
    "Staff rejudge may briefly show TESTING_ABORTED.",
)
triple(
    "rate_limited",
    "Submit tezligi chegarasi — yuborish rad etildi (429).",
    "Retry-After yoki xabardagi kutish vaqtini kuting; spam qilmang.",
    "1 daqiqada juda ko'p yuborish — RATE_LIMITED (tarixda qolishi mumkin).",
    "Submit rate limit hit — request rejected (429).",
    "Wait for Retry-After; do not spam submits.",
    "Too many submits per minute — RATE_LIMITED (may appear in history).",
)
triple(
    "denial_of_judgement",
    "Judge ishini yo'qotdi — infra muammosi (navbat qayta urinmadi).",
    "Sizning aybingiz emas; qayta yuboring; muammo takrorlansa support.",
    "Deploy vaqtida navbatdagi urinish DENIAL_OF_JUDGEMENT bo'lishi mumkin.",
    "Judge lost the job — infrastructure issue.",
    "Not your fault; resubmit; contact support if repeated.",
    "During deploy, queued jobs may get DENIAL_OF_JUDGEMENT.",
)


def fmt(key: str, val: str) -> str:
    esc = val.replace("\\", "\\\\").replace('"', '\\"')
    if len(esc) > 72:
        return f'  "{key}":\n    "{esc}",'
    return f'  "{key}": "{esc}",'


def patch_locale(code: str, strings: dict[str, str]) -> None:
    path = LOCALES / f"{code}.ts"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: list[str] = []
    skip = False
    for line in lines:
        st = line.strip()
        if st.startswith('"about.verdicts.'):
            skip = True
            continue
        if skip:
            if st.startswith('"') and not st.startswith('"about.verdicts.'):
                skip = False
                out.append(line)
            continue
        out.append(line)
    text = "\n".join(out) + "\n"
    marker = '"about.practices.readAll":'
    pos = text.find(marker)
    if pos < 0:
        raise SystemExit(f"no practices marker in {code}")
    line_end = text.find("\n", pos)
    ordered_keys = [
        "about.verdicts.title",
        "about.verdicts.intro",
        "about.verdicts.col.num",
        "about.verdicts.col.status",
        "about.verdicts.col.event",
        "about.verdicts.col.cause",
        "about.verdicts.col.example",
    ]
    for c in CODES:
        ordered_keys.extend(
            (
                f"about.verdicts.event.{c}",
                f"about.verdicts.cause.{c}",
                f"about.verdicts.example.{c}",
            )
        )
    block_lines = [fmt(k, strings[k]) for k in ordered_keys if k in strings]
    block = "\n".join(block_lines)
    text = text[: line_end + 1] + block + "\n" + text[line_end + 1 :]
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for loc, hdr in HEADER.items():
        strings = {**hdr, **(UZ if loc == "uz" else EN)}
        patch_locale(loc, strings)
    # Other locales: copy EN strings for all about.verdicts.*
    en_all = {**HEADER["en"], **EN}
    for loc in ("ru", "kk", "ky", "tg", "kaa", "tr", "zh", "es"):
        patch_locale(loc, en_all)
    print("patched all locales with", len(CODES) * 3 + len(HEADER["en"]), "verdict keys")


if __name__ == "__main__":
    main()
