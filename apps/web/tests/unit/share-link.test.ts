import { afterEach, describe, expect, it, vi } from "vitest";

import { TEMPLATES_KEY, rememberAppearance } from "@/lib/prefs";
import {
  decodeAppearance,
  decodeTheme,
  encodeAppearance,
  exportAppearance,
  importAppearance,
  shareUrl,
  stripAppearance,
} from "@/lib/theme/share";

afterEach(() => {
  vi.unstubAllGlobals();
});

function stubLocation(href: string) {
  vi.stubGlobal("window", { location: { href } });
}

// A shared link used to carry the style but not the mode, so a dark
// Terminal look opened in light (APP-6).
describe("share link theme", () => {
  it("writes an explicit light or dark mode", () => {
    expect(encodeAppearance({ style: "terminal" }, "dark")).toBe("style=terminal&theme=dark");
    expect(encodeAppearance({ style: "terminal" }, "light")).toBe("style=terminal&theme=light");
  });

  it("leaves `system` out like every other default, so the recipient keeps their own mode", () => {
    expect(encodeAppearance({ style: "terminal" }, "system")).toBe("style=terminal");
    expect(encodeAppearance({ style: "terminal" })).toBe("style=terminal");
  });

  it("reads the three known modes and nothing else", () => {
    expect(decodeTheme("?theme=dark")).toBe("dark");
    expect(decodeTheme("?theme=light")).toBe("light");
    expect(decodeTheme("?theme=system")).toBe("system");
    expect(decodeTheme("?theme=pink")).toBeNull();
    expect(decodeTheme("?style=terminal")).toBeNull();
    expect(decodeTheme("")).toBeNull();
  });

  it("keeps the mode out of the appearance group", () => {
    expect(decodeAppearance("?theme=dark")).toBeNull();
    expect(decodeAppearance("?theme=dark&style=terminal")).toEqual({ style: "terminal" });
  });

  it("round-trips overlayStyle except the Qogoz default", () => {
    expect(encodeAppearance({ overlayStyle: "soyabon" })).toBe("overlayStyle=soyabon");
    expect(encodeAppearance({ overlayStyle: "qogoz" })).toBe("");
    expect(decodeAppearance("?overlayStyle=orol")).toEqual({ overlayStyle: "orol" });
    expect(decodeAppearance("?overlayStyle=latta")).toEqual({ overlayStyle: "qogoz" });
  });

  it("round-trips formStyle except the Maydon default", () => {
    expect(encodeAppearance({ formStyle: "qator" })).toBe("formStyle=qator");
    expect(encodeAppearance({ formStyle: "maydon" })).toBe("");
    expect(decodeAppearance("?formStyle=orol")).toEqual({ formStyle: "orol" });
    expect(decodeAppearance("?formStyle=chiziq")).toEqual({ formStyle: "maydon" });
  });

  it("round-trips style and mode together", () => {
    const search = `?${encodeAppearance({ style: "terminal", density: "compact" }, "dark")}`;
    expect(decodeAppearance(search)).toEqual({ style: "terminal", density: "compact" });
    expect(decodeTheme(search)).toBe("dark");
  });

  it("strips the mode from the address after applying it", () => {
    stubLocation("https://rankwant.uz/problems?page=2&theme=dark&style=glass#top");
    expect(stripAppearance()).toBe("/problems?page=2#top");
  });

  it("replaces a stale mode when sharing, and drops it for `system`", () => {
    stubLocation("https://rankwant.uz/problems?page=2&theme=dark");
    const light = new URL(shareUrl({ style: "terminal" }, "light"));
    expect(light.searchParams.get("theme")).toBe("light");
    expect(light.searchParams.get("page")).toBe("2");
    const system = new URL(shareUrl({ style: "terminal" }, "system"));
    expect(system.searchParams.has("theme")).toBe(false);
  });
});

// APP-4: the JSON file carries the mode as well, without a new version.
describe("appearance file theme", () => {
  const appearance = { style: "terminal", size: 110 };
  const a11y = { vision: "normal" as const, motion: "system" as const };

  it("round-trips the mode", () => {
    const result = importAppearance(exportAppearance(appearance, a11y, "dark"));
    expect(result.ok && result.theme).toBe("dark");
  });

  it("reads a file saved before the mode existed", () => {
    const old = JSON.stringify({ version: 1, appearance, a11y });
    const result = importAppearance(old);
    expect(result.ok).toBe(true);
    expect(result.ok && "theme" in result).toBe(false);
  });

  it("drops an unknown mode but keeps the rest of the file", () => {
    const odd = JSON.stringify({ version: 1, appearance, a11y, theme: "pink" });
    const result = importAppearance(odd);
    expect(result.ok && result.appearance.style).toBe("terminal");
    expect(result.ok && "theme" in result).toBe(false);
  });
});

// `rememberAppearance` used to write `[]` over the saved templates whenever
// a caller left them out: a shared link and the sign-in sync both did.
describe("rememberAppearance", () => {
  function stubStorage() {
    const store = new Map<string, string>([[TEMPLATES_KEY, '[{"name":"Tun"}]']]);
    vi.stubGlobal("localStorage", {
      getItem: (key: string) => store.get(key) ?? null,
      setItem: (key: string, value: string) => void store.set(key, value),
    });
    vi.stubGlobal("document", { cookie: "" });
    return store;
  }

  it("leaves saved templates alone when none are passed", () => {
    const store = stubStorage();
    rememberAppearance({ style: "terminal" }, {});
    expect(store.get(TEMPLATES_KEY)).toBe('[{"name":"Tun"}]');
  });

  it("writes the list it is given, including an empty one", () => {
    const store = stubStorage();
    rememberAppearance({ style: "terminal" }, {}, []);
    expect(store.get(TEMPLATES_KEY)).toBe("[]");
  });
});
