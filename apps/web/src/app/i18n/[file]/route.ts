import { LOCALES, isLocale } from "@/i18n/messages";
import { dictionaryScript } from "@/i18n/messages.server";

/** The active language's dictionary as a static, cacheable script.
 *
 *  It used to travel inside every page: 72 kB of each HTML response and a
 *  third of the render CPU (docs/research/2026-09-18-homepage-profile). As a
 *  file it is built once, cached by the browser and the CDN, and fetched in
 *  parallel with the app's own scripts. */
export const dynamic = "force-static";
export const dynamicParams = false;

export function generateStaticParams() {
  return LOCALES.map((locale) => ({ file: `${locale}.js` }));
}

export async function GET(_request: Request, ctx: RouteContext<"/i18n/[file]">) {
  const { file } = await ctx.params;
  const locale = file.replace(/\.js$/, "");
  if (!isLocale(locale)) return new Response("Not found", { status: 404 });
  return new Response(dictionaryScript(locale), {
    headers: {
      "Content-Type": "text/javascript; charset=utf-8",
      // The address carries the dictionary's content hash (`dictionaryUrl`),
      // so the content never changes under the same URL.
      "Cache-Control": "public, max-age=31536000, immutable",
    },
  });
}
