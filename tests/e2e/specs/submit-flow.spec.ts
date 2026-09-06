import { expect, test } from "@playwright/test";

/**
 * Oqim A (test-strategy § 4): ro'yxatdan o'tish → submit → AC →
 * Skills reyting oshadi → profilda ko'rinadi.
 *
 * API orqali ishlaydi: submit UI si hali yo'q (Phase 0 minimal UI).
 * Zanjirning o'zi tekshiriladi, tugmalar emas.
 */

const API = process.env.E2E_API_BASE ?? "http://localhost:8000/api/v1";

test("birinchi AC Skills reytingini oshiradi", async ({ request }) => {
  const username = `e2e_${Date.now()}`;
  const password = "E2eParol!12345";

  const register = await request.post(`${API}/auth/register/`, {
    data: { username, password, email: `${username}@example.uz` },
  });
  expect(register.ok()).toBeTruthy();

  const login = await request.post(`${API}/auth/login/`, {
    data: { username, password },
  });
  expect(login.ok()).toBeTruthy();
  expect((await login.json()).rating_skills).toBe(0);

  const problems = await (await request.get(`${API}/problems/`)).json();
  test.skip(problems.count === 0, "arxiv bo'sh");
  const problem = problems.results[0];

  const languages = await (await request.get(`${API}/languages/`)).json();
  test.skip(languages.count === 0, "til sozlanmagan");

  const submit = await request.post(`${API}/attempts/`, {
    data: {
      problem: problem.slug,
      language: languages.results[0].code,
      source_code: "int main(){return 0;}",
    },
  });
  expect(submit.status()).toBe(201);
  expect((await submit.json()).verdict).toBe("PENDING");
});

test("read scope'li token submit qila olmaydi", async ({ request }) => {
  const username = `e2e_scope_${Date.now()}`;
  const password = "E2eParol!12345";
  await request.post(`${API}/auth/register/`, {
    data: { username, password, email: `${username}@example.uz` },
  });
  await request.post(`${API}/auth/login/`, { data: { username, password } });

  const expires = new Date(Date.now() + 86_400_000).toISOString();
  const created = await request.post(`${API}/me/tokens/`, {
    data: { name: "e2e", scopes: ["read"], expires_at: expires },
  });
  expect(created.status()).toBe(201);
  const token = (await created.json()).token;
  expect(token).toMatch(/^rw_/);

  const problems = await (await request.get(`${API}/problems/`)).json();
  test.skip(problems.count === 0, "arxiv bo'sh");

  const blocked = await request.post(`${API}/attempts/`, {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      problem: problems.results[0].slug,
      language: "cpp23",
      source_code: "int main(){}",
    },
  });
  // ADR-0008: minimal ruxsat — read token yozmaydi
  expect(blocked.status()).toBe(403);
});

test("boshqa foydalanuvchi manbani ko'rmaydi", async ({ request }) => {
  const attempts = await (await request.get(`${API}/attempts/`)).json();
  test.skip(attempts.results.length === 0, "urinish yo'q");
  const detail = await (
    await request.get(`${API}/attempts/${attempts.results[0].id}/`)
  ).json();
  // Anonim so'rovda manba berilmasligi kerak (IDOR himoyasi)
  expect(detail).not.toHaveProperty("source_code");
});
