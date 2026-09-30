#!/usr/bin/env python3
"""Render `/about` language sample maps from A+B solution modules."""

from __future__ import annotations

import json
from pathlib import Path

from aplus_file_solutions import APLUS_FILE
from aplus_solutions import APLUS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "apps/web/src/content/about/language-samples.ts"


def main() -> None:
    stdio_entries = ",\n".join(
        f"  {json.dumps(code)}: `{body}`" for code, body in sorted(APLUS.items())
    )
    file_entries = ",\n".join(
        f"  {json.dumps(code)}: `{body}`" for code, body in sorted(APLUS_FILE.items())
    )
    content = f"""/** A+B namunalari — `/about` yo'riqnomasi.
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
  if (code === "go124") return "go";
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
    OUT.write_text(content, encoding="utf-8")
    print(f"wrote {OUT} ({len(APLUS)} stdio + {len(APLUS_FILE)} file)")


if __name__ == "__main__":
    main()
