import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const src = (rel: string) =>
  readFileSync(fileURLToPath(new URL(rel, import.meta.url)), "utf8");

describe("login first paint is the form", () => {
  it("does not wrap AuthTabs or AuthForm in Suspense", () => {
    const page = src("../../src/app/(auth)/login/page.tsx");
    expect(page).not.toContain("AuthFormSkeleton");
    const tabs = page.indexOf("<AuthTabs");
    const form = page.indexOf("<AuthForm");
    const suspense = page.indexOf("<Suspense fallback");
    expect(tabs).toBeGreaterThan(-1);
    expect(form).toBeGreaterThan(tabs);
    expect(suspense).toBeGreaterThan(form);
    expect(page.slice(suspense)).toContain("<AuthProof");
    expect(page).toContain("next={nextOf(params)}");
    expect(page).toContain("link={one(params.link)}");
    expect(page).toContain("min-h-[4.5rem]");
  });

  it("AuthTabs is a server component and keeps next in the href", () => {
    const tabs = src("../../src/components/auth/AuthTabs.tsx");
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
    const form = src("../../src/components/AuthForm.tsx");
    expect(form).not.toMatch(/useSearchParams/);
    expect(form).toContain("next?: string | null");
    const reset = src("../../src/components/ResetForm.tsx");
    expect(reset).not.toMatch(/useSearchParams/);
    expect(reset).toContain("token = \"\"");
  });
});
