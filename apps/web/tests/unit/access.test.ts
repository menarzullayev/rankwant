import { describe, expect, it } from "vitest";

import { ACCESS, accessFor, loginHref, needsSignIn, sectionOf } from "@/lib/access";

describe("sectionOf", () => {
  it("is the first segment of the path", () => {
    expect(sectionOf("/")).toBe("");
    expect(sectionOf("/settings")).toBe("settings");
    expect(sectionOf("/settings/profil?tab=x#y")).toBe("settings");
    expect(sectionOf("/admin/users")).toBe("admin");
  });
});

describe("accessFor", () => {
  it("reads the level of the section", () => {
    expect(accessFor("/problems/a-plus-b")).toBe("public");
    expect(accessFor("/login?next=%2Fsettings")).toBe("guest");
    expect(accessFor("/notifications")).toBe("user");
    expect(accessFor("/admin/problems")).toBe("staff");
  });

  // A typo must end in "not found", not in a trip to the sign-in page.
  it("treats an unknown section as public", () => {
    expect(accessFor("/no-such-page")).toBe("public");
    // A plain object would answer for inherited names such as this one.
    expect(accessFor("/constructor")).toBe("public");
    expect(accessFor("/toString")).toBe("public");
  });

  // `/settingsx` is another section, not a page under `/settings`.
  it("matches whole segments only", () => {
    expect(accessFor("/settingsx")).toBe("public");
    expect(accessFor("/administrator")).toBe("public");
  });
});

describe("needsSignIn", () => {
  it("is true for user and staff sections only", () => {
    const closed = Object.keys(ACCESS).filter((section) => needsSignIn(`/${section}`));
    expect(closed.sort()).toEqual(["admin", "notifications", "onboarding", "settings"]);
  });

  // The statement of a problem is for everybody; only the solve panel is not.
  it("leaves the pages a guest reads open", () => {
    for (const path of ["/", "/problems", "/problems/a-plus-b", "/attempts", "/users/ali", "/qvant"]) {
      expect(needsSignIn(path)).toBe(false);
    }
  });
});

describe("loginHref", () => {
  it("carries the page to come back to", () => {
    expect(loginHref("/problems/a-plus-b?contest=demo")).toBe(
      "/login?tab=login&next=%2Fproblems%2Fa-plus-b%3Fcontest%3Ddemo",
    );
    expect(loginHref("/settings", "register")).toBe("/login?tab=register&next=%2Fsettings");
  });

  it("drops an address that is not an inner path", () => {
    for (const next of ["https://evil.example", "//evil.example", "/\\evil.example", "", null, undefined]) {
      expect(loginHref(next)).toBe("/login?tab=login");
    }
  });

  // Coming back to a sign-in page after signing in bounces for nothing.
  it("does not return to a sign-in page", () => {
    expect(loginHref("/login?tab=register")).toBe("/login?tab=login");
    expect(loginHref("/reset-password")).toBe("/login?tab=login");
  });
});
