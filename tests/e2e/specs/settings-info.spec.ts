import { expect, test } from "@playwright/test";

import { skipUnlessLocal } from "./guard";

/**
 * Settings save the fields added in ADR-0024, and the phone number that the
 * "Ma'lumotlar" form showed but never sent (fixed 2026-09-18).
 *
 * Like the signed-in test in `submit-ui.spec.ts`, it needs the site and the
 * API on one origin: the CI stand serves them apart, so it is skipped there.
 */

const API = process.env.E2E_API_BASE ?? "http://localhost:8000/api/v1";
const SITE = process.env.E2E_BASE_URL ?? "http://localhost:3000";
const sameOrigin = new URL(API, SITE).origin === new URL(SITE).origin;

test("ma'lumotlar va profil formasi yangi maydonlarni saqlaydi", async ({ page }) => {
  skipUnlessLocal();
  test.skip(!sameOrigin, "sayt va API alohida originda — sessiya cookie yetmaydi");

  const username = `e2einfo_${Date.now()}`;
  const password = "E2eParol!12345";
  const register = await page.request.post(`${API}/auth/register/`, {
    data: { username, password, email: `${username}@example.uz`, terms_accepted: true },
  });
  expect(register.ok()).toBeTruthy();
  const login = await page.request.post(`${API}/auth/login/`, {
    data: { identifier: username, password },
  });
  expect(login.ok()).toBeTruthy();

  const me = async () => (await page.request.get(`${API}/me/`)).json();

  await page.goto("/settings/malumotlar");
  const info = page.locator('form:has(input[name="phone"])');
  await info.locator('input[name="phone"]').fill("+998 90 123 45 67");
  await info.locator('select[name="grade"]').selectOption("b2");
  await info.locator('select[name="shirt_size"]').selectOption("L");
  await info.locator('button[type="submit"]').click();
  await expect
    .poll(async () => {
      const row = await me();
      return [row.phone, row.grade, row.shirt_size];
    })
    .toEqual(["+998901234567", "b2", "L"]);

  await page.goto("/settings/profil");
  const profile = page.locator('form:has(input[name="first_name"])');
  await profile.locator('input[name="first_name"]').fill("Ali");
  await profile.locator('input[name="last_name"]').fill("Valiyev");
  await profile.locator('button[type="submit"]').click();
  await expect
    .poll(async () => {
      const row = await me();
      return [row.first_name, row.last_name];
    })
    .toEqual(["Ali", "Valiyev"]);
});
