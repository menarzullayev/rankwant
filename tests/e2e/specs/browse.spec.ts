import { expect, test } from "@playwright/test";

/** Anonim foydalanuvchi uchun ochiq sahifalar — smoke qatlami. */

test("bosh sahifa ochiladi", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "RankWant" })).toBeVisible();
});

test("masalalar arxivi serverda render bo'ladi", async ({ page }) => {
  // JS o'chirilgan holatda ham mazmun bo'lishi kerak — SSR SEO uchun
  // qo'shilgan (ADR-0003), shuning uchun HTML da matn bo'lishi shart.
  const response = await page.goto("/problems");
  const html = await response!.text();
  expect(html).toContain("Masalalar arxivi");
  await expect(page.getByRole("heading", { name: "Masalalar arxivi" })).toBeVisible();
});

test("masala sahifasida o'z metadata si bor", async ({ page }) => {
  await page.goto("/problems");
  const first = page.locator("tbody tr a").first();
  const title = await first.textContent();
  await first.click();
  await expect(page).toHaveTitle(new RegExp(title!.trim()));
});

test("reyting formulalari ochiq", async ({ page }) => {
  await page.goto("/rating");
  // Launch gate sharti: 4 formulaning HAMMASI ko'rinishi kerak
  for (const name of ["Skills", "Contests", "Activity", "Challenges"]) {
    await expect(page.getByRole("heading", { name, exact: false })).toBeVisible();
  }
  await expect(page.getByText("0.95")).toBeVisible();
});

test("leaderboard Phase 0 va Phase 1 reytinglarini ko'rsatadi", async ({ page }) => {
  await page.goto("/leaderboard");
  await expect(page.getByText("Skills")).toBeVisible();
  await expect(page.getByText("Contests")).toBeVisible();
  await expect(page.getByText("Activity")).toBeVisible();
  // Challenges — Phase 3, hali ko'rinmasligi kerak
  await expect(page.getByText("Challenges")).toHaveCount(0);
});
