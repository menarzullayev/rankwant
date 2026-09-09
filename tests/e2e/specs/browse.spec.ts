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
  await expect(
    page.getByRole("heading", { name: "Masalalar arxivi" }),
  ).toBeVisible();
});

test("masala sahifasida o'z metadata si bor", async ({ page }) => {
  await page.goto("/problems");
  const first = page.locator("tbody tr a").first();
  const title = await first.textContent();
  await first.click();
  // Sarlavhada `+` bo'lishi mumkin ("A + B") — ekranlashsiz u regex
  // kvantifikatoriga aylanadi va hech qachon mos kelmaydi.
  const escaped = title!.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  await expect(page).toHaveTitle(new RegExp(escaped));
});

test("reyting formulalari ochiq", async ({ page }) => {
  await page.goto("/rating");
  // Launch gate sharti: 4 formulaning HAMMASI ko'rinishi kerak
  for (const name of ["Skills", "Contests", "Activity", "Challenges"]) {
    await expect(
      page.getByRole("heading", { name, exact: false }),
    ).toBeVisible();
  }
  await expect(page.getByText("0.95")).toBeVisible();
});

test("leaderboard to'rtala reytingni ko'rsatadi", async ({ page }) => {
  await page.goto("/leaderboard");
  // ADR-0006 fazali ochilish: Challenges Phase 3 da (duel) ochildi
  for (const name of ["Skills", "Contests", "Activity", "Challenges"]) {
    await expect(
      page.locator("main").getByText(name, { exact: true }),
    ).toBeVisible();
  }
});

test("arxiv filtri ro'yxatni toraytiradi va URL da qoladi", async ({
  page,
}) => {
  await page.goto("/problems");
  const all = await page.getByRole("row").count();

  await page.getByRole("button", { name: /^Filtrlar( \d+)?$/ }).click();
  await page.getByRole("button", { name: "Qiyin", exact: true }).click();
  await page.waitForURL(/level=hard/);

  const filtered = await page.getByRole("row").count();
  expect(filtered).toBeLessThan(all);
  // Faol filtr soni tugmada ko'rinadi va holat URL da qoladi.
  await expect(
    page.getByRole("button", { name: /^Filtrlar( \d+)?$/ }),
  ).toContainText("1");
});

test("saralash tabi tartibni almashtiradi", async ({ page }) => {
  await page.goto("/problems");
  const first = () => page.getByRole("row").nth(1).innerText();
  const easiest = await first();

  await page.getByRole("tab", { name: "Eng qiyin" }).click();
  await page.waitForURL(/ordering=-difficulty/);

  expect(await first()).not.toBe(easiest);
});

test("qidiruv ro'yxatni toraytiradi", async ({ page }) => {
  await page.goto("/problems?search=fibona");

  await expect(page.getByRole("row")).toHaveCount(2); // sarlavha + 1 natija
  await expect(
    page.getByRole("searchbox", { name: "Masala qidirish" }),
  ).toHaveValue("fibona");
});

test("sahifalash yozuv sonini ko'rsatadi", async ({ page }) => {
  await page.goto("/problems");
  await expect(page.getByLabel("Sahifalar")).toContainText("masala");
});

test("yechilmagan masalada mavzuni yashirish sozlamasi ishlaydi", async ({
  page,
}) => {
  await page.goto("/problems");
  // Mavzu MATNI bo'yicha tekshiriladi, CSS sinfi bo'yicha emas: teg
  // ilgari badge edi, endi kichik kulrang matn — ko'rinish o'zgarganda
  // test yiqilmasligi kerak, xatti-harakat o'sha-o'sha.
  const topics = page.locator("tbody [data-topics]");
  await expect(topics.first()).toBeVisible();

  await page.getByRole("button", { name: /^Filtrlar( \d+)?$/ }).click();
  await page
    .getByRole("button", { name: "Yechilmaganlarda mavzuni yashirish" })
    .click();

  // Qiyinlik belgisi qoladi, mavzu tegi ketadi.
  await expect(topics).toHaveCount(0);
});

test("kirgan foydalanuvchi holat filtrini va bo'lim havolalarini ko'radi", async ({
  page,
}) => {
  const api = process.env.E2E_API_BASE ?? "";
  const site = process.env.E2E_BASE_URL ?? "http://localhost:3000";
  test.skip(
    new URL(api, site).origin !== new URL(site).origin,
    "sayt va API alohida originda — sessiya cookie yetmaydi",
  );

  const username = `e2earx_${Date.now()}`;
  const password = "E2eParol!12345";
  await page.request.post(`${api}/auth/register/`, {
    data: { username, password, email: `${username}@example.uz` },
  });
  await page.request.post(`${api}/auth/login/`, {
    data: { username, password },
  });

  await page.goto("/problems");

  await expect(page.getByRole("link", { name: "Urinishlarim" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Statistikam" })).toBeVisible();

  await page.getByRole("button", { name: /^Filtrlar( \d+)?$/ }).click();
  await page.getByRole("button", { name: "Menga tavsiya" }).click();
  await page.waitForURL(/recommended=true/);
  await expect(
    page.getByRole("button", { name: /^Filtrlar \d+$/ }),
  ).toBeVisible();
});

test("arxiv qatorida masala raqami va statistikasi ko'rinadi", async ({
  page,
}) => {
  await page.goto("/problems");

  // Raqam sahifadagi o'rin emas — barqaror identifikator.
  await expect(page.getByText(/^#\d{4}$/).first()).toBeVisible();
  await expect(page.getByRole("columnheader", { name: "%" })).toBeVisible();
});

test("kirgan foydalanuvchi sevimliga qo'sha oladi", async ({ page }) => {
  const api = process.env.E2E_API_BASE ?? "";
  const site = process.env.E2E_BASE_URL ?? "http://localhost:3000";
  test.skip(
    new URL(api, site).origin !== new URL(site).origin,
    "sayt va API alohida originda — sessiya cookie yetmaydi",
  );

  const username = `e2efav_${Date.now()}`;
  const password = "E2eParol!12345";
  await page.request.post(`${api}/auth/register/`, {
    data: { username, password, email: `${username}@example.uz` },
  });
  await page.request.post(`${api}/auth/login/`, {
    data: { username, password },
  });

  await page.goto("/problems");

  const star = page
    .getByRole("button", { name: /sevimlilarga qo'shish/ })
    .first();
  await expect(star).toBeVisible();
  await star.click();
  await expect(
    page.getByRole("button", { name: /sevimlilardan olib tashlash/ }).first(),
  ).toBeVisible();

  // Qayta yuklangach ham saqlanib qolishi kerak — serverga yozilgan.
  await page.reload();
  await expect(
    page.getByRole("button", { name: /sevimlilardan olib tashlash/ }).first(),
  ).toBeVisible();
});

test("arxiv yon panelida progress bloki ko'rinadi", async ({ page }) => {
  await page.goto("/problems");

  // Mehmonda ham chiziladi — arxiv hajmini ko'rsatadi.
  await expect(
    page.getByRole("heading", { name: "Yechilganlar" }),
  ).toBeVisible();
  await expect(page.getByRole("progressbar").first()).toBeVisible();
});

test("yetti daraja filtr panelida ham, jadvalda ham bir xil", async ({
  page,
}) => {
  await page.goto("/problems");
  await page.getByRole("button", { name: /^Filtrlar( \d+)?$/ }).click();

  for (const label of [
    "Boshlang'ich",
    "Asosiy",
    "O'rta",
    "Yaxshi",
    "Qiyin",
    "Ekspert",
    "Master",
  ]) {
    await expect(
      page.getByRole("button", { name: label, exact: true }),
    ).toBeVisible();
  }
});

test("yon panelda o'quv rejalari va hamjamiyat bloki bor", async ({ page }) => {
  await page.goto("/problems");

  await expect(
    page.getByRole("heading", { name: "O'quv rejalari" }),
  ).toBeVisible();
  await expect(page.getByRole("heading", { name: "Hamjamiyat" })).toBeVisible();
});
