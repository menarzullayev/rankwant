import { describe, expect, it } from "vitest";

import { accentGateKind } from "@/lib/theme/apply";

describe("D52 accent gate copy", () => {
  it("does not call a null ratio an AA failure", () => {
    expect(
      accentGateKind({ error: "ground_unreadable", button: null, ink: null }),
    ).toBe("ground_unreadable");
    expect(
      accentGateKind({ error: "contrast_unreachable", button: null, ink: null }),
    ).toBe("contrast_unreachable");
    expect(accentGateKind({ button: null, ink: null })).toBe("ground_unreadable");
  });

  it("uses the AA sentence only when a ratio exists", () => {
    expect(accentGateKind({ button: 3.1, ink: 4.6 })).toBe("aa");
    expect(accentGateKind({ button: 4.6, ink: 3.2 })).toBe("aa");
    expect(accentGateKind({ button: 4.6, ink: 4.6 })).toBe("aa");
  });
});
