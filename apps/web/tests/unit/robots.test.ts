import { describe, expect, it } from "vitest";

import robots, { AI_CRAWLERS } from "@/app/robots";
import { absolute, SITE_INDEXABLE } from "@/lib/site";

const rules = () => {
  const result = robots().rules;
  return Array.isArray(result) ? result : [result];
};

describe("robots.txt", () => {
  // Lighthouse read `Disallow: /` and scored SEO 66 with a single failing
  // audit (`is-crawlable`). The site being open is the decision, not a detail.
  it("lets search engines in and points them at the sitemap", () => {
    expect(SITE_INDEXABLE).toBe(true);
    const open = rules().find((rule) => rule.userAgent === "*");
    expect(open?.allow).toBe("/");
    // `absolute()` reads NEXT_PUBLIC_SITE_URL, which the test env does not set;
    // what matters here is that the line is there and points at the sitemap.
    expect(robots().sitemap).toBe(absolute("/sitemap.xml"));
    expect(robots().sitemap).toMatch(/\/sitemap\.xml$/);
  });

  // The crawl that used up the Workers quota was 82% GPTBot. robots.txt is
  // only a request, so ADR-0023 pairs it with a Cloudflare WAF rule; this test
  // guards the half that lives in the repository.
  it("refuses the AI crawlers by name", () => {
    const refused = rules().find((rule) => Array.isArray(rule.userAgent));
    expect(refused?.disallow).toBe("/");
    for (const crawler of ["GPTBot", "ClaudeBot", "CCBot", "Google-Extended", "Bytespider"]) {
      expect(AI_CRAWLERS).toContain(crawler);
    }
    expect(refused?.userAgent).toEqual(AI_CRAWLERS);
  });

  // 10,001 seeded `neytron_*` profiles times filter and cursor parameters is
  // an endless URL space; it was the crawl target on 2026-09-15.
  it("keeps the seeded profiles and the staff pages out of the crawl", () => {
    const open = rules().find((rule) => rule.userAgent === "*");
    expect(open?.disallow).toEqual(["/admin", "/notifications", "/users/"]);
  });
});
