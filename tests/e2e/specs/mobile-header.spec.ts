import { expect, test } from "@playwright/test";

/**
 * Header mobilda sig'ishi kerak.
 *
 * Kirgan foydalanuvchida u eng to'liq holatga keladi (balans, streak,
 * qo'ng'iroq, uslub, tema, admin, profil, chiqish) va 375px ekranda
 * o'ng chekka kesilardi — belgilar ko'rinmay qolardi.
 */

const API = process.env.E2E_API_BASE ?? "http://localhost:8000/api/v1";
const SITE = process.env.E2E_BASE_URL ?? "http://localhost:3000";
const sameOrigin = new URL(API, SITE).origin === new URL(SITE).origin;

async function headerOverflow(page: import("@playwright/test").Page) {
  return page.evaluate(() => {
    const header = document.querySelector("header");
    if (!header) return null;
    return {
      width: Math.round(header.getBoundingClientRect().width),
      content: header.scrollWidth,
    };
  });
}

test("mehmon header'i 375px da sig'adi", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto("/problems");

  const size = await headerOverflow(page);
  expect(size).not.toBeNull();
  expect(size!.content).toBeLessThanOrEqual(size!.width);
});

test("kirgan foydalanuvchi header'i ham 375px da sig'adi", async ({ page }) => {
  test.skip(
    !sameOrigin,
    "sayt va API alohida originda — sessiya cookie yetmaydi",
  );

  const username = `e2ehdr_${Date.now()}`;
  const password = "E2eParol!12345";
  await page.request.post(`${API}/auth/register/`, {
    data: { username, password, email: `${username}@example.uz` },
  });
  await page.request.post(`${API}/auth/login/`, {
    data: { username, password },
  });

  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto("/problems");
  // Sessiyaga bog'liq bo'laklar hidratsiyadan keyin chiqadi.
  await expect(
    page.getByRole("button", { name: "Uslubni tanlash" }),
  ).toBeVisible();

  const size = await headerOverflow(page);
  expect(size!.content).toBeLessThanOrEqual(size!.width);
});
