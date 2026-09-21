import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const header = src("../../src/layout/AppHeader.tsx");
const topnav = src("../../src/layout/AppTopNav.tsx");
const actions = src("../../src/layout/HeaderActions.tsx");

const CLUSTER = [
  "SearchBox",
  "HeaderStatus",
  "UpdatesBell",
  "CustomizerTrigger",
  "LocaleSwitch",
  "UserMenu",
] as const;

describe("H1 HeaderActions", () => {
  it("is the only right-cluster mount in both chrome trees", () => {
    expect(header).toContain("<HeaderActions");
    expect(topnav).toContain("<HeaderActions");
    for (const name of CLUSTER) {
      expect(header).not.toContain(`<${name}`);
      expect(topnav).not.toContain(`<${name}`);
    }
  });

  it("keeps the cluster order and hides search plus customizer on /login", () => {
    let last = -1;
    for (const name of CLUSTER) {
      const at = actions.indexOf(`<${name}`);
      expect(at).toBeGreaterThan(last);
      last = at;
    }
    expect(actions).toContain('pathname === "/login"');
    expect(actions).toContain("{!auth && <SearchBox");
    expect(actions).toContain("CUSTOMIZER_ENABLED && <CustomizerTrigger");
    expect(actions).not.toContain("ThemeToggle");
  });
});
