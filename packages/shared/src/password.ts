/** Parol kuchi — 1 dan 5 gacha, 0 esa «hali yozilmagan».
 *
 * Kutubxona qo'shilmadi. `zxcvbn` 400 KB dan ortiq lug'at olib keladi va
 * u ro'yxatdan o'tish sahifasining O'ZIDAN katta bo'lardi; keng tarqalgan
 * parollarni bloklash esa backendda — `CommonPasswordValidator` ro'yxati
 * serverda tekshiriladi.
 *
 * Bu ko'rsatkich HECH NARSANI TO'SMAYDI: qabul qilish qoidasi faqat
 * serverda. Vazifa — yozayotgan odamga qanchalik yaxshi parol tanlayotganini
 * ko'rsatish. Shu sababli u serverning rad qoidalariga BO'YSUNADI: server
 * rad etadigan (qisqa, faqat raqam, takroriy, keng tarqalgan) parol hech
 * qachon «zaif»dan yuqori ko'rsatilmaydi — yolg'on «kuchli» chiqmasin.
 *
 * Beshta daraja (2026-10-26): 1 juda zaif · 2 zaif · 3 o'rtacha · 4 yaxshi ·
 * 5 kuchli. */

export type Strength = 0 | 1 | 2 | 3 | 4 | 5;

/** Serverdagi `CommonPasswordValidator` ro'yxatining eng ko'p uchraydigan
 *  qismi. To'liq ro'yxat serverda; bu yerdagisi faqat ko'rsatkichni
 *  ishonchsiz «kuchli»ga chiqarmaslik uchun. */
const COMMON = new Set([
  "password",
  "password1",
  "passw0rd",
  "qwertyuiop",
  "qwerty123",
  "qwerty12345",
  "iloveyou",
  "admin123",
  "welcome1",
  "letmein1",
  "parol123",
  "parol1234",
  "uzbekistan",
  "12345678",
  "123456789",
  "1234567890",
]);

/** Parol minimal qoidalardan o'tadimi (ro'yxatdagi uch band). */
export function passwordRules(value: string): {
  length: boolean;
  notNumeric: boolean;
  varied: boolean;
} {
  return {
    length: value.length >= 8,
    notNumeric: value.length > 0 && !/^\d+$/.test(value),
    varied: new Set(value).size > 2,
  };
}

export function strength(value: string): Strength {
  if (!value) return 0;

  const rules = passwordRules(value);
  if (!rules.length || !rules.notNumeric || !rules.varied) return 1;
  if (COMMON.has(value.toLowerCase())) return 1;

  const classes =
    Number(/[a-z]/.test(value)) +
    Number(/[A-Z]/.test(value)) +
    Number(/[0-9]/.test(value)) +
    Number(/[^A-Za-z0-9]/.test(value));

  const lengthPoints = value.length >= 16 ? 3 : value.length >= 12 ? 2 : 1;
  const classPoints = classes === 4 ? 2 : classes === 3 ? 1 : 0;
  // 1..5 → daraja. Faqat harflardan iborat sakkiz belgi — «zaif».
  const level = [0, 2, 3, 3, 4, 5][lengthPoints + classPoints] as Strength;
  return level;
}
