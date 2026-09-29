""": Recharts prototip tekshiruvi — komponentlar, ma'lumot va Recharts API.

Nima uchun alohida test kerak: prototip o'z-o'zini o'z ichiga olgan HTML va
JSX brauzerda (Babel) kompilyatsiya qilinadi. Ya'ni `tsc` tekshirmaydi, build
yo'q, lint yo'q. Busiz HTML ichidagi xato faqat brauzerda ko'rinadi — bu test
o'sha bo'shliqni yopadi.

Nima tekshiriladi:
  1. Har bir ishlatilgan Recharts komponenti destructure ro'yxatida bor
     (yo'q bo'lsa `undefined` bo'lib, sahifa oq chiqadi — jim xato).
  2. Har bir diagramma uchun ma'lumot to'plami mavjud.
  3. UMD skriptlar TARTIBI: Recharts'ning bundle'i `react`, `react-dom`,
     `react-is` ni tashqaridan kutadi, ya'ni ular oldin turishi shart.
  4. O'rnatilgan Recharts versiyasi CDN havolasi bilan bir xil.

Ishga tushirish:
    C:/Users/nsn/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe \\
        prototypes/test_contest_analytics.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE / "recharts-contest-analytics.html"
REPO = HERE.parent

#: Sahifada chiziladigan har bir Recharts komponenti.
#: `ComposedChart` ham ro'yxatda — u Recharts 3 da mavjud, lekin kam
#: ishlatiladi va xato yozilsa jim `undefined` bo'lardi.
CHART_COMPONENTS = [
    "ResponsiveContainer", "ComposedChart", "LineChart", "Line", "BarChart",
    "Bar", "AreaChart", "Area", "PieChart", "Pie", "RadialBarChart",
    "RadialBar", "Cell", "XAxis", "YAxis", "CartesianGrid", "Tooltip",
    "Legend", "ReferenceLine",
]

#: Diagramma funksiyasi -> unga kerak bo'lgan ma'lumot to'plami.
DATASET_BY_CHART = {
    "RatingTrend": "CONTEST_RATING",
    "TitleBands": "TITLE_BANDS",
    "DifficultySplit": "DIFFICULTY_VS_ATTEMPTS",
    "TopicBars": "TOPIC_STRENGTH",
    "VerdictDonut": "VERDICTS",
    "QvantFlow": "QVANT_FLOW",
    "SolveRing": None,       # ma'lumot funksiya ichida
    "WeeklyActivity": "ACTIVITY",
}

#: UMD globalining nomi — bundle `e.Recharts` deb yozadi.
RECHARTS_GLOBAL = "Recharts"


def strip_jsx_comments(text: str) -> str:
    """`{/* ... */}` va `//` izohlarni olib tashlaydi.

    Izohlarda ham komponent nomi uchraydi (`Recharts'da bunday yo'q`),
    ya'ni tekshiruv ularni "ishlatilgan" deb sanab, xatoni yashirardi.
    """
    text = re.sub(r"\{/\*.*?\*/\}", "", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(?m)^\s*//.*$", "", text)
    text = re.sub(r"(?m)\s//\s.*$", "", text)
    return text


def main() -> int:
    problems: list[str] = []

    if not PAGE.exists():
        print(f"FAIL: sahifa yo'q — {PAGE}")
        return 1

    raw = PAGE.read_text(encoding="utf-8")
    code = strip_jsx_comments(raw)

    # ── 1. Skript tartibi ────────────────────────────────────────────
    order = re.findall(r'<script src="([^"]+)"', raw)
    expected_prefix = ["react@", "react-dom@", "react-is@", "recharts@", "@babel/standalone@"]
    for i, marker in enumerate(expected_prefix):
        if i >= len(order) or marker not in order[i]:
            problems.append(
                f"skript tartibi buzilgan: {i}. o'rinda `{marker}` kutilgan, "
                f"topilgani: {order[i] if i < len(order) else 'yo`q'}"
            )

    # ── 2. Destructure ro'yxati ──────────────────────────────────────
    #
    # ⚠️ Regex ATAYLAB qator boshidan (`^const`) boshlanadi va `.*?` faqat
    # shu ta'rifning ichida yuradi. Erkin `const\s*\{(.*?)\}\s*=\s*Recharts`
    # shakli birinchi `const { useState, useMemo } = React;` ta'rifini ham
    # yutib, oxirgi nomga yopishib qolgan edi — natijada
    # `ResponsiveContainer` "destructure qilinmagan" bo'lib ko'rindi,
    # aslida esa ro'yxatning boshida turgan edi (o'lchandi).
    m = re.search(
        rf"^const\s*\{{([^}}]*)\}}\s*=\s*{RECHARTS_GLOBAL}\s*;", code, flags=re.M
    )
    if not m:
        problems.append(f"`{RECHARTS_GLOBAL}` dan destructure topilmadi")
        destructured: set[str] = set()
    else:
        destructured = {
            n.strip() for n in m.group(1).replace("\n", " ").split(",") if n.strip()
        }

    # ── 3. Har bir ishlatilgan komponent destructure qilinganmi ──────
    for name in CHART_COMPONENTS:
        used = re.search(rf"<{name}[\s/>]", code)
        if used and name not in destructured:
            problems.append(f"`<{name}>` ishlatilgan, lekin destructure qilinmagan")
        if name in destructured and not used:
            problems.append(f"`{name}` destructure qilingan, lekin hech qayerda ishlatilmagan")

    # ── 4. Diagramma -> ma'lumot to'plami ────────────────────────────
    for fn, dataset in DATASET_BY_CHART.items():
        if not re.search(rf"function\s+{fn}\s*\(", code):
            problems.append(f"diagramma funksiyasi yo'q: {fn}")
            continue
        if dataset and not re.search(rf"^const\s+{dataset}\s*=", code, flags=re.M):
            problems.append(f"`{fn}` uchun ma'lumot to'plami yo'q: {dataset}")

    # ── 5. Ma'lumot to'plami haqiqatan massivmi ──────────────────────
    for name in ["CONTEST_RATING", "TITLE_BANDS", "DIFFICULTY_VS_ATTEMPTS",
                 "TOPIC_STRENGTH", "QVANT_FLOW", "VERDICTS", "ACTIVITY"]:
        mm = re.search(rf"^const\s+{name}\s*=\s*(.{{0,60}})", code, flags=re.M | re.S)
        if mm and not (mm.group(1).lstrip().startswith("[") or mm.group(1).lstrip().startswith("Array.from")):
            problems.append(f"`{name}` massiv emas: {mm.group(1).strip()[:40]}")

    rating_points = len(re.findall(r'\{\s*at:\s*"', code))
    if rating_points < 8:
        problems.append(f"reyting nuqtalari kam: {rating_points} (kamida 8 kerak)")

    # ── 6. CDN versiyasi o'rnatilgan paketga mos ─────────────────────
    pkg = REPO / "apps" / "web" / "node_modules" / "recharts" / "package.json"
    cdn = re.search(r"recharts@([\d.]+)/", raw)
    if pkg.exists():
        installed = json.loads(pkg.read_text(encoding="utf-8"))["version"]
        if cdn and cdn.group(1) != installed:
            problems.append(
                f"CDN versiyasi ({cdn.group(1)}) o'rnatilganidan ({installed}) farq qiladi"
            )
    else:
        print("OGOHLANTIRISH: apps/web/node_modules topilmadi — versiya solishtirilmadi")

    if problems:
        print("FAIL:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(
        f"OK: {len(destructured)} Recharts komponenti destructure qilingan, "
        f"{len(DATASET_BY_CHART)} diagramma, reyting nuqtalari {rating_points}, "
        f"CDN {cdn.group(1) if cdn else '?'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
