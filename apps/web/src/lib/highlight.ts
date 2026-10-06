/** A light source highlighter for the attempt page.
 *
 *  Not a parser: it marks comments, strings, numbers and a shared set of
 *  keywords, which is what makes a submission readable at a glance. A
 *  full grammar per language (thirty-five of them) would be a dependency
 *  the page does not need; anything this does not recognise stays plain
 *  text, never wrong text — the tokens always join back to the source.
 */

export type TokenKind = "plain" | "comment" | "string" | "number" | "keyword";
export type Token = { kind: TokenKind; text: string };

type Family = { line: string[]; block: [string, string][]; quotes: string };

const C_LIKE: Family = { line: ["//"], block: [["/*", "*/"]], quotes: "\"'`" };
const HASH: Family = { line: ["#"], block: [], quotes: "\"'" };
const DASH: Family = { line: ["--"], block: [["{-", "-}"]], quotes: "\"" };
const ML: Family = { line: [], block: [["(*", "*)"]], quotes: "\"" };
const SEMI: Family = { line: [";"], block: [], quotes: "\"'" };
const PASCAL: Family = { line: ["//"], block: [["{", "}"], ["(*", "*)"]], quotes: "'" };

/** Comment and string syntax by language code prefix (`cpp23` → `cpp`). */
const FAMILIES: [string[], Family][] = [
  [["py", "pypy", "ruby", "perl", "r", "julia", "powershell", "php"], HASH],
  [["haskell", "lua", "ada", "sql"], DASH],
  [["ocaml", "caml", "fsharp"], ML],
  [["nasm", "lisp"], SEMI],
  [["pascal"], PASCAL],
];

function familyOf(language: string): Family {
  const name = language.replace(/\d+$/, "");
  for (const [names, family] of FAMILIES) {
    if (names.includes(name)) return family;
  }
  return C_LIKE;
}

/** Words that are keywords in most of the languages the judge runs. A
 *  word that is not a keyword in one of them is still a harmless accent. */
const KEYWORDS = new Set(
  (
    "if else elif for while do switch case default break continue return function def fn func fun " +
    "class struct enum interface trait impl import from include using namespace package module " +
    "public private protected static const let var val mut new delete try catch except finally " +
    "throw raise in of is not and or true false null nil None True False void int long double " +
    "float char bool string auto unsigned signed short template typename lambda yield async await " +
    "match with as pass begin end then procedure program uses type where sub my use"
  ).split(" "),
);

const WORD = /[A-Za-z_][A-Za-z0-9_]*/y;
const NUMBER = /(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/y;

export function highlight(source: string, language: string): Token[] {
  const family = familyOf(language);
  const tokens: Token[] = [];
  let plain = "";
  const push = (kind: TokenKind, text: string) => {
    if (plain) {
      tokens.push({ kind: "plain", text: plain });
      plain = "";
    }
    tokens.push({ kind, text });
  };

  let at = 0;
  scan: while (at < source.length) {
    for (const marker of family.line) {
      if (source.startsWith(marker, at)) {
        const end = source.indexOf("\n", at);
        const stop = end === -1 ? source.length : end;
        push("comment", source.slice(at, stop));
        at = stop;
        continue scan;
      }
    }
    for (const [open, close] of family.block) {
      if (source.startsWith(open, at)) {
        const end = source.indexOf(close, at + open.length);
        const stop = end === -1 ? source.length : end + close.length;
        push("comment", source.slice(at, stop));
        at = stop;
        continue scan;
      }
    }
    const char = source[at];
    if (family.quotes.includes(char)) {
      let end = at + 1;
      // A string ends at its quote or at the line's end: an apostrophe
      // that is not a string (a Rust lifetime) must not swallow the file.
      while (end < source.length && source[end] !== char && source[end] !== "\n") {
        end += source[end] === "\\" ? 2 : 1;
      }
      const stop = Math.min(source.length, source[end] === char ? end + 1 : end);
      push("string", source.slice(at, stop));
      at = stop;
      continue;
    }
    WORD.lastIndex = at;
    const word = WORD.exec(source);
    if (word) {
      if (KEYWORDS.has(word[0])) push("keyword", word[0]);
      else plain += word[0];
      at += word[0].length;
      continue;
    }
    NUMBER.lastIndex = at;
    const number = NUMBER.exec(source);
    if (number) {
      push("number", number[0]);
      at += number[0].length;
      continue;
    }
    plain += char;
    at += 1;
  }
  if (plain) tokens.push({ kind: "plain", text: plain });
  return tokens;
}
