import { describe, expect, it } from "vitest";

import { periodStart, type BillingOverview } from "@/features/billing/api/billing";
import { discountPercent, groupDigits } from "@/features/billing/format";

describe("billing price helpers", () => {
  it("groups digits the same way everywhere", () => {
    expect(groupDigits(315000)).toBe("315 000");
    expect(groupDigits(1069000)).toBe("1 069 000");
    expect(groupDigits(26250)).toBe("26 250");
    expect(groupDigits(0)).toBe("0");
  });

  it("shows a discount only against a higher struck price", () => {
    expect(discountPercent(315000, 525000)).toBe(40);
    expect(discountPercent(49000, 0)).toBe(0);
    expect(discountPercent(49000, 49000)).toBe(0);
  });
});

describe("periodStart", () => {
  const now = Date.parse("2026-11-10T12:00:00Z");
  const overview = (periods: BillingOverview["periods"]): BillingOverview =>
    ({ plans: [], providers: [], plan: "pro", plan_expires_at: null, periods }) as BillingOverview;
  const pro = { plan: "pro" as const, starts_at: "2026-11-01T00:00:00Z", ends_at: "2026-12-01T00:00:00Z", running: true };

  it("starts a lower or equal plan after the higher one ends", () => {
    expect(periodStart(overview([pro]), "plus", now)?.toISOString()).toBe("2026-12-01T00:00:00.000Z");
    expect(periodStart(overview([pro]), "pro", now)?.toISOString()).toBe("2026-12-01T00:00:00.000Z");
  });

  it("starts a higher plan now", () => {
    expect(periodStart(overview([pro]), "judge", now)).toBeNull();
    expect(periodStart(overview([]), "plus", now)).toBeNull();
  });
});
