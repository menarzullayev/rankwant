import { describe, expect, it } from "vitest";

import { NAV } from "@/layout/nav";
import { uz } from "@/i18n/locales/uz";

/** The rail panel (`AppRail`) draws `nav.hint.<entry>` under every entry and
 *  builds that key at run time, so a new entry without a hint would show the
 *  raw key. This ties nav.ts to the dictionary. */
describe("rail hints", () => {
  it("every menu entry has a hint in the source dictionary", () => {
    const missing = NAV.map((item) => item.key.replace(/^nav\./, "nav.hint."))
      .filter((key) => !(key in uz));
    expect(missing).toEqual([]);
  });
});
