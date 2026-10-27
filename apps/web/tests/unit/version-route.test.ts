import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "@/app/version/route";

describe("/version", () => {
  afterEach(() => vi.unstubAllEnvs());

  it("answers with the commit the image was built from", async () => {
    vi.stubEnv("GIT_SHA", "a".repeat(40));
    const response = GET();
    expect(await response.json()).toEqual({ sha: "a".repeat(40) });
    expect(response.headers.get("Cache-Control")).toBe("no-store");
  });

  it("says `unknown` when the build argument was not given", async () => {
    vi.stubEnv("GIT_SHA", "");
    expect(await GET().json()).toEqual({ sha: "unknown" });
  });
});
