import type { MetadataRoute } from "next";

import { api, type Paginated } from "@/lib/api";
import { absolute } from "@/lib/site";

/** Sayt xaritasi.
 *
 * Har soatda qayta quriladi: arxiv kuniga bir necha marta o'zgaradi,
 * lekin har so'rovda 21 ta API chaqiruvi (2096 masala, sahifasiga 100 ta)
 * ortiqcha bo'lardi.
 */
export const revalidate = 3600;

const STATIC = [
  "/",
  "/problems",
  "/contests",
  "/leaderboard",
  "/learn",
  "/roadmaps",
  "/algorithms",
  "/blog",
  "/calendar",
  "/rating",
  "/about",
  "/team",
  "/arena",
  "/duels",
  "/tournaments",
  "/hackathons",
  "/quizzes",
];

/** Sahifalab hamma slug'ni yig'adi. Cheklov ATAYIN: buzuq javob yoki
 * kutilmagan hajm sitemap qurilishini cheksiz cho'zib yubormasin. */
async function allSlugs(
  fetchPage: (page: number) => Promise<Paginated<{ slug: string }>>,
  maxPages = 40,
): Promise<string[]> {
  const slugs: string[] = [];
  for (let page = 1; page <= maxPages; page++) {
    const body = await fetchPage(page);
    slugs.push(...body.results.map((row) => row.slug));
    if (!body.next) break;
  }
  return slugs;
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date();
  const entries: MetadataRoute.Sitemap = STATIC.map((path) => ({
    url: absolute(path),
    lastModified: now,
    changeFrequency: path === "/" ? "daily" : "weekly",
    priority: path === "/" ? 1 : 0.7,
  }));

  const groups: [string, () => Promise<string[]>][] = [
    ["/problems", () => allSlugs((p) => api.problemSlugs(p))],
    ["/contests", () => allSlugs((p) => api.contestSlugs(p))],
    ["/learn", () => allSlugs((p) => api.articleSlugs(p))],
    ["/blog", () => allSlugs((p) => api.postSlugs(p))],
  ];

  for (const [prefix, load] of groups) {
    try {
      for (const slug of await load()) {
        entries.push({
          url: absolute(`${prefix}/${slug}`),
          lastModified: now,
          changeFrequency: "weekly",
          priority: 0.6,
        });
      }
    } catch {
      // Bitta bo'lim olinmasa xarita BO'SH qolmasin — qolgani beriladi.
    }
  }
  return entries;
}
