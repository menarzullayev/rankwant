#!/usr/bin/env python3
"""Render `/about` language sample maps from A+B solution modules.

The samples are source code in thirty-five languages, written into TypeScript
template literals. A template literal is not a raw string: `\\s` reads as `s`,
`\\n` as a line break, `${...}` as an interpolation and a backtick ends it.
Until 2026-11-14 the body was written as it was, so the page showed
`split(/s+/)` for JavaScript and a broken string for PHP, Dart and Prolog —
code that does not solve the problem it is shown for. `template_literal`
escapes exactly those three things, and `tools/check_language_samples.py`
holds the generated file to these sources.
"""

from __future__ import annotations

import json
from pathlib import Path

from aplus_file_solutions import APLUS_FILE
from aplus_solutions import APLUS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "apps/web/src/content/about/language-samples.ts"


def template_literal(text: str) -> str:
    """`text` as the body of a template literal that evaluates back to `text`.

    The backslash goes first: the other two replacements add backslashes of
    their own, which must not be doubled.
    """
    return text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def entries(samples: dict[str, str]) -> str:
    return ",\n".join(
        f"  {json.dumps(code)}: `{template_literal(body)}`"
        for code, body in sorted(samples.items())
    )


def render() -> str:
    """The whole file, with `\\n` line ends whatever the platform."""
    stdio_entries = entries(APLUS)
    file_entries = entries(APLUS_FILE)
    return f"""/** A+B namunalari — `/about` yo'riqnomasi.
 *
 * Manba: `tools/aplus_solutions.py`, `tools/aplus_file_solutions.py`.
 * Yangilash: `python tools/render_language_samples.py`
 */
export const LANGUAGE_SAMPLES: Record<string, string> = {{
{stdio_entries}
}};

export const LANGUAGE_FILE_SAMPLES: Record<string, string> = {{
{file_entries}
}};

/** Monaco til identifikatori — faqat ko'rinish uchun. */
export function sampleEditorLanguage(code: string): string {{
  if (code.startsWith("cpp") || code === "c17") return "cpp";
  if (code.startsWith("py") || code === "pypy73") return "python";
  if (code.startsWith("java") || code.startsWith("kotlin") || code.startsWith("scala"))
    return "java";
  if (code === "js24" || code === "ts24") return "javascript";
  if (code === "csharp14" || code === "fsharp10" || code === "vbnet17") return "csharp";
  if (code === "go127") return "go";
  if (code.startsWith("rust")) return "rust";
  if (code === "php84") return "php";
  if (code === "ruby33") return "ruby";
  if (code === "pascal322") return "pascal";
  if (code === "swift60") return "swift";
  if (code === "dart313") return "dart";
  return "plaintext";
}}

export function sampleForLanguage(code: string): string | null {{
  return LANGUAGE_SAMPLES[code] ?? null;
}}

export function sampleFileForLanguage(code: string): string | null {{
  return LANGUAGE_FILE_SAMPLES[code] ?? null;
}}
"""


def main() -> None:
    # `newline="\n"`: on Windows the default turns every line end into CRLF,
    # and the file would differ from the committed one on every line.
    OUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(APLUS)} stdio + {len(APLUS_FILE)} file)")


if __name__ == "__main__":
    main()
