import { defineConfig, devices } from "@playwright/test";

/**
 * E2E — test-strategy.md § 4.
 *
 * Bu testlar ISHLAYOTGAN stack'ni talab qiladi (API + web + judge).
 * CI da compose stack'iga qarshi ishlaydi (`docker-compose.ci.yml`),
 * staging kutilmaydi.
 */
export default defineConfig({
  testDir: "./",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false, // reyting va streak holati ketma-ket bo'lishi kerak
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? "github" : "list",
  // ⚠️ PLATFORMA SUFFIKSI OLIB TASHLANDI — baseline'lar BITTA muhitniki.
  //
  // Playwright sukutda baseline nomiga platformani qo'shadi
  // (`home-visual-win32.png`). Ya'ni nom allaqachon "qaysi OS'da olingan"
  // degan ma'noni beradi va shu bilan ko'p-muhitli yurishni JIMGINA
  // buzadi: Windows'da olingan baseline CI'da (Linux) topilmay, har
  // skrinshot "snapshot doesn't exist" berib yiqilardi.
  //
  // ⚠️ 2026-09-24 O'LCHANDI: "shrift qulflangan, 1% shovqinni yutadi"
  // degan umid NOTO'G'RI edi. Linux konteynerida 6/6 sahifa **3–4%**
  // farq berdi (`maxDiffPixelRatio: 0.01` dan katta). Diff rasmda butun
  // matn qizil — ya'ni sabab shrink ANTIALIASING/hinting, layout emas.
  // Konteynerda faqat 50 ta shrift bor (`FreeSans`, `DejaVu`...); web
  // esa `Inter`/sistema shriftlarini ishlatadi va ular Linux'da YO'Q.
  //
  // XULOSA: bitta baseline ikki OS'ga yaramaydi, `maxDiffPixelRatio`
  // ni ko'tarish esa haqiqiy regressiyani ham yutib yuborardi.
  // Qabul qilingan yo'l (Saidakbar aka tasdig'i, 2026-09-24):
  // **baseline'lar CI muhitida (Linux konteyneri) olinadi va commit
  // qilinadi — CI yagona haqiqat.** Lokal Windows'da vizual suite shu
  // sababdan qizil beradi; bu normal, Windows'da baseline YARATILMAYDI.
  //
  // Baseline yangilash (CI muhitida, Windows'da emas):
  //   MSYS_NO_PATHCONV=1 docker run --rm --network rankwant_default \
  //     -v "<repo>/tests/e2e:/e2e" -w /e2e \
  //     -e E2E_BASE_URL=http://host.docker.internal:3400 -e CI=1 \
  //     mcr.microsoft.com/playwright:v1.63.0-noble \
  //     npx playwright test --project=visual --update-snapshots
  //
  // ⚠️ Agar kelajakda CI'da boshqa image ishlatilsa, baseline'lar
  // o'sha image'da qayta olinishi SHART.
  snapshotPathTemplate: "{testDir}/{testFilePath}-snapshots/{arg}{ext}",
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
    //
    // ⚠️ Vizual testlar ham shunga TAYANADI: baseline o'zbekcha matn bilan
    // olingan, ya'ni bu qiymat o'zgarsa `visual` proyekti qizaradi.
    locale: "uz-UZ",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  // Brauzer matritsasi — test-strategy § 15 compatibility.
  // Mobil viewport alohida: SSR jadvallari tor ekranda sinadi.
  //
  // ⚠️ `testDir` endi `./` (ilgari `./specs`): `visual/` shu config ostida
  // alohida PROYEKT sifatida yurishi kerak, aks holda uning 4 ta brauzer
  // uchun skrinshot oladigan testlari oddiy `e2e` yurishiga aralashib
  // ketadi. Har proyekt `testMatch` bilan chegaralangan.
  projects: [
    {
      name: "e2e",
      testIgnore: /visual\//,
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      testIgnore: /visual\//,
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      testIgnore: /visual\//,
      use: { ...devices["Desktop Safari"] },
    },
    {
      name: "mobile",
      testIgnore: /visual\//,
      use: { ...devices["Pixel 7"] },
    },
    // ── RW-ARCH-016: vizual regressiya ──────────────────────────────────
    //
    // Faqat chromium: brauzerlar shrift va soyalarni boshqacha chizadi,
    // ya'ni yagona baseline ular orasida ishlamaydi. Brauzerlararo
    // farqni `e2e`/`firefox`/`webkit` funksional darajada qamraydi.
    {
      name: "visual",
      testMatch: /visual\/.*\.spec\.ts$/,
      use: {
        ...devices["Desktop Chrome"],
        // Yarim holatdagi animatsiya skrinshotni beqaror qiladi.
        reducedMotion: "reduce",
      },
    },
  ],
});
