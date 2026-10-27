import { describe, expect, it } from "vitest";

import { WIRE_VERSION, wireName } from "@/lib/useEventStream";

describe("event names on the wire", () => {
  it("carry the wire version", () => {
    expect(wireName("verdict")).toBe(`verdict.v${WIRE_VERSION}`);
    expect(wireName("notification")).toBe(`notification.v${WIRE_VERSION}`);
  });

  it("leave the resync control frame unversioned", () => {
    expect(wireName("resync")).toBe("resync");
  });
});
