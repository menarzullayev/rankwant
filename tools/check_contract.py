"""Judge shartnomasi: protocol.md ↔ Go struct ↔ Python JudgeJob.

Nega kerak: API va judge alohida sinaladi (API judge'ni mock qiladi,
bake-off harness job'ni o'zi quradi), shuning uchun ular orasidagi
nomuvofiqlik ikkala to'plamda ham ko'rinmaydi. Amalda ikkita shunday
nomuvofiqlik topildi:

  * API `input_ref`/`output_ref` yuborardi, judge `input`/`expected`
    kutardi — HAR submission WA olardi;
  * judge natijada `attempt_id` qaytarmasdi — verdict hech qachon
    yozilmasdi, urinish PENDING qolardi.

Ishlatish:  python3 tools/check_contract.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
PROTOCOL = REPO / "services/bakeoff/protocol.md"
GO_PROTOCOL = REPO / "services/judge-go/protocol.go"
PY_PROVIDER = REPO / "apps/api/judging/provider.py"
PY_SERVICES = REPO / "apps/api/judging/services.py"

# Kirish shartnomasi: web nima YUBORADI ↔ API nima KUTADI.
# Foydalanuvchi nomi/email maydoni bir marta `username` dan `identifier`
# ga o'zgardi (4-qaror) va bu ikkala tomonni birga yangilashni talab
# qildi. Web yangilandi, API konteyneri esa eski image'da qolib ketdi:
# sayt `identifier` yubordi, API `username` kutdi va HAR kirish
# "Ushbu maydon to'ldirilishi shart" bilan rad etildi — parol to'g'ri
# bo'lsa ham. Ikkala tomon alohida sinovdan o'tgani uchun bu
# nomuvofiqlik hech qayerda ko'rinmadi.
WEB_AUTH_FORM = REPO / "apps/web/src/components/AuthForm.tsx"
WEB_API = REPO / "apps/web/src/lib/api.ts"
API_SERIALIZERS = REPO / "apps/api/core/serializers.py"
# Smoke — HAQIQIY API'ni sinaydigan yagona joy, ya'ni shartnomadan birinchi
# bo'lib uziladi. Uning yuki ham shu yerda tekshiriladi (quyida).
SMOKE = REPO / "tests/smoke/check.py"

problems: list[str] = []


def json_blocks(text: str) -> list[dict]:
    return [
        json.loads(m)
        for m in re.findall(r"```json\n(.*?)\n```", text, re.S)
        if m.lstrip().startswith("{")
    ]


def go_json_tags(text: str) -> set[str]:
    return set(re.findall(r'json:"([^",]+)', text))


def _brace_block(text: str, name: str) -> str | None:
    """`name = { ... }` — qavslarni SANAB olingan tana (ichki lug'atlar uchun).

    Regex bu yerda yaroqsiz: `extra_kwargs` ichida `{"required": True}`
    kabi ichki lug'atlar bor, ya'ni non-greedy `.*?` birinchi `}` da
    to'xtab, tanani chala o'qiydi va tekshiruv jimgina bo'sh qoladi.
    """
    m = re.search(re.escape(name) + r"\s*=\s*\{", text)
    if not m:
        return None
    start = m.end()
    depth = 1
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i]
    return None


def check_login_contract() -> list[str]:
    """Kirish maydonlari: web yuboradigan ↔ API kutadigan.

    Maydon nomi ikki tomonda bir xil bo'lishi SHART. Farq bo'lsa API
    maydonni «to'ldirilmagan» deb hisoblaydi va foydalanuvchi to'g'ri
    parol bilan ham kira olmaydi — xato matni esa parolga ishora qiladi,
    ya'ni sababni yashiradi.
    """
    found: list[str] = []

    serializers = API_SERIALIZERS.read_text()
    match = re.search(r"class LoginSerializer\(.*?\n\n\n", serializers, re.S)
    if not match:
        return ["API: LoginSerializer topilmadi — shartnoma tekshirilmadi"]

    body = match.group(0)
    # `identifier = serializers.CharField()` ko'rinishidagi maydonlar.
    api_fields = set(re.findall(r"^\s+(\w+)\s*=\s*serializers\.", body, re.M))

    # Eski nom qolib ketmasin: u bo'lsa web bilan mos kelmaydi.
    if "username" in api_fields:
        found.append(
            "API: LoginSerializer hali `username` kutadi — web `identifier` yuboradi, "
            "har kirish «maydon to'ldirilmadi» bilan yiqiladi"
        )

    if "identifier" not in api_fields:
        found.append("API: LoginSerializer da `identifier` maydoni yo'q")

    # Web tomoni: AuthForm maydon nomi va login chaqiruvidagi kalit.
    # `postJson("/auth/login/", { identifier: ... })` — shu kalit API
    # kutadigan maydon nomi bilan AYNAN bir xil bo'lishi kerak.
    form = WEB_AUTH_FORM.read_text()
    if not re.search(r'name="identifier"', form):
        found.append('WEB: AuthForm da `name="identifier"` maydoni yo\'q')

    login_calls = re.findall(r'postJson\(\s*"/auth/login/",\s*\{(.*?)\}', form, re.S)
    if not login_calls:
        found.append("WEB: AuthForm da `/auth/login/` chaqiruvi topilmadi")
    else:
        for call in login_calls:
            # `identifier` maydoni birinchi kalit bo'lishi shart.
            if not re.search(r"identifier\s*:", call):
                found.append(
                    "WEB: `/auth/login/` chaqiruvida `identifier` yuborilmaydi "
                    "(API aynan shu maydonni kutadi)"
                )
            if re.search(r"username\s*:", call):
                found.append(
                    "WEB: `/auth/login/` chaqiruvida eski `username` kaliti qolgan — "
                    "API uni tanimaydi"
                )

    return found


WEB_AUTH_TABS = REPO / "apps/web/src/components/auth/AuthTabs.tsx"
WEB_TAB_MODEL = REPO / "apps/web/src/lib/auth-tabs.ts"


def check_register_contract() -> list[str]:
    """Ro'yxatdan o'tish: web yuboradigan maydonlar ↔ API talab qiladigan.

    3-qarordan keyin 1-qadamda FAQAT to'rt maydon yuboriladi:
    `email`, `password`, `terms_accepted` (+ ixtiyoriy `marketing_opt_in`).
    `username`, `display_name`, `country`, `region` 2-qadamga
    (`/onboarding`) ko'chirildi.

    ⚠️ Nega bu tekshiruv kerak bo'ldi (2026-09-13, o'lchandi): veb-forma
    `username` ni YUBORMASDI, API esa uni MAJBURIY deb bilardi —
    `extra_kwargs` da faqat `validators: []` yozilgan edi. Model
    maydonida `unique=True` bo'lgani uchun DRF `username` ni
    `required=True, allow_blank=False` qilib yasaydi, ya'ni har bir
    ro'yxatdan o'tish `400 {"username": ["Ushbu maydon to'ldirilishi
    shart."]}` bilan qaytardi. Sayt orqali HECH KIM ro'yxatdan
    o'ta olmasdi, lekin API'ni to'g'ridan-to'g'ri chaqirgan mijoz
    (sinov skripti `username` yuborgan) ishlayverardi — shuning uchun
    xato uzoq vaqt ko'rinmadi.

    Tekshiruv ikki tomonni qiyoslaydi: web 1-qadamda nima yuboradi va
    API shu maydonlarni ixtiyoriy deb biladimi.
    """
    found: list[str] = []

    form = WEB_AUTH_FORM.read_text()
    # 1-qadam yuki: `postJson("/auth/register/", { ... })` ichidagi kalitlar.
    calls = re.findall(r'postJson\(\s*"/auth/register/",\s*\{(.*?)\}\s*\)', form, re.S)
    if not calls:
        return ["WEB: AuthForm da `/auth/register/` chaqiruvi topilmadi"]
    web_fields = set(re.findall(r"^\s*(\w+)\s*:", calls[0], re.M))

    serializers = API_SERIALIZERS.read_text()
    match = re.search(r"class RegisterSerializer\(.*?\n\nclass ", serializers, re.S)
    if not match:
        return ["API: RegisterSerializer topilmadi — shartnoma tekshirilmadi"]
    body = match.group(0)

    # Model maydonlari `Meta.fields` dan keladi, ya'ni `username` kabi
    # maydonlar sinf tanasida E'LON QILINMAYDI — ular `extra_kwargs` da
    # sozlanadi. Shuning uchun tekshiruv `extra_kwargs` ni o'qiydi.
    #
    # `extra_kwargs` — ICHMA-ICH lug'at (`"email": {"required": ...}`),
    # ya'ni uni regex bilan o'qib bo'lmaydi: non-greedy `.*?` birinchi
    # ichki `}` da to'xtaydi. Qavslar sanog'i bilan olinadi.
    kw_body = _brace_block(body, "extra_kwargs")
    if kw_body is None:
        return ["API: RegisterSerializer da `extra_kwargs` topilmadi"]

    def flag(field: str, name: str) -> bool | None:
        """`extra_kwargs[field][name]` — `True`/`False`, yozilmagan bo'lsa `None`."""
        m = re.search(re.escape(f'"{field}"') + r"\s*:\s*\{(.*?)\}", kw_body, re.S)
        if not m:
            return None
        v = re.search(rf'"{name}"\s*:\s*(True|False)', m.group(1))
        return None if v is None else v.group(1) == "True"

    # 1-qadamda yuborilmaydigan har bir maydon ixtiyoriy bo'lishi shart.
    # Aks holda web formasi 400 oladi va ro'yxatdan o'tish ishlamaydi.
    # `None` = yozuv umuman yo'q, ya'ni DRF modeldan yasaydi —
    # `username` uchun bu `required=True, allow_blank=False` bo'ladi.
    deferred = {"username", "display_name", "country", "region"}
    for field in sorted(deferred - web_fields):
        if flag(field, "required") is not False:
            found.append(
                f"API: `{field}` 1-qadamda yuborilmaydi, lekin `extra_kwargs` da "
                f"`required: False` yo'q — ro'yxatdan o'tish 400 bilan yiqiladi"
            )
        if flag(field, "allow_blank") is not True:
            found.append(
                f"API: `{field}` 1-qadamda yuborilmaydi, lekin `allow_blank: True` yo'q — "
                f"DRF modeldan `allow_blank=False` yasaydi"
            )

    # Web yuboradigan har bir maydon API'da mavjud bo'lishi kerak
    # (`Meta.fields` yoki sinf tanasida e'lon qilingan).
    declared = set(re.findall(r"^\s+(\w+)\s*=\s*serializers\.", body, re.M))
    fields_match = re.search(r"fields\s*=\s*\[(.*?)\]", body, re.S)
    in_meta = set(re.findall(r'"(\w+)"', fields_match.group(1))) if fields_match else set()
    for field in sorted(web_fields):
        if field not in declared and field not in in_meta:
            found.append(f"API: web `{field}` yuboradi, lekin RegisterSerializer uni bilmaydi")

    return found


def check_tab_bar() -> list[str]:
    """Tablar qatorida ustun soni yozuvlar bilan mos kelishi.

    `AuthTabs` — `grid-cols-N` sinfini ishlatadi, ya'ni ustun soni
    QO'LDA yoziladi (Tailwind sinf nomini dinamik yasay olmaydi:
    `grid-cols-${n}` build vaqtida skanerlanmaydi). `TAB_BAR` ro'yxati
    esa shu fayldan alohida turadi. Ikkalasi ajralib ketsa tablar
    jimgina buziladi: ortiqcha `<li>` keyingi qatorga tushadi yoki
    ustunlar teng bo'lmagani uchun yozuv kesiladi.

    Nega bu MATNLAR bilan emas, SANOQ bilan tekshiriladi: nosozlik
    2026-09-13 da shundan chiqdi — uchta teng ustunga "Parolni tiklash"
    sig'may, 10 tildan 9 tasida o'rtasidan kesilgan edi (o'lchandi:
    360px da kk −115px, es −71px, uz −14px).
    """
    found: list[str] = []

    if not WEB_TAB_MODEL.exists():
        return [f"WEB: {WEB_TAB_MODEL.relative_to(REPO)} topilmadi"]
    if not WEB_AUTH_TABS.exists():
        return [f"WEB: {WEB_AUTH_TABS.relative_to(REPO)} topilmadi"]

    model = WEB_TAB_MODEL.read_text()
    bar = WEB_AUTH_TABS.read_text()

    bar_match = re.search(r"^export const TAB_BAR[^=]*=\s*\[(.*?)\]", model, re.M | re.S)
    if not bar_match:
        found.append("WEB: `TAB_BAR` ro'yxati `lib/auth-tabs.ts` da topilmadi")
    else:
        items = re.findall(r'"([^"]+)"', bar_match.group(1))
        if not items:
            found.append("WEB: `TAB_BAR` bo'sh — tablar qatori ko'rinmay qoladi")

        # Ustun soni `grid-cols-N` bilan bir xil bo'lishi shart.
        cols_match = re.search(r"grid-cols-(\d+)", bar)
        if not cols_match:
            found.append("WEB: `AuthTabs` da `grid-cols-N` sinfi topilmadi")
        elif int(cols_match.group(1)) != len(items):
            found.append(
                f"WEB: `TAB_BAR` {len(items)} ta bo'lim, lekin `AuthTabs` "
                f"`grid-cols-{cols_match.group(1)}` ishlatadi — ustunlar mos emas"
            )

        # Har bir bo'lim uchun yozuv `LABEL` xaritasida bo'lishi shart
        # (u yerda kalitlar `login: "auth.tabLogin"` shaklida yoziladi).
        # Yozuvsiz bo'lim `t(locale, undefined)` berib, `tsc` ni ham
        # yiqitardi — lekin bu faqat build vaqtida ko'rinadi.
        label_match = re.search(r"const LABEL[^=]*=\s*\{(.*?)\}", bar, re.S)
        label_body = label_match.group(1) if label_match else ""
        for tab in items:
            key = tab if re.match(r"^\w+$", tab) else f'"{tab}"'
            if not re.search(re.escape(key) + r"\s*:", label_body):
                found.append(f"WEB: `TAB_BAR` dagi `{tab}` uchun yozuv `AuthTabs` da yo'q")

    # `reset-password` — haqiqiy bo'lim, ya'ni `TABS` da qolishi SHART
    # (manzil, xatdagi token, `/reset-password` yo'naltirishi ishlashi
    # kerak). Uni butunlay o'chirish havolalarni sindirardi.
    tabs_match = re.search(r"export const TABS\s*=\s*\[(.*?)\]", model, re.S)
    if not tabs_match:
        found.append("WEB: `TABS` ro'yxati topilmadi")
    elif '"reset-password"' not in tabs_match.group(1):
        found.append(
            "WEB: `TABS` dan `reset-password` chiqarilgan — u haqiqiy bo'lim "
            "bo'lib qolishi shart (xatdagi token shu yerga keladi)"
        )

    return found


def _block_after(text: str, marker: str) -> str | None:
    """`marker` dan keyingi birinchi `{ ... }` — qavslar sanog'i bilan.

    `marker` ni `creds` kabi nom yoki `"/auth/login/"` kabi satr bo'lishi
    mumkin. Yuklar ichma-ich (`{"identifier": creds["username"]}`), ya'ni
    regex bilan o'qib bo'lmaydi.
    """
    m = re.search(re.escape(marker), text)
    if not m:
        return None
    start = text.find("{", m.end())
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i]
    return None


def check_smoke_payloads() -> list[str]:
    """Smoke testining yuklari API shartnomasiga mos kelishi.

    Smoke — HAQIQIY API'ni sinaydigan YAGONA joy: qolgan testlar API'ni
    mock qiladi. Shu sabab u shartnomadan birinchi bo'lib uziladi va
    uzilish faqat CI'da ko'rinadi.

    Aynan shu yuz berdi (2026-09-14, o'lchandi): maydon `username` dan
    `identifier` ga o'zgardi (4-qaror) va registrga majburiy
    `terms_accepted` qo'shildi. Web forma yangilandi, smoke esa
    yangilanmadi — u eski yukni yuborib `400` oldi, sayt esa
    ishlayverdi. Ya'ni tekshiruvning O'ZI jimgina o'lib qolgan edi.

    Shuning uchun yuk shakli shu yerda, serializer yonida tekshiriladi.
    `check_login_contract` va `check_register_contract` faqat web
    formani o'qiydi — smoke ularning ko'rigidan tashqarida qolgan edi.
    """
    found: list[str] = []
    if not SMOKE.exists():
        return [f"SMOKE: {SMOKE.relative_to(REPO)} topilmadi"]

    smoke = SMOKE.read_text()

    # ── Login: API `identifier` kutadi, `username` EMAS ──────────────
    login_body = _block_after(smoke, '"/auth/login/"')
    if login_body is None:
        found.append("SMOKE: `/auth/login/` chaqiruvi topilmadi")
    else:
        # Kalitlar qo'shtirnoq ichida (`"identifier":`), ya'ni qo'shtirnoq
        # ixtiyoriy bo'lishi shart — aks holda hech biri topilmaydi va
        # tekshiruv doim qizil bo'lardi.
        keys = set(re.findall(r'"?(\w+)"?\s*:', login_body))
        if "identifier" not in keys:
            found.append(
                "SMOKE: `/auth/login/` da `identifier` yuborilmaydi — "
                "API shu maydonni kutadi, login 400 bo'ladi"
            )
        if "username" in keys:
            found.append(
                "SMOKE: `/auth/login/` da eski `username` kaliti qolgan — "
                "API `identifier` kutadi"
            )

    # ── Register: majburiy maydonlarning HAMMASI yuborilishi shart ───
    serializers = API_SERIALIZERS.read_text()
    match = re.search(r"class RegisterSerializer\(.*?\n\nclass ", serializers, re.S)
    if not match:
        found.append("SMOKE: RegisterSerializer topilmadi — yuk tekshirilmadi")
        return found
    body = match.group(0)

    declared = set(re.findall(r"^\s+(\w+)\s*=\s*serializers\.", body, re.M))
    fields_match = re.search(r"fields\s*=\s*\[(.*?)\]", body, re.S)
    in_meta = set(re.findall(r'"(\w+)"', fields_match.group(1))) if fields_match else set()

    # Ixtiyoriylar ikki yo'l bilan belgilanadi: `extra_kwargs` ichida
    # (`{"required": False}`) yoki maydon e'lonida (`required=False`).
    kw_body = _brace_block(body, "extra_kwargs") or ""
    optional = set(re.findall(r'"(\w+)"\s*:\s*\{[^{}]*"required"\s*:\s*False', kw_body))
    optional |= set(
        re.findall(r"^\s+(\w+)\s*=\s*serializers\.\w+\([^)]*required\s*=\s*False", body, re.M)
    )
    required = (declared | in_meta) - optional

    creds_body = _brace_block(smoke, "creds")
    if creds_body is None:
        found.append("SMOKE: `creds` lug'ati topilmadi — register yuki tekshirilmadi")
        return found

    sent = set(re.findall(r'"(\w+)"\s*:', creds_body))
    for field in sorted(required - sent):
        found.append(
            f"SMOKE: register yukida majburiy `{field}` yo'q — "
            "ro'yxatdan o'tish 400 bilan yiqiladi"
        )
    for field in sorted(sent - declared - in_meta):
        found.append(f"SMOKE: register yuki `{field}` yuboradi, API uni bilmaydi")

    return found


def check_legacy_routes() -> list[str]:
    """`TABS` dagi har bo'lim uchun sahifa fayli bo'lishi shart.

    `TABS` — manzil shartnomasi: ro'yxatdagi har bir bo'lim HAQIQIY,
    chunki xatdagi `?token=` havolalari shu yerga keladi. 2026-09-13 da
    shu ro'yxatdagi bo'limning yo'naltirish fayli o'chib qolgan edi va
    hech bir tekshiruv buni ko'rmadi — sahifa 404 berib, parolni
    tiklash butunlay ishlamay qoldi.

    Ro'yxat qo'lda emas, `lib/auth-tabs.ts` dan o'qiladi: yangi bo'lim
    qo'shilsa tekshiruv o'zi kengayadi, bo'lim o'chirilsa — qizaradi.
    """
    found: list[str] = []
    model = REPO / "apps/web/src/lib/auth-tabs.ts"
    if not model.exists():
        return [f"WEB: {model.relative_to(REPO)} topilmadi"]

    match = re.search(r"export const TABS\s*=\s*\[(.*?)\]", model.read_text(), re.S)
    if not match:
        return ["WEB: `TABS` ro'yxati `lib/auth-tabs.ts` da topilmadi"]

    tabs = re.findall(r'"([^"]+)"', match.group(1))
    if not tabs:
        return ["WEB: `TABS` bo'sh — tekshiruv hech narsani qamramaydi"]

    app = REPO / "apps/web/src/app"
    for tab in tabs:
        page = app / tab / "page.tsx"
        if not page.exists():
            found.append(
                f"WEB: `TABS` dagi `{tab}` bo'limi uchun "
                f"{page.relative_to(REPO)} yo'q — havola 404 beradi"
            )
    return found


def main() -> int:
    protocol = PROTOCOL.read_text()
    blocks = json_blocks(protocol)
    if len(blocks) < 2:
        print(f"protocol.md da Job va Result bloklari topilmadi ({len(blocks)} ta)")
        return 1
    job_block, result_block = blocks[0], blocks[1]

    go_tags = go_json_tags(GO_PROTOCOL.read_text())
    py_source = PY_PROVIDER.read_text() + PY_SERVICES.read_text()

    for name, block in (("Job", job_block), ("Result", result_block)):
        for key in block:
            if key not in go_tags:
                problems.append(f"{name}.{key} — protocol.md da bor, judge-go da json tag yo'q")
            if f'"{key}"' not in py_source:
                problems.append(f"{name}.{key} — protocol.md da bor, API kodida ishlatilmagan")

    # Test maydonlari alohida: judge S3 havolasini ham, inline matnni ham
    # qabul qiladi, lekin API HAVOLA yuboradi.
    for key in ("input_ref", "output_ref"):
        if key not in go_tags:
            problems.append(f"tests[].{key} — API yuboradi, judge-go o'qimaydi")

    # Har bir qoida BIR o'tishda yig'iladi. Ilgari har tekshiruvdan keyin
    # erta `return` bor edi: yuqoridagi uzilish quyidagilarni to'sib,
    # bitta nosozlikni bir necha bosqichda ochardi (2026-09-14 saboqi).
    groups = [
        ("Shartnoma nomuvofiqligi", problems),
        ("Kirish shartnomasi nomuvofiqligi", check_login_contract()),
        ("Ro'yxatdan o'tish shartnomasi nomuvofiqligi", check_register_contract()),
        ("Tablar qatori nomuvofiqligi", check_tab_bar()),
        ("Smoke yuki nomuvofiqligi", check_smoke_payloads()),
        ("Eski manzillar nomuvofiqligi", check_legacy_routes()),
    ]
    failed = False
    for title, items in groups:
        if not items:
            continue
        failed = True
        print(f"{title}:", file=sys.stderr)
        for p in items:
            print(f"  - {p}", file=sys.stderr)
    if failed:
        return 1

    print(
        f"Shartnoma mos: Job {len(job_block)} maydon, Result {len(result_block)} maydon, "
        "kirish maydonlari, ro'yxat maydonlari, tablar qatori, smoke yuki, "
        "eski manzillar ✓"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
