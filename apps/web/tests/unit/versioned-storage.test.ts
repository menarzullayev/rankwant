import { describe, expect, it } from "vitest";

import { pack, readString, unpack } from "@/lib/versioned-storage";

describe("versioned storage", () => {
  it("round-trips a string", () => {
    expect(readString(pack(1, "int main(){}"), 1)).toBe("int main(){}");
  });

  it("reads a value written before versioning as it always was", () => {
    expect(readString("print(1)", 1)).toBe("print(1)");
    expect(unpack('["a","b"]', 1)).toEqual({ kind: "legacy", raw: '["a","b"]' });
  });

  it("ignores a value from a newer version instead of guessing", () => {
    expect(readString(pack(2, "x"), 1)).toBeNull();
    expect(unpack(pack(2, "x"), 1)).toEqual({ kind: "newer" });
  });

  it("falls back to the default when the data has the wrong shape", () => {
    expect(readString(pack(1, { not: "a string" }), 1)).toBeNull();
  });

  it("reports an absent value", () => {
    expect(unpack(null, 1)).toEqual({ kind: "empty" });
    expect(readString(null, 1)).toBeNull();
  });
});
