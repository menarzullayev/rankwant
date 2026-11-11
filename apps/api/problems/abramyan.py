# ruff: noqa: E501 — the statements' sentences are data, kept whole to compare by eye.
"""The Abramyan "Programming Taskbook" package, turned into our fields (ADR-0060 § 2.5).

The package (`manifest.json`, `tests/`, `solutions/`) is the owner's own
export of the 1 100 problems he entered into Robocontest; the author's
permission exists. Everything here is a pure function of the package, so the
import command stays a thin writer and these rules are tested on their own.
"""

from __future__ import annotations

import html
import math
import re
from dataclasses import dataclass
from typing import Any

from problems.html_to_markdown import html_to_markdown

#: The package's language codes → ours. Karakalpak is `kaa` here.
LOCALES = {"uz": "uz", "ru": "ru", "en": "en", "qq": "kaa"}
#: The author's language of every problem; the others are translations.
BASE = "uz"

SOURCE = "M. E. Abramyan, Programming Taskbook"
TIME_LIMIT_MS = 1000
#: Owner decision: 64 MB; each language's runtime is added on top (ADR-0060 § 2.2).
MEMORY_LIMIT_KB = 64 * 1024
#: The package's real-number checker: |x − y| ≤ 1e-6 · max(1, |x|).
REAL_TOLERANCE = 1e-6

#: Owner-approved section → topic slugs (decision 2026-11-11, round 4).
TOPICS: dict[str, tuple[str, ...]] = {
    "Begin": ("oddiy", "math"),
    "Integer": ("math", "sonlar-nazariyasi"),
    "Boolean": ("oddiy",),
    "If": ("implementation",),
    "Case": ("implementation",),
    "For": ("sikllar",),
    "While": ("sikllar",),
    "Proc": ("funksiyalar",),
    "Series": ("sikllar",),
    "Minmax": ("sikllar",),
    "Array": ("massiv",),
    "Matrix": ("matritsa",),
    "String": ("satrlar",),
    "Recur": ("rekursiya",),
    "Param": ("funksiyalar", "massiv"),
    "Text": ("fayllar", "satrlar"),
    "File": ("fayllar",),
    "Dynamic": ("malumotlar-tuzilmasi",),
    "Tree": ("malumotlar-tuzilmasi", "rekursiya"),
}

#: The agent's difficulty estimate (owner decision ③): a base per section and
#: a span spent by the problem's place in the section and its solution's size.
DIFFICULTY: dict[str, tuple[int, int]] = {
    "Begin": (800, 200),
    "Integer": (800, 200),
    "Boolean": (800, 200),
    "If": (800, 300),
    "Case": (800, 200),
    "For": (800, 300),
    "While": (900, 300),
    "Proc": (900, 300),
    "Series": (900, 300),
    "Minmax": (900, 300),
    "Array": (1000, 500),
    "Matrix": (1100, 500),
    "String": (1000, 400),
    "Recur": (1200, 500),
    "Param": (1100, 400),
    "Text": (1100, 400),
    "File": (1100, 400),
    "Dynamic": (1200, 500),
    "Tree": (1300, 600),
}

_MATH = re.compile(r'<span class="math-tex">\s*\\\((.*?)\\\)\s*</span>', re.S)
_PLACEHOLDER = "@@ABRAMYANMATH{}@@"


def code_title(title: str) -> str:
    """`Begin1 [Kvadrat perimetri]` → `Begin1. Kvadrat perimetri` (owner decision ⑧)."""
    match = re.fullmatch(r"\s*(\S+)\s*\[(.*)\]\s*", title)
    if match is None:
        return title.strip()
    return f"{match.group(1)}. {match.group(2).strip()}"


def to_markdown(source: str | None) -> str:
    """The package's HTML → our Markdown, its `\\( … \\)` spans as `$ … $`.

    The converter escapes backslashes and brackets, which would break the
    LaTeX, so each formula is lifted out before it runs and put back after.
    """
    if not source:
        return ""
    formulas: list[str] = []

    def lift(match: re.Match[str]) -> str:
        formulas.append(html.unescape(match.group(1)).strip())
        return _PLACEHOLDER.format(len(formulas) - 1)

    text = html_to_markdown(_MATH.sub(lift, source))
    for index, formula in enumerate(formulas):
        text = text.replace(_PLACEHOLDER.format(index), f"${formula}$")
    return text.strip()


# ── File and Text: the book's file I/O (owner decision ⑦) ─────────────

#: The Robocontest adaptation sentence → the file I/O sentence, per language.
#: Five forms cover 143 of the 150 problems (measured on the package); the
#: other seven say nothing about files and get `FILE_NOTE` appended.
FILE_SENTENCES: dict[str, list[tuple[str, str]]] = {
    "uz": [
        (
            "Fayl o'rniga uning komponentlari kirishda beriladi, natijaviy fayl komponentlari esa ekranga chiqariladi.",
            "Fayl komponentlari input.txt faylida beriladi, natijaviy fayl komponentlarini output.txt fayliga yozing.",
        ),
        (
            "Matn fayl o'rniga uning qatorlari kirishda beriladi, natijaviy fayl qatorlari esa ekranga chiqariladi.",
            "Matn fayl qatorlari input.txt faylida beriladi, natijaviy fayl qatorlarini output.txt fayliga yozing.",
        ),
        (
            "Matn fayl o'rniga uning qatorlari kirishda beriladi, natijaviy fayl qatorlari ekranga chiqariladi.",
            "Matn fayl qatorlari input.txt faylida beriladi, natijaviy fayl qatorlarini output.txt fayliga yozing.",
        ),
        (
            "Binar fayllar o'rniga ma'lumotlar kirishda beriladi, natijaviy fayl qatorlari ekranga chiqariladi.",
            "Binar fayllar ma'lumotlari input.txt faylida beriladi, natijaviy fayl qatorlarini output.txt fayliga yozing.",
        ),
        ("Fayl o'rniga qatorlarni ekranga chiqaring.", "Qatorlarni output.txt fayliga yozing."),
    ],
    "ru": [
        (
            "Вместо файла его компоненты задаются во входных данных, а компоненты результирующего файла выводятся на экран.",
            "Компоненты файла заданы в файле input.txt; компоненты результирующего файла запишите в файл output.txt.",
        ),
        (
            "Вместо текстового файла его строки задаются во входных данных, а строки результирующего файла выводятся на экран.",
            "Строки текстового файла заданы в файле input.txt; строки результирующего файла запишите в файл output.txt.",
        ),
        (
            "Вместо текстового файла его строки задаются во входных данных, строки результирующего файла выводятся на экран.",
            "Строки текстового файла заданы в файле input.txt; строки результирующего файла запишите в файл output.txt.",
        ),
        (
            "Вместо бинарных файлов данные задаются во входных данных, строки результирующего файла выводятся на экран.",
            "Данные бинарных файлов заданы в файле input.txt; строки результирующего файла запишите в файл output.txt.",
        ),
        ("Вместо файла выведите строки на экран.", "Запишите строки в файл output.txt."),
    ],
    "en": [
        (
            "Instead of a file its components are given in the input, and the components of the resulting file are printed.",
            "The file's components are given in input.txt; write the components of the resulting file to output.txt.",
        ),
        (
            "Instead of a text file its lines are given in the input, and the lines of the resulting file are printed.",
            "The text file's lines are given in input.txt; write the lines of the resulting file to output.txt.",
        ),
        (
            "Instead of the text file its lines are given in the input, the lines of the resulting file are printed.",
            "The text file's lines are given in input.txt; write the lines of the resulting file to output.txt.",
        ),
        (
            "Instead of binary files the data is given in the input, the lines of the resulting file are printed.",
            "The data of the binary files is given in input.txt; write the lines of the resulting file to output.txt.",
        ),
        ("Instead of the file print the lines.", "Write the lines to output.txt."),
    ],
    "qq": [
        (
            "Fayl ornına onıń komponentleri kirisiwde beriledi, nátiyjelik fayl komponentleri bolsa ekranǵa shıǵarıladı.",
            "Fayl komponentleri input.txt faylında beriledi, nátiyjelik fayl komponentlerin output.txt faylına jazıń.",
        ),
        (
            "Tekst fayl ornına onıń qatarları kirisiwde beriledi, nátiyjelik fayl qatarları bolsa ekranǵa shıǵarıladı.",
            "Tekst fayl qatarları input.txt faylında beriledi, nátiyjelik fayl qatarların output.txt faylına jazıń.",
        ),
        (
            "Tekst fayl ornına onıń qatarları kirisiwde beriledi, nátiyjelik fayl qatarları ekranǵa shıǵarıladı.",
            "Tekst fayl qatarları input.txt faylında beriledi, nátiyjelik fayl qatarların output.txt faylına jazıń.",
        ),
        (
            "Ekilik fayllar ornına maǵlıwmatlar kirisiwde beriledi, nátiyjelik fayl qatarları ekranǵa shıǵarıladı.",
            "Ekilik fayllar maǵlıwmatları input.txt faylında beriledi, nátiyjelik fayl qatarların output.txt faylına jazıń.",
        ),
        ("Fayl ornına qatarlardı ekranǵa shıǵarıń.", "Qatarlardı output.txt faylına jazıń."),
    ],
}

#: For the seven Text problems the adaptation rewrote without a file sentence.
FILE_NOTE: dict[str, str] = {
    "uz": "Kiruvchi ma'lumotlar input.txt faylida beriladi, natijani output.txt fayliga yozing.",
    "ru": "Входные данные заданы в файле input.txt; результат запишите в файл output.txt.",
    "en": "The input is given in input.txt; write the result to output.txt.",
    "qq": "Kiriwshi maǵlıwmatlar input.txt faylında beriledi, nátiyjeni output.txt faylına jazıń.",
}


def to_file_io(legend: str, lang: str) -> str:
    """The statement's adaptation sentence back to the book's file I/O."""
    for old, new in FILE_SENTENCES[lang]:
        if old in legend:
            return legend.replace(old, new)
    return f"{legend.rstrip()}\n\n{FILE_NOTE[lang]}"


#: Prepended to a reference solution of a file problem: the same program,
#: reading input.txt and writing output.txt, as the book asks.
FILE_PREAMBLE = (
    "import sys\n"
    "sys.stdin = open('input.txt', encoding='utf-8')\n"
    "sys.stdout = open('output.txt', 'w', encoding='utf-8')\n"
)


def file_solution(source: str) -> str:
    """A stdin/stdout reference solution turned into a file one.

    `from __future__` must stay the first statement, so the preamble goes
    after it when the solution has one.
    """
    lines = source.splitlines(keepends=True)
    head = [line for line in lines if line.startswith("from __future__")]
    rest = [line for line in lines if not line.startswith("from __future__")]
    return "".join(head) + FILE_PREAMBLE + "".join(rest)


# ── Difficulty (owner decision ③: the agent's estimate) ────────────────


def solution_size(source: str) -> int:
    """Lines of code plus three per level of the deepest nesting."""
    code = [
        line for line in source.splitlines() if line.strip() and not line.strip().startswith("#")
    ]
    depth = max((len(line) - len(line.lstrip(" "))) // 4 for line in code) if code else 0
    return len(code) + 3 * depth


@dataclass(frozen=True)
class Estimate:
    code: str
    section: str
    position: float
    size_rank: float
    difficulty: int


def estimate(tasks: list[dict[str, Any]], sizes: dict[str, int]) -> dict[str, Estimate]:
    """Each problem's difficulty: its section's base, plus the span times the mean
    of its place in the section and its solution's size rank there, on the
    800–3500 scale in steps of 100."""
    out: dict[str, Estimate] = {}
    by_section: dict[str, list[dict[str, Any]]] = {}
    for task in tasks:
        by_section.setdefault(task["section"], []).append(task)
    for section, rows in by_section.items():
        rows = sorted(rows, key=lambda row: row["order"])
        base, span = DIFFICULTY[section]
        ordered_sizes = sorted(sizes.get(row["code"], 0) for row in rows)
        last = max(len(rows) - 1, 1)
        for index, row in enumerate(rows):
            size = sizes.get(row["code"], 0)
            rank = ordered_sizes.index(size) / last
            position = index / last
            score = (position + rank) / 2
            value = base + math.floor(score * span / 100 + 0.5) * 100
            out[row["code"]] = Estimate(
                row["code"], section, round(position, 3), round(rank, 3), min(value, 3500)
            )
    return out


def slug(code: str) -> str:
    """The book code is the problem's address (owner decision ⑨): `begin1`."""
    return code.lower()


def plan_text(value: str) -> str:
    """A study-plan text without the Robocontest practice-contest number
    (`40 ta masala. Mashg'ulot contesti: #4126` → `40 ta masala.`)."""
    return re.sub(r"\s*[^.]*#\d+\.?", "", value or "").strip()


#: The plan's description. The package's says each section is one practice
#: contest, which is true on Robocontest and not here.
PLAN_DESCRIPTION: dict[str, str] = {
    "uz": (
        "M. E. Abramyan «Programming Taskbook» kitobidagi 1100 ta masala: o'zgaruvchilardan "
        "massivlar, satrlar, rekursiya, ko'rsatkichlar va daraxtlargacha. Bo'limlar va "
        "masalalar kitob tartibida."
    ),
    "ru": (
        "1100 задач из книги М. Э. Абрамяна «Programming Taskbook»: от переменных до массивов, "
        "строк, рекурсии, указателей и деревьев. Разделы и задачи идут в порядке книги."
    ),
    "en": (
        "1100 problems from M. E. Abramyan's Programming Taskbook: from variables to arrays, "
        "strings, recursion, pointers and trees. Sections and problems follow the book."
    ),
    "qq": (
        "M. E. Abramyan'nıń «Programming Taskbook» kitabındaǵı 1100 másele: ózgeriwshilerden "
        "massivler, qatarlar, rekursiya, kórsetkishler hám aǵashlarǵa shekem. Bólimler hám "
        "máseleler kitap tártibinde."
    ),
}
