import { expect, test } from "@playwright/test";

/**
 * ADR-0059: Uzbek in the new alphabet by default, the old one by choice.
 * The project pins the old alphabet for every other spec
 * (`playwright.config.ts`); this file looks at both.
 */

test.describe("yangi alifbo — standart", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("cookie'siz o'zbekcha yangi alifboda chiziladi", async ({ page }) => {
    await page.goto("/problems");
    await expect(page.locator('script[src^="/i18n/uz.js"]')).toHaveCount(1);
    await expect(page.getByRole("searchbox", { name: "Masala qidiriş" })).toBeVisible();
  });
});

test("rw_alphabet=old bilan eski alifbo", async ({ page }) => {
  await page.goto("/problems");
  await expect(page.locator('script[src^="/i18n/uz-old.js"]')).toHaveCount(1);
  await expect(page.getByRole("searchbox", { name: "Masala qidirish" })).toBeVisible();
});
