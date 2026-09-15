import type { MetadataRoute } from "next";

import { absolute, SITE_INDEXABLE } from "@/lib/site";

/** Qidiruv robotlari uchun.
 *
 * `Sitemap` qatori MUHIM: 2096 masalaning ko'pi bosh sahifadan bir necha
 * bosishda turadi va havola bo'yicha yurish ularni topa olmasligi mumkin.
 *
 * Xodim va shaxsiy bo'limlar indekslanmaydi — ular baribir kirishni
 * talab qiladi, robot esa ularga urinib bekorga vaqt sarflardi.
 */
export default function robots(): MetadataRoute.Robots {
  // Closed until launch (see SITE_INDEXABLE). No sitemap line: listing URLs
  // that robots.txt blocks only produces Search Console warnings.
  if (!SITE_INDEXABLE) {
    return { rules: [{ userAgent: "*", disallow: "/" }] };
  }
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: ["/admin", "/notifications"] },
    ],
    sitemap: absolute("/sitemap.xml"),
  };
}
