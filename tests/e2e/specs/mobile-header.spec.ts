import { expect, test } from "@playwright/test";

import { skipUnlessLocal } from "./guard";

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
  skipUnlessLocal();
  test.skip(
    !sameOrigin,
    "sayt va API alohida originda — sessiya cookie yetmaydi",
  );

  const username = `e2ehdr_${Date.now()}`;
  const password = "E2eParol!12345";
  await page.request.post(`${API}/auth/register/`, {
    data: { username, password, email: `${username}@example.uz`, terms_accepted: true },
  });
  await page.request.post(`${API}/auth/login/`, {
    data: { identifier: username, password },
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

/**
 * Sahifa telefon ekraniga SIG'ISHI kerak.
 *
 * O'lchandi: arxiv 412 px li ekranda 629 px, masala sahifasi 600 px
 * bo'lib ketardi — sahifa yon tomonga siljir, submit panelidagi tab
 * tugmalarini esa umuman bosib bo'lmasdi (Monaco qatlami ustiga
 * chiqardi). Sabab `min-w-0` emas edi: mobilda `grid-cols` ko'rsatilmasa
 * element yashirin `auto` trekka tushadi va TREK mazmun bo'yicha
 * kengayadi.
 *
 * Keng jadval o'z `overflow-x-auto` konteynerida aylanishi kerak,
 * SAHIFA emas.
 */
const PAGES = [
  "/",
  "/problems",
  "/problems/a-plus-b",
  "/leaderboard",
  "/contests",
  "/attempts",
  "/qvant",
  "/learn",
  "/calendar",
];

for (const path of PAGES) {
  test(`${path} telefon ekraniga sig'adi`, async ({ page }) => {
    await page.goto(path);
    const { scrollWidth, clientWidth } = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
    }));
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 4);
  });
}

test("birinchi Tab mazmunga o'tish havolasini beradi", async ({ page }) => {
  // WCAG 2.4.1 — o'lchandi: usiz mazmunga yetish uchun yigirmadan ortiq
  // yon menyu havolasini Tab bilan kesib o'tish kerak edi, HAR sahifada.
  await page.goto("/problems");
  await page.keyboard.press("Tab");

  const skip = page.locator("a[href='#main']");
  await expect(skip).toBeFocused();
  await expect(skip).toBeVisible(); // fokusda ko'rinadi
});
