import { defineConfig, devices } from "@playwright/test";

/**
 * E2E — test-strategy.md § 4.
 *
 * Bu testlar ISHLAYOTGAN stack'ni talab qiladi (API + web + judge).
 * CI da compose stack'iga qarshi ishlaydi (`docker-compose.ci.yml`),
 * staging kutilmaydi.
 */
export default defineConfig({
  testDir: "./specs",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false, // reyting va streak holati ketma-ket bo'lishi kerak
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    // ⚠️ BU QATOR BO'LMASA TESTLAR YIQILADI.
    //
    // Til cookie'dan (`rw_locale`) yoki `Accept-Language` dan keladi.
    // Playwright brauzeri standart holatda `en-US` yuboradi, ya'ni server
    // sahifani INGLIZCHA qaytaradi — `<html lang="en">`, "Problem archive".
    // Testlar esa o'zbekcha matn kutadi ("Masalalar arxivi") va 32 tasi
    // birinchi yugurishda aynan shu sababdan yiqildi (run 34904632282).
    //
    // `uz-UZ` qo'yilsa brauzer shuni yuboradi va server `uz` ga o'tadi.
    locale: "uz-UZ",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  // Brauzer matritsasi — test-strategy § 15 compatibility.
  // Mobil viewport alohida: SSR jadvallari tor ekranda sinadi.
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
});
