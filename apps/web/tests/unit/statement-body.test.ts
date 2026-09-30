import { describe, expect, it } from "vitest";

import { stripDuplicateStatementHeading } from "@/lib/statement-body";

describe("stripDuplicateStatementHeading", () => {
  it("removes leading h2 when it matches the title", () => {
    const body = "## A + B\n\nBitta qator.";
    expect(stripDuplicateStatementHeading(body, "A + B")).toBe("Bitta qator.");
  });

  it("keeps heading when it differs", () => {
    const body = "## Other\n\nText.";
    expect(stripDuplicateStatementHeading(body, "A + B")).toBe(body);
  });

  it("ignores non-heading bodies", () => {
    const body = "Plain paragraph.";
    expect(stripDuplicateStatementHeading(body, "A + B")).toBe(body);
  });
});
