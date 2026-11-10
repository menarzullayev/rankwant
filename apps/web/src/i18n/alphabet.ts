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

import type { Locale } from "./messages";

export const ALPHABET_COOKIE = "rw_alphabet";

export const ALPHABETS = ["new", "old"] as const;
export type Alphabet = (typeof ALPHABETS)[number];
export const DEFAULT_ALPHABET: Alphabet = "new";

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
