import { describe, expect, it } from "vitest";

import { date, dateTime, time } from "@/i18n/messages";
import { DISPLAY_TIME_ZONE } from "@rankwant/shared/i18n";
import { numericStamp, SITE_TZ } from "@rankwant/shared/format";

// 09:56:31 UTC is 14:56:31 in Tashkent — and 23:30 UTC is already the
// next day there.
const NOON = "2026-09-30T09:56:31Z";
const LATE = "2026-09-30T23:30:00Z";

describe("dates are written in the site's zone", () => {
  it("uses one zone for the helpers and the formatter", () => {
    expect(DISPLAY_TIME_ZONE).toBe(SITE_TZ);
  });

  it("does not depend on the zone of the machine that renders", () => {
    expect(time(NOON, "en")).toContain("2:56:31");
    expect(dateTime(NOON, "en")).toContain("2:56:31");
    expect(date(LATE, "en")).toContain("10/1/2026");
  });

  it("lets a caller ask for another zone", () => {
    expect(time(NOON, "en", { timeZone: "UTC" })).toContain("9:56:31");
    expect(date(LATE, "en", { timeZone: "UTC" })).toContain("9/30/2026");
  });

  it("writes a digits-only stamp that no ICU can disagree about", () => {
    expect(numericStamp(NOON)).toBe("30.09.2026 14:56:31");
    expect(numericStamp(LATE)).toBe("01.10.2026 04:30:00");
    expect(numericStamp("2026-01-05T19:00:00Z")).toBe("06.01.2026 00:00:00");
  });
});
