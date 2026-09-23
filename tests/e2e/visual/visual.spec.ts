import { expect, test, type Page } from "@playwright/test";

/**
 * Vizual regressiya — RW-ARCH-016.
 *
 * NEGA ALOHIDA PAPKA: bu testlar `specs/` dan chiqarilgan, chunki ular
 * boshqa shartnoma bo'yicha ishlaydi. `specs/` — "funksiya ishlayaptimi"
 * (matn bor, tugma bosiladi, oqim tugaydi). Bu yerdagi testlar esa
 * "KO'RINISH o'zgarganmi" — ya'ni piksel solishtirish. Ikkalasini bitta
 * papkada aralashtirsak, `npx playwright test` buyrug'i har safar 4 ta
 * brauzer × 6 sahifa skrinshot olib, sekin va shovqinli bo'lardi.
 *
 * ⚠️ `toHaveScreenshot` FAQAT `chromium` da yuritiladi. Brauzerlar
 * shriftlarni, `border-radius` ni va soya silliqlashini boshqacha
 * chizadi — Firefox/WebKit bilan bir xil baseline'ni solishtirish har
 * yurishda yolg'on qizil beradi. Rang/shrift regressiyasini tutish uchun
 * bitta brauzer yetarli; brauzerlararo farqni `specs/` allaqachon
 * funksional darajada qamraydi.
 *
 * ⚠️ ANIMATSIYA O'CHIRILADI. CSS o'tishlar (hover, kirish effektlari)
 * skrinshot paytida yarim holatda bo'lishi mumkin va baseline barqaror
 * bo'lmaydi. `reducedMotion` + `animations: "disabled"` ikkisi birga
 * ishlatiladi.
 *
 * Baseline yangilash (ataylab o'zgargan dizayndan keyin):
 *   npx playwright test --project=visual --update-snapshots
 */

/** Skrinshot barqarorligi uchun umumiy sozlamalar.
 *
 *  `maxDiffPixelRatio` — piksel sonining ulushi. 0 qilinmaydi: matn
 *  joylashuvida bir piksel siljish ham shovqin beradi va darvoza
 *  foydasiz bo'lib qoladi. 0.01 (1%) mazmunli o'zgarishni tutadi.
 *
 *  `threshold` — bitta pikselning rang farqi (YIQ). Antialiasing
 *  chetlari uchun kerak.
 */
const SHOT = {
  animations: "disabled",
  caret: "hide",
  maxDiffPixelRatio: 0.01,
  threshold: 0.2,
} as const;

/** Sahifa barqarorlashguncha kutadi: shriftlar + tarmoq tinchligi. */
async function settle(page: Page): Promise<void> {
  await page.evaluate(() => document.fonts.ready);
  // `networkidle` — SSR'dan keyin klient gidratatsiyasi tugaganini
  // bildiradi. Usiz skrinshot yarim gidratlangan holatni olishi mumkin.
  await page.waitForLoadState("networkidle");
}

test.describe("vizual regressiya", () => {
  test.skip(
    ({ browserName }) => browserName !== "chromium",
    "piksel solishtirish faqat chromium'da barqaror",
  );

  // Ko'rinish cookie'dan keladi; `playwright.config.ts` `uz-UZ` beradi,
  // ya'ni baseline o'zbekcha matn bilan bir xil bo'lib qoladi.

  test("bosh sahifa", async ({ page }) => {
    await page.goto("/");
    await settle(page);
    await expect(page).toHaveScreenshot("home.png", SHOT);
  });

  test("masalalar arxivi", async ({ page }) => {
    await page.goto("/problems");
    await settle(page);
    await expect(page).toHaveScreenshot("problems.png", SHOT);
  });

  test("reyting jadvallari", async ({ page }) => {
    await page.goto("/rating");
    await settle(page);
    await expect(page).toHaveScreenshot("rating.png", SHOT);
  });

  test("kirish sahifasi", async ({ page }) => {
    // `(auth)/login` — alohida layout (`app/auth.css`), ya'ni dizayn
    // tizimining ikkinchi yuzasi: asosiy karkasdan farq qiladi.
    await page.goto("/login");
    await settle(page);
    await expect(page).toHaveScreenshot("login.png", SHOT);
  });

  test("profil sahifasi", async ({ page }) => {
    // Profil — KPI katakchasi `xl` da bosqichma-bosqich o'zgaradi va
    // 300 px yon panel tufayli tor ustunga ega (2026-09-18 qarori).
    // Ya'ni bu eng "nozik" grid sahifasi.
    //
    // ⚠️ USERNAME QATTIQ YOZILMAYDI. Avval `seed_demo` ning "ustoz"
    // nomiga tayanardik — natijada jonli bazada (import qilingan
    // haqiqiy Codeforces hisoblari) 404 sahifasi skrinshot qilinib
    // qoldi, ya'ni baseline profil emas, xato sahifasini qulflab oldi.
    //
    // ⚠️ API'GA UMUMAN MUROJAAT QILINMAYDI. Ilgari `E2E_API_BASE` dan
    // username so'ralardi. CI'da bu ikki marta buzildi:
    //   1. web `baseURL` bilan chaqirilsa 404 (next.config da `rewrites`
    //      yo'q) → test jimgina SKIP;
    //   2. konteyner ichidan `http://rankwant-api-1:8000` → **400**
    //      (`ALLOWED_HOSTS` konteyner nomini bilmaydi) → yana SKIP.
    // Har ikkisi "profil baseline umuman tekshirilmadi" degani.
    //
    // Yechim: username sahifaning O'ZIDAN olinadi — bosh sahifadagi
    // reyting blokidagi profil havolasi (`/users/<name>`), u SSR'da
    // keladi. Web qaysi manzilda bo'lsa ham ishlaydi, qo'shimcha host
    // ruxsati talab qilmaydi.
    //
    // `/rating` sahifasi YARAMAYDI: u klient tomonda renderlanadi, ya'ni
    // SSR HTML'da `/users/` havolasi yo'q (o'lchandi: 0 ta).
    await page.goto("/");
    await settle(page);
    const link = page.locator('a[href^="/users/"]').first();
    if ((await link.count()) === 0) {
      test.skip(true, "bosh sahifada foydalanuvchi havolasi yo'q");
    }
    const href = (await link.getAttribute("href"))!;

    await page.goto(href);
    await settle(page);
    // 404 bo'lsa bu jimgina o'tib ketmasligi kerak — aks holda yana
    // xato sahifasi baseline bo'lib qoladi.
    await expect(page.locator("body")).not.toContainText("Sahifa topilmadi");
    await expect(page).toHaveScreenshot("profile.png", SHOT);
  });

  test("masala sahifasi", async ({ page }) => {
    // Masala sahifasi — Monaco, KaTeX va shart paneli birga. Eng og'ir
    // vizual yuzaki; shrift va o'lcham regressiyasi shu yerda ko'rinadi.
    //
    // ⚠️ Ro'yxat sahifasi BU YERDA qayta olinmaydi: `/problems` allaqachon
    // "masalalar arxivi" testida `problems.png` sifatida qulflangan va
    // o'sha manzil + o'sha `SHOT` sozlamasi bilan olingan surat **bayt-bayt
    // bir xil** chiqadi (o'lchandi: ikkisi ham 118867 bayt, bir xil sha256).
    // Ya'ni u takroriy qoplov edi — olib tashlandi.
    await page.goto("/problems");
    await settle(page);

    const first = page.locator("tbody tr a").first();
    if ((await first.count()) === 0) {
      test.skip(true, "masala arxivi bo'sh");
    }
    const href = await first.getAttribute("href");
    await page.goto(href!);
    await settle(page);
    await expect(page).toHaveScreenshot("problem.png", SHOT);
  });

  test("mobil bosh sahifa", async ({ page }) => {
    // SSR jadvallari va sarlavhalar 390 px da sinadi
    // (`specs/mobile-header.spec.ts` funksional darajada tekshiradi;
    // bu esa ko'rinishni qulflaydi).
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/");
    await settle(page);
    await expect(page).toHaveScreenshot("home-mobile.png", SHOT);
  });
});
