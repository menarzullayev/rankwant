import type { MetadataRoute } from "next";

import { absolute, SITE_INDEXABLE } from "@/lib/site";

/** AI crawlers, refused by owner decision (ADR-0023).
 *
 * On 2026-09-15 GPTBot alone made 82% of the zone's requests — 201,588 in
 * fourteen hours, more than half of them 404s on URLs that no longer exist.
 * This file only asks; the Cloudflare WAF rule in ADR-0023 is what stops the
 * crawlers that ignore it. Search engines are not on this list: RankWant wants
 * to be found, it just does not want to be training data.
 */
export const AI_CRAWLERS = [
  "GPTBot",
  "ChatGPT-User",
  "OAI-SearchBot",
  "ClaudeBot",
  "Claude-User",
  "Claude-SearchBot",
  "anthropic-ai",
  "CCBot",
  "Google-Extended",
  "PerplexityBot",
  "Perplexity-User",
  "Bytespider",
  "Amazonbot",
  "Applebot-Extended",
  "meta-externalagent",
  "FacebookBot",
  "Diffbot",
  "ImagesiftBot",
  "Timpibot",
  "YouBot",
  "cohere-ai",
];

/** Qidiruv robotlari uchun.
 *
 * `Sitemap` qatori MUHIM: 2096 masalaning ko'pi bosh sahifadan bir necha
 * bosishda turadi va havola bo'yicha yurish ularni topa olmasligi mumkin.
 *
 * Xodim va shaxsiy bo'limlar indekslanmaydi — ular baribir kirishni
 * talab qiladi, robot esa ularga urinib bekorga vaqt sarflardi.
 *
 * `/users/` ham yopiq: 10 001 ta `neytron_*` sinov profili filtr va cursor
 * parametrlari bilan deyarli cheksiz URL beradi — aynan shu 2026-09-15 da
 * Workers kunlik limitini tugatgan. 2026-09-20 HITL `keep-users-closed`:
 * 974k profil (CF import + sinov); foydalanuvchilarni o'chirish taqiqlangan,
 * shuning uchun «tozalangach ochiladi» emas — alohida HITL (allowlist)
 * bo'lmaguncha yopiq qoladi (ADR-0023). Sitemap'da `/users/` yo'q.
 */
export default function robots(): MetadataRoute.Robots {
  // Closed until launch (see SITE_INDEXABLE). No sitemap line: listing URLs
  // that robots.txt blocks only produces Search Console warnings.
  if (!SITE_INDEXABLE) {
    return { rules: [{ userAgent: "*", disallow: "/" }] };
  }
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: ["/admin", "/notifications", "/users/"] },
      { userAgent: AI_CRAWLERS, disallow: "/" },
    ],
    sitemap: absolute("/sitemap.xml"),
  };
}
