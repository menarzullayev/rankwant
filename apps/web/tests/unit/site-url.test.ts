import { afterEach, describe, expect, it, vi } from "vitest";

// Both values are baked at build time, and since 2026-11-10 the web Dockerfile
// declares `ENV NEXT_PUBLIC_X=$NEXT_PUBLIC_X` for each. A build without the
// value therefore bakes `""`, not `undefined` — these tests pin what `""` means.

async function load<T>(path: string): Promise<T> {
  vi.resetModules();
  return (await import(path)) as T;
}

const siteUrl = async () => (await load<typeof import("@/lib/site")>("@/lib/site")).SITE_URL;
const customizer = async () =>
  (await load<typeof import("@/lib/theme/flag")>("@/lib/theme/flag")).CUSTOMIZER_ENABLED;

afterEach(() => {
  vi.unstubAllEnvs();
});

describe("SITE_URL", () => {
  // With `??` the empty string won: SITE_URL was "" and `new URL(SITE_URL)` in
  // proxy.ts threw `TypeError: Invalid URL` while the module loaded.
  it("treats an empty build arg as unset and takes the origin of the API base", async () => {
    vi.stubEnv("NEXT_PUBLIC_SITE_URL", "");
    vi.stubEnv("NEXT_PUBLIC_API_BASE", "https://rankwant.uz/api/v1");
    expect(await siteUrl()).toBe("https://rankwant.uz");
  });

  it("uses an explicit value, without its trailing slash", async () => {
    vi.stubEnv("NEXT_PUBLIC_SITE_URL", "https://example.uz/");
    vi.stubEnv("NEXT_PUBLIC_API_BASE", "https://rankwant.uz/api/v1");
    expect(await siteUrl()).toBe("https://example.uz");
  });

  it("falls back to localhost when neither is set", async () => {
    vi.stubEnv("NEXT_PUBLIC_SITE_URL", "");
    vi.stubEnv("NEXT_PUBLIC_API_BASE", "");
    expect(await siteUrl()).toBe("http://localhost:3000");
  });
});

describe("CUSTOMIZER_ENABLED", () => {
  it("is on when the build arg is empty", async () => {
    vi.stubEnv("NEXT_PUBLIC_CUSTOMIZER", "");
    expect(await customizer()).toBe(true);
  });

  it("is off only for 0", async () => {
    vi.stubEnv("NEXT_PUBLIC_CUSTOMIZER", "0");
    expect(await customizer()).toBe(false);
  });
});
