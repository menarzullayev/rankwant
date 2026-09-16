"""Export a bilingual review sheet for a language whose translations are unverified.

WHY THIS EXISTS
---------------
Ten languages ship, but only some of them were translated by a speaker of
that language. Karakalpak, Kyrgyz and Tajik dictionaries were written by the
model, and the honest status of those values is "plausible, unverified" —
not "done". A wrong word in a table header is invisible in CI and obvious to
the person who reads it.

So the values are not silently trusted. This tool produces a sheet a native
speaker can work through: the key, the Uzbek source, and the current value,
one row per string, with a column to mark the verdict.

It is a tool rather than a one-off file because the dictionaries change: the
sheet has to be regenerable, and a stale sheet is worse than none.

Usage
-----
    python tools/export_i18n_review.py                  # admin.* keys, 4 languages
    python tools/export_i18n_review.py --prefix ""      # every key
    python tools/export_i18n_review.py --prefix customizer.

Output goes to `docs/08-technical-spec/i18n-review/<lang>.md`.
"""

from __future__ import annotations

import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCALES = ROOT / "apps/web/src/i18n/locales"
OUT = ROOT / "docs/08-technical-spec/i18n-review"

#: Languages whose values were written by the model and need a speaker's eye.
#: `en`/`ru`/`tr`/`zh`/`es` are not here: their vocabulary is well covered,
#: and a wrong word there would be caught in review of the English anyway.
NEEDS_REVIEW = {
    "kaa": "Karakalpak",
    "ky": "Kyrgyz",
    "tg": "Tajik",
    "kk": "Kazakh",
}

PAIR = re.compile(r'^\s*(?:"([^"]+)"|([A-Za-z_$][\w$]*)):\s*"((?:[^"\\]|\\.)*)",\s*$', re.M)


def load(code: str) -> dict[str, str]:
    text = (LOCALES / f"{code}.ts").read_text(encoding="utf-8")
    return {a or b: c for a, b, c in PAIR.findall(text)}


def escape(value: str) -> str:
    """Make a value safe inside a Markdown table cell."""
    return value.replace("|", "\\|")


def _regen_line(prefix: str) -> str:
    """Varaq ichidagi "qayta yaratish" buyrug'i — ko'chirib bo'ladigan bo'lsin.

    Bo'sh prefiksda `--prefix ` osilib qoladi va buyruq ishlamaydi. Bo'sh
    prefiks "hamma kalit" degani, shuning uchun u qo'shtirnoq bilan aniq
    yoziladi. Tire bilan boshlanadigan prefiks ham qo'shtirnoq talab qiladi
    (aks holda argparse uni bayroq deb o'qiydi).
    """
    if prefix == "":
        return (
            'Regenerate with `python tools/export_i18n_review.py --prefix ""` '
            "(every key)."
        )
    return (
        f'Regenerate with `python tools/export_i18n_review.py '
        f'--prefix "{prefix}"`.'
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="admin.", help="only keys starting with this")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args()

    source = load("uz")
    keys = [k for k in source if k.startswith(args.prefix)]
    if not keys:
        print(f"XATO: `{args.prefix}` bilan boshlanadigan kalit yo'q")
        return 1

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for code, name in NEEDS_REVIEW.items():
        values = load(code)
        rows = [
            f"| `{k}` | {escape(source[k])} | {escape(values.get(k, '—'))} |  |"
            for k in keys
        ]
        body = "\n".join([
            f"# {name} ({code}) — translation review",
            "",
            "**Status:** unverified. These values were produced by a language",
            "model, not by a speaker of the language. They are plausible, and",
            "some are certainly wrong.",
            "",
            "## How to review",
            "",
            "Read the third column against the second. If the meaning is right,",
            "tick the last column. If it is wrong, write the correct wording in",
            "it and it will be copied into the dictionary.",
            "",
            "- Column 2 is the **Uzbek source**, the text the app was written in.",
            "- Column 3 is what a user of this language currently sees.",
            "- Proper nouns and loanwords are expected to match the source; that",
            "  is deliberate and `tools/check_i18n.py` exempts them explicitly.",
            "",
            # ⚠️ Bo'sh prefiks `--prefix ` bo'lib chiqadi va buyruq ishlamaydi.
            # Bo'sh prefiks "hamma kalit" degani — uni aynan shunday yozish
            # kerak, aks holda varaqni ko'chirib olgan odam buzuq buyruq
            # oladi (o'lchandi: varaqlardagi qator shunday qolib ketgan).
            _regen_line(args.prefix),
            "",
            f"**{len(rows)} strings.**",
            "",
            "| Key | Uzbek (source) | " + name + " | Review |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
        ])
        path = out_dir / f"{code}.md"
        # `newline="\n"` SHART: Windows'da `write_text` standart holatda
        # `\n` ni `\r\n` ga o'giradi va varaq butunlay CRLF bo'lib qoladi.
        # Repo LF'da, ya'ni bu jimgina nuqson emas — `check_negative` dagi
        # langarlar faylni `read_bytes()` bilan o'qiydi va CRLF ularni
        # topilmas qiladi (o'lchandi: 1/64 salbiy test yiqildi).
        path.write_text(body, encoding="utf-8", newline="\n")
        # `--out` repo TASHQARISIDA bo'lishi mumkin (masalan `.tmp/` yoki
        # boshqa papka) — u holda `relative_to(ROOT)` ValueError beradi va
        # buyruq yozishni tugatib bo'lgach yiqiladi. Ko'rsatish uchun
        # nisbiy yo'l bo'lmasa, to'liq yo'lni chiqaramiz.
        try:
            shown = path.relative_to(ROOT)
        except ValueError:
            shown = path
        print(f"  {shown}  ({len(rows)} satr)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
