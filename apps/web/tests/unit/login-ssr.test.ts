import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const src = (rel: string) =>
  readFileSync(fileURLToPath(new URL(rel, import.meta.url)), "utf8");

describe("login first paint is the form", () => {
  it("does not wrap AuthTabs or AuthForm in Suspense", () => {
    const page = src("../../src/app/(auth)/login/page.tsx");
    expect(page).not.toContain("AuthFormSkeleton");
    // Nothing on the page suspends: the form is the first paint.
    expect(page).not.toContain("<Suspense");
    const heading = page.indexOf("<h1");
    const tabs = page.indexOf("<AuthTabs");
    const form = page.indexOf("<AuthForm");
    expect(heading).toBeGreaterThan(-1);
    expect(tabs).toBeGreaterThan(heading);
    expect(form).toBeGreaterThan(tabs);
    expect(page).toContain("next={nextOf(params)}");
    expect(page).toContain("link={one(params.link)}");
  });

  it("the sign-in shell makes no API request", () => {
    // Decision 18 dropped a split screen whose panel rendered live stats:
    // an API outage left it empty. The panel is back, so it stays static.
    const shell = src("../../src/features/auth/components/AuthShell.tsx");
    expect(shell).not.toMatch(/from ["']@\/lib\/api["']/);
    expect(shell).not.toContain("fetch(");
  });

  it("AuthTabs is a server component and keeps next in the href", () => {
    const tabs = src("../../src/features/auth/components/AuthTabs.tsx");
    expect(tabs).not.toMatch(/from ["']next\/navigation["']/);
    expect(tabs).not.toContain('"use client"');
    expect(tabs).toContain("if (next) query.set(\"next\", next)");
  });

  it("login does not inline the full site stylesheet", () => {
    const root = src("../../src/app/layout.tsx");
    const auth = src("../../src/app/(auth)/layout.tsx");
    const site = src("../../src/app/(site)/layout.tsx");
    expect(root).not.toMatch(/import ["']\.\/globals\.css["']/);
    expect(auth).toContain('import "../auth.css"');
    expect(site).toContain('import "../globals.css"');
  });

  it("AuthForm and ResetForm read query from props", () => {
    const form = src("../../src/features/account/components/AuthForm.tsx");
    expect(form).not.toMatch(/useSearchParams/);
    expect(form).toContain("next?: string | null");
    const reset = src("../../src/features/account/components/ResetForm.tsx");
    expect(reset).not.toMatch(/useSearchParams/);
    expect(reset).toContain("token = \"\"");
  });
});
