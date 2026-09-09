import type { MetadataRoute } from "next";

import { absolute } from "@/lib/site";

/** Qidiruv robotlari uchun.
 *
 * `Sitemap` qatori MUHIM: 2096 masalaning ko'pi bosh sahifadan bir necha
 * bosishda turadi va havola bo'yicha yurish ularni topa olmasligi mumkin.
 *
 * Xodim va shaxsiy bo'limlar indekslanmaydi — ular baribir kirishni
 * talab qiladi, robot esa ularga urinib bekorga vaqt sarflardi.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow: ["/admin", "/notifications"] },
    ],
    sitemap: absolute("/sitemap.xml"),
  };
}
