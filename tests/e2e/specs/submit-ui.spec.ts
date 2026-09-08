import { expect, test } from "@playwright/test";

/**
 * Submit oynasi — asosiy oqim shu yerdan boshlanadi.
 *
 * Monaco ichiga yozish testda mo'rt (CDN dan yuklanadi, virtual DOM),
 * shuning uchun bu yerda simlar tekshiriladi: panel chiqadimi, tillar
 * keldimi, va yuborish huquqi holatga qarab to'g'ri ko'rinadimi.
 * Kod → verdikt zanjiri `submit-flow.spec.ts` da API orqali sinaladi.
 */

const API = process.env.E2E_API_BASE ?? "http://localhost:8000/api/v1";
const PROBLEM = "/problems/a-plus-b";

test("mehmonga panel ko'rinadi, lekin yuborish kirishni talab qiladi", async ({
  page,
}) => {
  await page.goto(PROBLEM);

  await expect(page.getByRole("heading", { name: "Yechim" })).toBeVisible();
  // Tillar serverda olinadi — mehmon ham ko'radi (SSR).
  await expect(
    page.getByRole("combobox", { name: /|/ }).first(),
  ).toContainText(/C\+\+|Python|Java/);
  await expect(
    page.getByRole("link", { name: "Yuborish uchun kiring" }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Yuborish" })).toHaveCount(0);
});

test("kirgan foydalanuvchi yuborish va sinab ko'rishni oladi", async ({
  page,
}) => {
  const username = `e2eui_${Date.now()}`;
  const password = "E2eParol!12345";

  // `page.request` brauzer konteksti bilan bir xil cookie idishidan
  // foydalanadi, ya'ni sessiya keyingi `goto` da ham amal qiladi.
  const register = await page.request.post(`${API}/auth/register/`, {
    data: { username, password, email: `${username}@example.uz` },
  });
  expect(register.ok()).toBeTruthy();
  const login = await page.request.post(`${API}/auth/login/`, {
    data: { username, password },
  });
  expect(login.ok()).toBeTruthy();

  await page.goto(PROBLEM);

  await expect(page.getByRole("button", { name: "Yuborish" })).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Sinab ko'rish" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Urinishlar/ }),
  ).toBeVisible();
});

test("musobaqadan kelgan havola kontekstni ko'rsatadi", async ({ page }) => {
  await page.goto(`${PROBLEM}?contest=demo-contest`);
  await expect(page.getByText(/musobaqasi hisobiga yoziladi/)).toBeVisible();
});
