import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

function src(rel: string): string {
  return readFileSync(resolve(__dirname, rel), "utf8");
}

const menu = src("../../src/layout/UserMenu.tsx");

describe("H4 overflow-you", () => {
  it("keeps the sign-in link on one line", () => {
    expect(menu).toContain('"/login?tab=login"');
    expect(menu).toContain("whitespace-nowrap");
  });

  it("puts profile, settings, and logout in one account menu", () => {
    expect(menu).toContain('aria-controls="rw-account-menu"');
    expect(menu).toContain('id="rw-account-menu"');
    expect(menu).toContain("settings.nav.profile");
    expect(menu).toContain("/settings/profil");
    expect(menu).toContain("auth.logout");
    expect(menu).toContain('role="menu"');
    expect(menu).not.toContain("sm:flex");
  });

  it("opens the appearance panel and switches the theme below xl", () => {
    expect(menu).toContain("customizer.setOpen(true)");
    // Every row is a 44 px target.
    expect(menu).toContain('"flex min-h-11 w-full items-center');
    expect(menu).toContain("toggleTheme(");
    expect(menu.match(/<li role="none" className="xl:hidden">/g)).toHaveLength(2);
  });
});
