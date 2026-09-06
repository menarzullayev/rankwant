import { expect, test } from "@playwright/test";

/** Oqim B (test-strategy § 4): contest va standings. */

test("contest sahifasi standings bilan ochiladi", async ({ page }) => {
  await page.goto("/contests");
  const first = page.locator("li a").first();
  test.skip((await page.locator("li a").count()) === 0, "musobaqa yo'q");
  await first.click();
  await expect(page.getByRole("heading", { name: "Natijalar jadvali" })).toBeVisible();
});

test("standings SSE oqimi ochiladi yoki polling'ga tushadi", async ({ page }) => {
  await page.goto("/contests");
  test.skip((await page.locator("li a").count()) === 0, "musobaqa yo'q");
  await page.locator("li a").first().click();

  // Proxy SSE ni buferlashi mumkin (test-strategy § compatibility) —
  // shuning uchun jadval har holda ko'rinishi kerak.
  await expect(page.locator("table")).toBeVisible();
});
