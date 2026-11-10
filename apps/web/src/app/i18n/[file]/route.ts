import { ALPHABET_LOCALE, type Alphabet } from "@/i18n/alphabet";
import { LOCALES, isLocale, type Locale } from "@/i18n/messages";
import { dictionaryFile, dictionaryScript } from "@/i18n/messages.server";

/** The active language's dictionary as a static, cacheable script.
 *
 *  It used to travel inside every page: 72 kB of each HTML response and a
 *  third of the render CPU (docs/research/2026-09-18-homepage-profile). As a
 *  file it is built once, cached by the browser and the CDN, and fetched in
 *  parallel with the app's own scripts. Uzbek has two files, one per
 *  alphabet (ADR-0059): `uz.js` (new) and `uz-old.js`. */
export const dynamic = "force-static";
export const dynamicParams = false;

const FILES: { file: string; locale: Locale; alphabet: Alphabet }[] = [
  ...LOCALES.map((locale) => ({ file: dictionaryFile(locale), locale, alphabet: "new" as const })),
  {
    file: dictionaryFile(ALPHABET_LOCALE, "old"),
    locale: ALPHABET_LOCALE,
    alphabet: "old" as const,
  },
];

export function generateStaticParams() {
  return FILES.map(({ file }) => ({ file }));
}

export async function GET(_request: Request, ctx: RouteContext<"/i18n/[file]">) {
  const { file } = await ctx.params;
  const entry = FILES.find((row) => row.file === file);
  if (!entry || !isLocale(entry.locale)) return new Response("Not found", { status: 404 });
  return new Response(dictionaryScript(entry.locale, entry.alphabet), {
    headers: {
      "Content-Type": "text/javascript; charset=utf-8",
      // The address carries the dictionary's content hash (`dictionaryUrl`),
      // so the content never changes under the same URL.
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
}
