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
const SITE = process.env.E2E_BASE_URL ?? "http://localhost:3000";
const PROBLEM = "/problems/a-plus-b";

/**
 * Brauzerda autentifikatsiya faqat sayt va API bitta originda bo'lganda
 * ishlaydi: `SESSION_COOKIE_SAMESITE=Lax` cross-site so'rovda cookie
 * yubormaydi. Productionda tunnel `/api/*` ni o'sha originda beradi
 * (ADR-0008), CI stendi esa `web:3000` va `api:8000` ni alohida
 * ko'taradi — o'sha yerda bu tekshiruv o'tkazib yuboriladi.
 */
const sameOrigin = new URL(API, SITE).origin === new URL(SITE).origin;

test("mehmonga panel ko'rinadi, lekin yuborish kirishni talab qiladi", async ({
  page,
}) => {
  await page.goto(PROBLEM);

  await expect(page.getByRole("heading", { name: "Yechim" })).toBeVisible();
  // Tillar serverda olinadi — mehmon ham ko'radi (SSR).
  await expect(page.getByRole("combobox", { name: /|/ }).first()).toContainText(
    /C\+\+|Python|Java/,
  );
  await expect(
    page.getByRole("link", { name: "Yuborish uchun kiring" }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Yuborish" })).toHaveCount(0);
});

test("kirgan foydalanuvchi yuborish va sinab ko'rishni oladi", async ({
  page,
}) => {
  test.skip(
    !sameOrigin,
    "sayt va API alohida originda — sessiya cookie yetmaydi",
  );

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
    page.getByRole("button", { name: "Namunada sinash" }),
  ).toBeVisible();
  // Urinishlar sahifa tepasidagi bo'limga ko'chdi — panelda faqat ishchi
  // tablar qoldi.
  await expect(page.getByRole("button", { name: /^Urinishlar/ })).toHaveCount(
    0,
  );

  await page.getByRole("button", { name: "O'z testim" }).click();
  await expect(
    page.getByRole("button", { name: "Ishga tushirish" }),
  ).toBeVisible();
});

test("musobaqadan kelgan havola kontekstni ko'rsatadi", async ({ page }) => {
  await page.goto(`${PROBLEM}?contest=demo-contest`);
  await expect(page.getByText(/musobaqasi hisobiga yoziladi/)).toBeVisible();
});

test("namunalar kirish va chiqish bilan ko'rinadi", async ({ page }) => {
  await page.goto(PROBLEM);

  const samples = page.getByRole("heading", { name: "Namunalar" });
  await expect(samples).toBeVisible();
  // Namuna matni SSR ga kiradi — qidiruv ham, mehmon ham ko'radi.
  await expect(page.getByText("Kirish", { exact: true }).first()).toBeVisible();
  await expect(
    page.getByRole("button", { name: /namuna kirishini nusxalash/ }).first(),
  ).toBeVisible();
});

test("masala sahifasida ommaviy raqam ko'rinadi", async ({ page }) => {
  await page.goto(PROBLEM);

  await expect(page.getByText(/^#\d{4}$/)).toBeVisible();
  // Sarlavhada ham — qidiruv natijasida masalani raqami bilan tanish uchun.
  await expect(page).toHaveTitle(/#\d{4}/);
});

test("bo'lim tablari sahifalar orasida yuradi", async ({ page }) => {
  await page.goto(PROBLEM);

  // Yon menyuda ham «Urinishlar» havolasi bor — bo'lim navigatsiyasi
  // bilan cheklaymiz.
  const tabs = page.getByRole("navigation", { name: "Masala bo'limlari" });

  await tabs.getByRole("link", { name: "Urinishlar" }).click();
  await page.waitForURL(/\/status$/);
  await expect(
    page.getByRole("columnheader", { name: "Foydalanuvchi" }),
  ).toBeVisible();
  // Begonaga manba ko'rinmasligi kerak — jadvalda umuman ustun yo'q.
  await expect(
    page.getByRole("columnheader", { name: /manba|source/i }),
  ).toHaveCount(0);

  await tabs.getByRole("link", { name: "Statistika" }).click();
  await page.waitForURL(/\/stats$/);
  await expect(page.getByRole("heading", { name: "Verdiktlar" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Tillar" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Yechganlar" })).toBeVisible();

  await tabs.getByRole("link", { name: "Tavsif" }).click();
  await page.waitForURL(/\/problems\/[^/]+$/);
  await expect(page.getByRole("heading", { name: "Yechim" })).toBeVisible();
});
