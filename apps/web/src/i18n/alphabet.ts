/** The Uzbek alphabet a reader sees (ADR-0059).
 *
 *  The new alphabet (law O'RQ-1184) is the default; the old one stays a
 *  choice, kept in a cookie so the server renders the same text the browser
 *  hydrates. Only Uzbek has two: every other language ignores the cookie.
 *
 *  Choosing the old alphabet also pins `rw_locale` to `uz` when no language
 *  was chosen yet: the guest CDN rules (`tools/cf-guest-cache-rule.json`)
 *  skip any request carrying `rw_locale`, so a cached new-alphabet page is
 *  never served to an old-alphabet reader.
 */

import { toNewAlphabet, toOldAlphabet } from "@rankwant/shared/alphabet";

import type { Locale } from "./messages";

export const ALPHABET_COOKIE = "rw_alphabet";

export const ALPHABETS = ["new", "old"] as const;
export type Alphabet = (typeof ALPHABETS)[number];
export const DEFAULT_ALPHABET: Alphabet = "new";
/** The alphabet in force before O'RQ-1184. */
export const OLD_ALPHABET: Alphabet = "old";

/** The only locale with two alphabets. */
export const ALPHABET_LOCALE: Locale = "uz";

export function parseAlphabet(value: string | null | undefined): Alphabet {
  return value === "old" ? "old" : DEFAULT_ALPHABET;
}

/** The alphabet for `locale`: the choice applies to Uzbek only. */
export function alphabetFor(locale: Locale, choice: Alphabet): Alphabet {
  return locale === ALPHABET_LOCALE ? choice : DEFAULT_ALPHABET;
}

/** Reads the choice from a raw `Cookie` header (the server's request hook). */
export function alphabetFromCookieHeader(header: string | null | undefined): Alphabet {
  if (!header) return DEFAULT_ALPHABET;
  for (const part of header.split(";")) {
    const [name, ...rest] = part.trim().split("=");
    if (name === ALPHABET_COOKIE) return parseAlphabet(rest.join("="));
  }
  return DEFAULT_ALPHABET;
}

/** The `document.cookie` line that stores `alphabet` (the default clears it). */
export function alphabetCookieLine(alphabet: Alphabet): string {
  if (alphabet === DEFAULT_ALPHABET) return `${ALPHABET_COOKIE}=; path=/; max-age=0; samesite=lax`;
  return `${ALPHABET_COOKIE}=${alphabet}; path=/; max-age=31536000; samesite=lax`;
}

/** Where the server keeps the request's alphabet (`messages.server.ts`
 *  installs it; `AsyncLocalStorage` cannot be imported here, this module
 *  also runs in the browser). On `globalThis`, like the dictionary
 *  registry: server code is evaluated more than once. */
type AlphabetResolver = () => Alphabet | undefined;
const realm = globalThis as typeof globalThis & { __rwAlphabetResolver?: AlphabetResolver };

export function setAlphabetResolver(resolver: AlphabetResolver | undefined): void {
  realm.__rwAlphabetResolver = resolver;
}

/** The reader's alphabet choice — the request's on the server, the cookie in
 *  the browser. Both read the same cookie, so server HTML and hydration
 *  agree. */
export function readerAlphabet(): Alphabet {
  const fromRequest = realm.__rwAlphabetResolver?.();
  if (fromRequest) return fromRequest;
  if (typeof document !== "undefined") return alphabetFromCookieHeader(document.cookie);
  return DEFAULT_ALPHABET;
}

/** Content text in the reader's alphabet (ADR-0059). Only text written in
 *  Uzbek is touched — `lang` is the content's own language, never the
 *  interface's: an English statement must not lose its `sh`. */
export function inReaderAlphabet(text: string, lang: string | null | undefined): string {
  if (lang !== ALPHABET_LOCALE || !text) return text;
  return readerAlphabet() === OLD_ALPHABET ? toOldAlphabet(text) : toNewAlphabet(text);
}
