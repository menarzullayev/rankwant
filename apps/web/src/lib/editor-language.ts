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
  // gnatmake names the unit after the file: main.adb must hold procedure Main.
  [
    "ada",
    {
      monaco: PLAIN_TEXT,
      starter: `with Ada.Text_IO; use Ada.Text_IO;\n\nprocedure Main is\nbegin\n   null;\nend Main;\n`,
    },
  ],
  [
    "c",
    {
      monaco: "c",
      starter: `#include <stdio.h>\n\nint main(void) {\n    \n    return 0;\n}\n`,
    },
  ],
  ["caml", { monaco: PLAIN_TEXT, starter: "" }],
  // Fixed format: code starts in column 8.
  [
    "cobol",
    {
      monaco: PLAIN_TEXT,
      starter: `       IDENTIFICATION DIVISION.\n       PROGRAM-ID. MAIN.\n       PROCEDURE DIVISION.\n           STOP RUN.\n`,
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
  [
    "d",
    {
      monaco: PLAIN_TEXT,
      starter: `import std.stdio;\n\nvoid main()\n{\n    \n}\n`,
    },
  ],
  ["dart", { monaco: "dart", starter: `void main() {\n  \n}\n` }],
  [
    "fortran",
    {
      monaco: PLAIN_TEXT,
      starter: `program main\n  implicit none\n  \nend program main\n`,
    },
  ],
  ["fsharp", { monaco: "fsharp", starter: "" }],
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
  ["julia", { monaco: "julia", starter: "" }],
  ["kotlin", { monaco: "kotlin", starter: `fun main() {\n    \n}\n` }],
  ["lisp", { monaco: PLAIN_TEXT, starter: "" }],
  ["lua", { monaco: "lua", starter: "" }],
  // No libc: the program starts at _start and leaves through the exit syscall.
  [
    "nasm",
    {
      monaco: PLAIN_TEXT,
      starter: `section .text\n    global _start\n\n_start:\n    mov eax, 60\n    xor edi, edi\n    syscall\n`,
    },
  ],
  // GCC's Objective-C runtime has no @autoreleasepool.
  [
    "objc",
    {
      monaco: "objective-c",
      starter: `#import <Foundation/Foundation.h>\n\nint main(void) {\n    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];\n    \n    [pool drain];\n    return 0;\n}\n`,
    },
  ],
  ["ocaml", { monaco: PLAIN_TEXT, starter: "" }],
  ["pascal", { monaco: "pascal", starter: `begin\n  \nend.\n` }],
  ["perl", { monaco: "perl", starter: "" }],
  // PHP prints everything outside `<?php` verbatim: a solution without the
  // tag outputs its own source and gets WA.
  ["php", { monaco: "php", starter: `<?php\n\n` }],
  ["powershell", { monaco: "powershell", starter: "" }],
  // Without the directive swipl opens its toplevel and reads the input as queries.
  [
    "prolog",
    {
      monaco: PLAIN_TEXT,
      starter: `:- initialization(main, main).\n\nmain :-\n    true.\n`,
    },
  ],
  ["py", { monaco: "python", starter: "" }],
  ["pypy", { monaco: "python", starter: "" }],
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
  [
    "vbnet",
    {
      monaco: "vb",
      starter: `Module Program\n    Sub Main()\n        \n    End Sub\nEnd Module\n`,
    },
  ],
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
