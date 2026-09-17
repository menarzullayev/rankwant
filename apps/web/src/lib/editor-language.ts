/** Judge language code (`cpp23`, `py313`, `kotlin24`) → editor grammar and
 * starter code.
 *
 * Looked up by family — the code without its version digits — never by
 * prefix: among dozens of languages a prefix picks the wrong one (`c` would
 * take `cpp23` and `csharp14`, and `kt` never matched `kotlin24`). Every
 * language of the judge catalog (`apps/api/problems/languages.py`) has a row;
 * a unit test holds the two lists together.
 */

/** Monaco's id for "no grammar". */
const PLAIN_TEXT = "plaintext";

type Family = {
  /** Monaco language id; `plaintext` where Monaco has no grammar. */
  monaco: string;
  /** Code a new draft starts from; empty for scripts that need none. */
  starter: string;
};

export const LANGUAGE_FAMILIES: ReadonlyMap<string, Family> = new Map([
  [
    "c",
    {
      monaco: "c",
      starter: `#include <stdio.h>\n\nint main(void) {\n    \n    return 0;\n}\n`,
    },
  ],
  [
    "cpp",
    {
      monaco: "cpp",
      starter: `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    \n    return 0;\n}\n`,
    },
  ],
  [
    "csharp",
    {
      monaco: "csharp",
      starter: `using System;\n\nclass Program\n{\n    static void Main()\n    {\n        \n    }\n}\n`,
    },
  ],
  // Monaco has no grammar for D, Haskell or OCaml.
  [
    "d",
    {
      monaco: PLAIN_TEXT,
      starter: `import std.stdio;\n\nvoid main()\n{\n    \n}\n`,
    },
  ],
  ["dart", { monaco: "dart", starter: `void main() {\n  \n}\n` }],
  // No imports: Go refuses to compile an unused one.
  ["go", { monaco: "go", starter: `package main\n\nfunc main() {\n\t\n}\n` }],
  [
    "haskell",
    { monaco: PLAIN_TEXT, starter: `main :: IO ()\nmain = do\n  return ()\n` },
  ],
  // The judge runs `java -cp /box Main`, so the class must be `Main`.
  [
    "java",
    {
      monaco: "java",
      starter: `import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        \n    }\n}\n`,
    },
  ],
  ["js", { monaco: "javascript", starter: "" }],
  ["kotlin", { monaco: "kotlin", starter: `fun main() {\n    \n}\n` }],
  ["ocaml", { monaco: PLAIN_TEXT, starter: "" }],
  ["pascal", { monaco: "pascal", starter: `begin\n  \nend.\n` }],
  ["perl", { monaco: "perl", starter: "" }],
  // PHP prints everything outside `<?php` verbatim: a solution without the
  // tag outputs its own source and gets WA.
  ["php", { monaco: "php", starter: `<?php\n\n` }],
  ["py", { monaco: "python", starter: "" }],
  ["r", { monaco: "r", starter: "" }],
  ["ruby", { monaco: "ruby", starter: "" }],
  ["rust", { monaco: "rust", starter: `fn main() {\n    \n}\n` }],
  // The judge runs `java ... Main`, so the object must be `Main`.
  [
    "scala",
    {
      monaco: "scala",
      starter: `object Main {\n  def main(args: Array[String]): Unit = {\n    \n  }\n}\n`,
    },
  ],
  ["swift", { monaco: "swift", starter: "" }],
  ["ts", { monaco: "typescript", starter: "" }],
]);

export function languageFamily(code: string): string {
  return code.toLowerCase().replace(/\d+$/, "");
}

export function editorLanguage(code: string): string {
  return LANGUAGE_FAMILIES.get(languageFamily(code))?.monaco ?? PLAIN_TEXT;
}

export function starterSource(code: string): string {
  return LANGUAGE_FAMILIES.get(languageFamily(code))?.starter ?? "";
}
