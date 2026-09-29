import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  buildAttemptsHref,
  buildProblemTabHref,
  buildSolversHref,
  DEFAULT_PROBLEM_TAB,
  parseProblemTab,
  PROBLEM_TABS,
  resolveProblemTab,
} from "@/lib/problem-tabs";

describe("problem tabs", () => {
  it("defaults to description", () => {
    expect(DEFAULT_PROBLEM_TAB).toBe("description");
    expect(PROBLEM_TABS).toEqual([
      "description",
      "attempts",
      "editorial",
      "statistics",
      "solvers",
    ]);
  });

  it("resolves URL -> selected tab", () => {
    expect(resolveProblemTab(undefined)).toBe("description");
    expect(resolveProblemTab("description")).toBe("description");
    expect(resolveProblemTab("attempts")).toBe("attempts");
    expect(resolveProblemTab("editorial")).toBe("editorial");
    expect(resolveProblemTab("statistics")).toBe("statistics");
    expect(resolveProblemTab("solvers")).toBe("solvers");
  });

  it("accepts legacy names", () => {
    expect(parseProblemTab("statement")).toBe("description");
    expect(parseProblemTab("status")).toBe("attempts");
    expect(parseProblemTab("stats")).toBe("statistics");
    expect(parseProblemTab("solvers")).toBe("solvers");
  });

  it("falls back to description on invalid tab", () => {
    expect(parseProblemTab("nope")).toBeNull();
    expect(parseProblemTab("")).toBeNull();
    expect(parseProblemTab(null)).toBeNull();
    expect(resolveProblemTab("nope")).toBe("description");
    expect(resolveProblemTab("DESCRIPTION")).toBe("description");
    expect(resolveProblemTab(["attempts", "statistics"])).toBe("attempts");
  });

  it("builds selected tab -> URL", () => {
    // Description — yalang'och manzil (SEO kanonik toza qoladi).
    expect(buildProblemTabHref("a-plus-b", "description")).toBe(
      "/problems/a-plus-b",
    );
    expect(buildProblemTabHref("a-plus-b", "attempts")).toBe(
      "/problems/a-plus-b?tab=attempts",
    );
    expect(buildProblemTabHref("a-plus-b", "editorial")).toBe(
      "/problems/a-plus-b?tab=editorial",
    );
    expect(buildProblemTabHref("a-plus-b", "statistics")).toBe(
      "/problems/a-plus-b?tab=statistics",
    );
    expect(buildProblemTabHref("a-plus-b", "solvers")).toBe(
      "/problems/a-plus-b?tab=solvers",
    );
  });

  it("preserves contest context when switching tabs", () => {
    expect(
      buildProblemTabHref("a-plus-b", "attempts", { contest: "demo" }),
    ).toBe("/problems/a-plus-b?tab=attempts&contest=demo");
    expect(buildProblemTabHref("a-plus-b", "description", {})).toBe(
      "/problems/a-plus-b",
    );
  });

  it("keeps attempts filters inside tab=attempts", () => {
    expect(buildAttemptsHref("a-plus-b", {})).toBe(
      "/problems/a-plus-b?tab=attempts",
    );
    expect(
      buildAttemptsHref("a-plus-b", { verdict: "AC", mine: "true" }),
    ).toBe("/problems/a-plus-b?tab=attempts&verdict=AC&mine=true");
    // Eski kursor yangi ro'yxatga ishora qilmasligi uchun tashlanadi.
    expect(
      buildAttemptsHref("a-plus-b", { verdict: "AC", cursor: "abc" }),
    ).toBe("/problems/a-plus-b?tab=attempts&verdict=AC");
  });

  it("keeps solvers ordering inside tab=solvers", () => {
    expect(buildSolversHref("a-plus-b", "fast")).toBe(
      "/problems/a-plus-b?tab=solvers&ordering=fast",
    );
  });
});

describe("problem tabs wiring", () => {
  const src = (rel: string) =>
    readFileSync(fileURLToPath(new URL(rel, import.meta.url)), "utf8");

  it("renders accessible tab navigation without a half-tablist", () => {
    const tabs = src("../../src/features/problems/components/ProblemTabs.tsx");
    expect(tabs).toContain('aria-label={t(locale, "problem.tabsLabel")}');
    expect(tabs).toContain('aria-current={key === current ? "page" : undefined}');
    expect(tabs).toContain("scroll={false}");
    expect(tabs).toContain('data-kit-tabs="underline"');
    expect(tabs).toContain("rw-focus-ring");
    expect(tabs).not.toContain('role="tablist"');
    expect(tabs).not.toContain("useSearchParams");
    expect(tabs).not.toContain("useState");
    // Beshala tab bitta manbadan — ikki joyda yozilmaydi.
    expect(tabs).toContain("PROBLEM_TABS");
    for (const tab of [
      "description",
      "attempts",
      "editorial",
      "statistics",
      "solvers",
    ]) {
      expect(tabs).not.toContain(`"${tab}"`);
    }
  });

  it("reuses existing translations instead of new keys", () => {
    const tabs = src("../../src/features/problems/components/ProblemTabs.tsx");
    expect(tabs).toContain('"problem.tab.statement"');
    expect(tabs).toContain('"problem.tab.status"');
    expect(tabs).toContain('"editorial.title"');
    expect(tabs).toContain('"problem.tab.stats"');
    expect(tabs).toContain('"problem.tab.solvers"');
  });

  it("loads only the active tab data", () => {
    const page = src("../../src/app/(site)/problems/[slug]/page.tsx");
    expect(page).toContain("resolveProblemTab");
    // Har bir qo'shimcha so'rov faqat o'z tabi ichida.
    expect(page).toContain('tab === "attempts"');
    expect(page).toContain('tab === "statistics"');
    expect(page).toContain('tab === "solvers"');
    expect(page).not.toContain("Promise.all([");
    // Soxta statistika yo'q — hammasi mavjud API dan.
    expect(page).toContain("ProblemAttemptsPanel");
    expect(page).toContain("ProblemStatsPanel");
    expect(page).toContain("ProblemSolversPanel");
    expect(page).toContain("ProblemEditorialPanel");
    expect(page).toContain("notFound()");
  });

  it("handles loading, empty and error states", () => {
    const attempts = src(
      "../../src/app/(site)/problems/[slug]/_panels/ProblemAttemptsPanel.tsx",
    );
    expect(attempts).toContain("attempts.emptyFilteredTitle");
    expect(attempts).toContain("attempts.emptyTitle");
    expect(attempts).toContain("attempts.clearFilters");
    const stats = src(
      "../../src/features/problems/components/ProblemStatsPanel.tsx",
    );
    expect(stats).toContain("problem.stats.empty");
    expect(stats).toContain("EmptyState");
    const solvers = src(
      "../../src/features/problems/components/ProblemSolversPanel.tsx",
    );
    expect(solvers).toContain("problem.solvers.none");
    const editorial = src(
      "../../src/features/problems/components/ProblemEditorialPanel.tsx",
    );
    expect(editorial).toContain("editorial_state.available");
    expect(editorial).toContain("EmptyState");
  });

  it("respects existing auth rules instead of inventing new ones", () => {
    const page = src("../../src/app/(site)/problems/[slug]/page.tsx");
    // Shaxsiy maydonlar sessiya bilan o'qiladi (my_verdict, my_rating…).
    expect(page).toContain("getWithSession");
    const editorial = src(
      "../../src/features/problems/components/ProblemEditorialPanel.tsx",
    );
    // Paywall/login mantiqi `Editorial` ichida — panel qayta yozmaydi.
    expect(editorial).toContain("<Editorial");
    const attempts = src(
      "../../src/app/(site)/problems/[slug]/_panels/ProblemAttemptsPanel.tsx",
    );
    // Manba himoyasi backend'da — panel izohda qayd etadi.
    expect(attempts).toContain("IDOR");
  });

  it("keeps legacy routes as redirects, not duplicates", () => {
    const status = src(
      "../../src/app/(site)/problems/[slug]/status/page.tsx",
    );
    expect(status).toContain("redirect(");
    expect(status).toContain("tab=attempts");
    const stats = src("../../src/app/(site)/problems/[slug]/stats/page.tsx");
    expect(stats).toContain("redirect(");
    expect(stats).toContain("tab=statistics");
    const solvers = src(
      "../../src/app/(site)/problems/[slug]/solvers/page.tsx",
    );
    expect(solvers).toContain("redirect(");
    expect(solvers).toContain("tab=solvers");
  });

  it("points inner links at tab URLs, not legacy routes", () => {
    const filters = src(
      "../../src/features/submissions/components/AttemptFilters.tsx",
    );
    expect(filters).toContain("buildAttemptsHref");
    expect(filters).not.toContain("/status");
    const table = src(
      "../../src/features/submissions/components/AttemptTable.tsx",
    );
    expect(table).toContain("buildAttemptsHref");
    expect(table).not.toContain("/status");
  });
});
