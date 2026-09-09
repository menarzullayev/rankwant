import { test } from "@playwright/test";

/** Ro'yxatdan o'tadigan testlar uchun qo'riqchi.
 *
 * Bu testlar haqiqiy hisob yaratadi va o'zidan keyin tozalamaydi. Jonli
 * manzilga qarshi qo'lda yuritilganda ular bazaga chiqindi yozib
 * qo'ygan edi: 178 faol foydalanuvchidan 170 tasi shu yo'l bilan
 * paydo bo'lgan va reyting jadvalini to'ldirib turgan.
 *
 * CI o'z stackida ishlaydi (`web:3000`), ya'ni u to'sib qo'yilmaydi.
 * Ataylab jonli manzilda sinash kerak bo'lsa: `E2E_ALLOW_REMOTE=1`.
 */
const LOCAL = /^https?:\/\/(localhost|127\.0\.0\.1|\[::1\]|web|api)(:|\/|$)/;

export function skipUnlessLocal(): void {
  const base = process.env.E2E_BASE_URL ?? "http://localhost:3000";
  const allowed =
    process.env.E2E_ALLOW_REMOTE === "1" ||
    process.env.CI === "1" ||
    LOCAL.test(base);
  test.skip(
    !allowed,
    `Hisob yaratadigan test ${base} da o'tkazib yuborildi — E2E_ALLOW_REMOTE=1 bilan yuriting`,
  );
}
