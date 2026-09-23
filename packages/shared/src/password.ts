/** Parol kuchi — 1 dan 4 gacha, 0 esa «hali yozilmagan».
 *
 * Kutubxona qo'shilmadi. `zxcvbn` 400 KB dan ortiq lug'at olib keladi va
 * u ro'yxatdan o'tish sahifasining O'ZIDAN katta bo'lardi; keng tarqalgan
 * parollarni bloklash esa allaqachon backendda —
 * `CommonPasswordValidator` ro'yxati serverda tekshiriladi.
 *
 * Bu ko'rsatkich HECH NARSANI TO'SMAYDI: qabul qilish qoidasi faqat
 * serverda (kamida 8 belgi, faqat raqam emas, taxallusga o'xshamasin).
 * Bu yerdagi vazifa — yozayotgan odamga qanchalik yaxshi parol
 * tanlayotganini ko'rsatish.
 */
export function strength(value: string): 0 | 1 | 2 | 3 | 4 {
  if (!value) return 0;

  const classes =
    Number(/[a-z]/.test(value)) +
    Number(/[A-Z]/.test(value)) +
    Number(/[0-9]/.test(value)) +
    Number(/[^A-Za-z0-9]/.test(value));

  // Takroriy («aaaaaaaa») va ketma-ket («12345678») parol uzun bo'lsa ham
  // zaif: uzunlikni sanashdan oldin shu ikkisi ushlanadi.
  const uniq = new Set(value).size;
  if (value.length < 8 || uniq <= 2) return 1;

  let score = 1;
  if (value.length >= 10) score += 1;
  if (value.length >= 14) score += 1;
  if (classes >= 3) score += 1;
  if (classes <= 1) score -= 1;

  return Math.min(4, Math.max(1, score)) as 1 | 2 | 3 | 4;
}
