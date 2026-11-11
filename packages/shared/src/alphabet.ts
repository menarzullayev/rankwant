/**
 * The Uzbek Latin alphabet, old and new (ADR-0059).
 *
 * Law O'RQ-1184 of 21.10.2026 (in force from 22.04.2027) rewrites the
 * alphabet: `oʻ → ö`, `gʻ → ğ`, `sh → ş`, `ch → ç`, and the tutuq belgisi
 * is `ʼ`. Text written in the old form stays valid, so the platform holds
 * both: this module converts between them, and `apps/api/core/alphabet.py`
 * is its twin (one set of cases, `alphabet-cases.json`, checks both).
 *
 * What is never converted: code (fenced and inline), LaTeX, URLs, e-mail
 * addresses, file names, placeholders (`{count}`), HTML tags, link targets,
 * and words that are not Uzbek — a brand written in camel case (`GitHub`),
 * a short acronym (`SSH`), a word with letters Uzbek does not use (`w`, a
 * `c` outside `ch`, `oo`, `th`), or one from `FOREIGN_WORDS` (`Shift`).
 * The conversion is a starting point: staff correct what it misses.
 */

/** Characters the old alphabet writes its apostrophe with. */
export const OLD_APOSTROPHES = "'’ʻ‘`´";
/** The tutuq belgisi of the new alphabet (U+02BC). */
export const TUTUQ = "ʼ";
/** The `ʻ` of `oʻ` and `gʻ` when the old alphabet is written back (U+02BB). */
const TURNED_COMMA = "ʻ";

/** The new letters folded onto the old spelling for search, so «Özbekiston»,
 *  «O'zbekiston» and «Ozbekiston» are one query. `core.search.ALPHABET_FOLD`
 *  is the server's copy. */
export const ALPHABET_FOLD: Readonly<Record<string, string>> = {
  ö: "o",
  Ö: "o",
  ğ: "g",
  Ğ: "g",
  ş: "sh",
  Ş: "sh",
  ç: "ch",
  Ç: "ch",
};

/** Words that look Uzbek to the letter rules but are not. Lower case. */
export const FOREIGN_WORDS: ReadonlySet<string> = new Set([
  "bash",
  "branch",
  "chart",
  "chrome",
  "crash",
  "dashboard",
  "english",
  "finish",
  "flash",
  "flush",
  "fresh",
  "hash",
  "publish",
  "push",
  "refresh",
  "sha",
  "shell",
  "shift",
  "shortcut",
  "ssh",
]);

/** Stems of foreign words that take Uzbek suffixes (`Changelogda`). Long
 *  enough not to start an Uzbek word. Lower case. */
export const FOREIGN_STEMS: readonly string[] = ["challenge", "changelog", "dashboard", "shimmer"];

const LETTER = "A-Za-z\\u00C0-\\u024F";
const APOS = "'’ʻ‘`´ʼ";

/** Spans that keep their text, in the order they are tried. */
const PROTECTED = new RegExp(
  [
    "```[\\s\\S]*?```",
    "~~~[\\s\\S]*?~~~",
    "(?<![A-Za-z])`[^`\\n]+`",
    "\\$\\$[\\s\\S]*?\\$\\$",
    "\\$[^$\\n]+\\$",
    "\\\\\\([\\s\\S]*?\\\\\\)",
    "\\\\\\[[\\s\\S]*?\\\\\\]",
    "(?:https?://|www\\.)[^\\s<>()]+",
    "[\\w.+-]+@[\\w-]+(?:\\.[\\w-]+)+",
    "\\]\\([^)\\n]*\\)",
    "<[^<>\\n]+>",
    "\\{[A-Za-z_][\\w.]*\\}",
    // A heading anchor (`## Qidiruv {#binary-search}`): links point at the
    // id as written, so converting it would break them (ADR-0062).
    "\\{#[\\w-]+\\}",
    // A file name's extension is lower case: `Main.java`, not the
    // `yechildi.Shu` of a missing space.
    "\\b[\\w-]+\\.[a-z][a-z0-9]{0,4}\\b",
  ].join("|"),
  "g",
);

const WORD = new RegExp(`[${LETTER}]+(?:[${APOS}][${LETTER}]+)*[${APOS}]?`, "g");

const isApostrophe = (char: string | undefined) =>
  char !== undefined && OLD_APOSTROPHES.includes(char);

/** Whether a word is left as it is written (see the module comment). */
export function isForeignWord(word: string): boolean {
  const bare = word.replace(new RegExp(`[${APOS}]`, "g"), "");
  const lower = bare.toLowerCase();
  if (FOREIGN_WORDS.has(lower)) return true;
  if (FOREIGN_STEMS.some((stem) => lower.startsWith(stem))) return true;
  // A lower-to-upper step inside a word: GitHub, TypeScript, ChatGPT.
  if (/\p{Ll}\p{Lu}/u.test(bare)) return true;
  // A short all-caps word is an acronym: SSH, SHA, CPU.
  if (bare.length <= 4 && bare.length > 1 && bare === bare.toUpperCase()) return true;
  // Letters are judged on the new spelling: `Qo'oq` is `qöoq`, not
  // `qooq`, and every Uzbek `c` has become `ç`.
  const letters = wordToNew(word).replace(new RegExp(`[${APOS}]`, "g"), "").toLowerCase();
  if (/w|c|oo|ee|th/.test(letters)) return true;
  // A letter Uzbek does not use (ü, ı, â, é, …) — Turkish, French, German.
  return /[^a-zöğşç]/.test(letters);
}

function wordToNew(word: string): string {
  let out = "";
  for (let i = 0; i < word.length; i += 1) {
    const char = word.charAt(i);
    const next = word[i + 1];
    const lower = char.toLowerCase();
    if ((lower === "o" || lower === "g") && isApostrophe(next)) {
      const letter = lower === "o" ? "ö" : "ğ";
      out += char === lower ? letter : letter.toUpperCase();
      i += 1;
    } else if ((lower === "s" || lower === "c") && next?.toLowerCase() === "h") {
      const letter = lower === "s" ? "ş" : "ç";
      out += char === lower ? letter : letter.toUpperCase();
      i += 1;
    } else if (lower === "s" && isApostrophe(next) && word[i + 2]?.toLowerCase() === "h") {
      // `s'h` keeps two letters apart in the old alphabet (Is'hoq); the
      // new one has `ş`, so a plain `sh` is already two letters.
      out += char;
      i += 1;
    } else if (isApostrophe(char) && i > 0 && i < word.length - 1) {
      out += TUTUQ;
    } else {
      out += char;
    }
  }
  return out;
}

function wordToOld(word: string): string {
  const caps = word.length > 1 && word === word.toUpperCase();
  let out = "";
  for (const char of word) {
    switch (char) {
      case "ö":
        out += `o${TURNED_COMMA}`;
        break;
      case "Ö":
        out += `O${TURNED_COMMA}`;
        break;
      case "ğ":
        out += `g${TURNED_COMMA}`;
        break;
      case "Ğ":
        out += `G${TURNED_COMMA}`;
        break;
      case "ş":
        out += "sh";
        break;
      case "Ş":
        out += caps ? "SH" : "Sh";
        break;
      case "ç":
        out += "ch";
        break;
      case "Ç":
        out += caps ? "CH" : "Ch";
        break;
      default:
        out += char;
    }
  }
  return out;
}

function convert(text: string, word: (value: string) => string, skip: (value: string) => boolean): string {
  // A word right before `(` is a call — `chr(65)`, `push(x)` — not Uzbek.
  const plain = (part: string) =>
    part.replace(WORD, (match: string, offset: number, whole: string) =>
      whole[offset + match.length] === "(" || skip(match) ? match : word(match),
    );
  let out = "";
  let cursor = 0;
  for (const match of text.matchAll(PROTECTED)) {
    const start = match.index ?? 0;
    out += plain(text.slice(cursor, start)) + match[0];
    cursor = start + match[0].length;
  }
  return out + plain(text.slice(cursor));
}

/** Old Uzbek Latin → the alphabet of O'RQ-1184. */
export function toNewAlphabet(text: string): string {
  return convert(text, wordToNew, isForeignWord);
}

/** The new alphabet → old Uzbek Latin (`oʻ`, `gʻ` with U+02BB). */
export function toOldAlphabet(text: string): string {
  // Only letters outside Uzbek (ü, é, …) keep a word as it is here: the
  // English rules above judge old spelling, and a new-alphabet word has
  // no `sh`/`ch` to protect.
  return convert(text, wordToOld, (word) => /[^a-zöğşçʼ'’ʻ‘`´]/.test(word.toLowerCase()));
}
