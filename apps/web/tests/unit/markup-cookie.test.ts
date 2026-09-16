import { describe, expect, it } from "vitest";
import { type MarkupPrefs, parseMarkupCookie, serializeMarkupCookie } from "@/lib/prefs";

// Server and client both read this cookie; if the two sides disagree, React
// hydration breaks on every page that renders a verdict (D61).
describe("markup cookie", () => {
  it("round-trips every non-default choice", () => {
    const prefs: MarkupPrefs = {
      verdictStyle: "circle",
      statusStyle: "text",
      loadingStyle: "skeleton",
      iconPack: "phosphor",
    };
    expect(parseMarkupCookie(serializeMarkupCookie(prefs))).toEqual(prefs);
  });

  it("leaves defaults out, so the cookie stays empty for most visitors", () => {
    expect(
      serializeMarkupCookie({
        verdictStyle: "auto",
        statusStyle: "auto",
        loadingStyle: "spinner",
        iconPack: "lucide",
      }),
    ).toBe("");
  });

  it("reads a missing or empty cookie as no preferences", () => {
    expect(parseMarkupCookie(undefined)).toEqual({});
    expect(parseMarkupCookie(null)).toEqual({});
    expect(parseMarkupCookie("")).toEqual({});
  });

  it("ignores unknown keys and pairs without a value", () => {
    expect(parseMarkupCookie("x=1&v=&s=text&garbage")).toEqual({ statusStyle: "text" });
  });
});
