import { describe, expect, it } from "vitest";

import { splitMarker } from "@/components/MarkerText";

/** ADR-0027 § L2 — the marker is what separates the 16 tiers inside a
 *  shared colour group (five of them are "red"). */
describe("splitMarker", () => {
  it("inks nothing when the tier has no marker", () => {
    // Magnetar (tier 12) is red/0 — nothing is inked.
    expect(splitMarker("tourist", 0)).toEqual(["", "tourist"]);
  });

  it("splits a handle longer than the marker", () => {
    // Cosmos (tier 16) is red/4 — the first 4 characters are inked.
    expect(splitMarker("tourist", 4)).toEqual(["tour", "ist"]);
  });

  it("inks the whole handle when it is shorter than the marker", () => {
    // "Alex" at Cosmos (marker 4) must be entirely inked, otherwise it
    // looks identical to "Alex" at Magnetar (marker 0) and the marker
    // stops separating the five red tiers. ADR-0027 § L2.
    expect(splitMarker("Alex", 4)).toEqual(["Alex", ""]);
  });

  it("inks the whole handle when it is exactly as long as the marker", () => {
    expect(splitMarker("Alex", 4)).toEqual(["Alex", ""]);
    expect(splitMarker("abcd", 4)).toEqual(["abcd", ""]);
  });

  it("inks the whole handle when the marker exceeds its length", () => {
    expect(splitMarker("ab", 4)).toEqual(["ab", ""]);
  });

  it("handles a single-character handle", () => {
    expect(splitMarker("x", 1)).toEqual(["x", ""]);
    expect(splitMarker("x", 4)).toEqual(["x", ""]);
  });

  it("handles an empty handle", () => {
    expect(splitMarker("", 4)).toEqual(["", ""]);
  });

  it("inks the whole tier name for every tier badge", () => {
    // The badge text is the localised tier name; marker 0 still leaves it
    // plain (no split), higher markers ink the leading characters.
    expect(splitMarker("Cosmos", 4)).toEqual(["Cosm", "os"]);
    expect(splitMarker("Quark", 0)).toEqual(["", "Quark"]);
    expect(splitMarker("Molecule", 2)).toEqual(["Mo", "lecule"]);
  });
});
