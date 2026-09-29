/**
 * Forma sxemalari — zod.
 *
 * Nima uchun: tekshiruv ilgari komponent ichida qo'lda yozilgan edi
 * (`emailStatus`, `password !== password2` shoxlari). Uch muammo bor edi:
 *
 *   1. Bir xil qoida ikki joyda — kirish formasi va parol tiklash formasi
 *      «parollar mos kelsin» ni alohida-alohida tekshirardi.
 *   2. Tekshiruv React'siz sinalmasdi, ya'ni unga test yozib bo'lmasdi.
 *   3. DRF `min_length=8` va `terms_accepted` shartlari serverda bor edi,
 *      lekin mijozda aks ettirilmagan — odam butun formani to'ldirib,
 *      oxirida xato ko'rardi.
 *
 * ⚠️ Bu sxemalar SERVERNI ALMASHTIRMAYDI. Server har doim qayta
 * tekshiradi (ADR-0003: qoida serverda). Bu yerdagi vazifa — odamga
 * xatoni ERTA ko'rsatish, ya'ni maydonni to'ldirib bo'lgach kutmaslik.
 *
 * ⚠️ Xato MATNI bu yerda YO'Q. Sxema faqat KALIT qaytaradi
 * (`auth.passwordMismatch`), matn esa `t(locale, key)` orqali olinadi —
 * aks holda 10 til uchun 10 nusxa sxema bo'lardi.
 */

import { z } from "zod";

/** Xato kaliti — `t()` ga uzatiladigan i18n kaliti. */
export type RuleKey =
  | "auth.emailInvalid"
  | "auth.passwordHint"
  | "auth.passwordMismatch"
  | "auth.termsRequired"
  | "auth.required"
  | "auth.usernameRequired"
  | "auth.usernameInvalid"
  | "submit.sourceRequired"
  | "submit.sourceTooLong";

/** Maydon nomi → xato kaliti. `null` — xato yo'q. */
export type FieldErrors<K extends string> = Partial<Record<K, RuleKey>>;

//: Parolning eng kam uzunligi — DRF `min_length` bilan BIR XIL bo'lishi
//: shart, aks holda mijoz «yaroqli» deydi-yu server rad etadi.
export const PASSWORD_MIN = 8;

//: Email naqshi. Ataylab QATTIQ EMAS: `a@b.co` o'tsin, `a@b` o'tmasin.
//: To'liq RFC 5322 ni tekshirish 6 KB regex olib keladi va baribir
//: haqiqiy emailni kafolatlamaydi — buni faqat xat yuborish aniqlaydi.
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

/** Kirish/ro'yxat formasi. */
export const authSchema = z
  .object({
    /** Kirishda — taxallus YOKI email (4-qaror); ro'yxatda — email. */
    identifier: z.string().trim().min(1, "auth.required"),
    email: z.string().trim().min(1, "auth.required"),
    password: z.string().min(1, "auth.required"),
    password2: z.string(),
    terms_accepted: z.boolean(),
  })
  .superRefine((value, ctx) => {
    if (value.email && !EMAIL.test(value.email)) {
      ctx.addIssue({ code: "custom", path: ["email"], message: "auth.emailInvalid" });
    }
    if (value.password && value.password.length < PASSWORD_MIN) {
      ctx.addIssue({ code: "custom", path: ["password"], message: "auth.passwordHint" });
    }
    if (value.password2 && value.password !== value.password2) {
      ctx.addIssue({
        code: "custom",
        path: ["password2"],
        message: "auth.passwordMismatch",
      });
    }
    if (!value.terms_accepted) {
      ctx.addIssue({
        code: "custom",
        path: ["terms_accepted"],
        message: "auth.termsRequired",
      });
    }
  });

/**
 * Kirish yoki ro'yxatdan o'tish — REJIMGA qarab.
 *
 * ⚠️ Nega alohida: kirishda email va rozilik umuman so'ralmaydi, lekin
 * `authSchema` ularni talab qiladi. Ilgari chaqiruvchi bo'sh maydonlarga
 * soxta qiymat qo'yardi (`email: "a@b.co"`) — bu ishlaydi, LEKIN
 * (a) qattiq yozilgan matn sifatida `check_hardcoded` ni yiqitadi va
 * (b) sxemani "nima tekshirilayotgani" haqida yolg'on gapiradi: o'qigan
 * odam email HAQIQATAN tekshiriladi deb o'ylaydi.
 *
 * Bu yerda niyat ochiq yoziladi: qaysi maydon qaysi rejimda majburiy.
 */
export const loginSchema = z
  .object({
    identifier: z.string().trim().min(1, "auth.required"),
    password: z.string().min(1, "auth.required"),
  })
  .superRefine(() => {});

export const registerSchema = authSchema;

/** Rejimga qarab to'g'ri sxemani beradi. */
export function authSchemaFor(mode: "login" | "register") {
  return mode === "register" ? registerSchema : loginSchema;
}

/** Parolni tiklash — yangi parol qo'yish (token xatdan keladi). */
export const resetSchema = z
  .object({
    password: z.string().min(1, "auth.required"),
    password2: z.string(),
  })
  .superRefine((value, ctx) => {
    if (value.password && value.password.length < PASSWORD_MIN) {
      ctx.addIssue({ code: "custom", path: ["password"], message: "auth.passwordHint" });
    }
    if (value.password !== value.password2) {
      ctx.addIssue({
        code: "custom",
        path: ["password2"],
        message: "auth.passwordMismatch",
      });
    }
  });

/** Parolni tiklash — havola so'rash. */
export const resetRequestSchema = z.object({
  login: z.string().trim().min(1, "auth.required"),
});

/**
 * Sozlamalar — parolni almashtirish.
 *
 * `old_password` bu yerda QISQA tekshiriladi, chunki uning qoidasi —
 * «to'g'rimi yoki yo'q» — faqat serverda ma'lum. Mijoz uni uzunlikka
 * qarab baholay olmaydi.
 */
export const passwordChangeSchema = z
  .object({
    old_password: z.string(),
    new_password: z.string().min(1, "auth.required"),
    confirm: z.string(),
  })
  .superRefine((value, ctx) => {
    if (value.new_password && value.new_password.length < PASSWORD_MIN) {
      ctx.addIssue({
        code: "custom",
        path: ["new_password"],
        message: "auth.passwordHint",
      });
    }
    if (value.new_password !== value.confirm) {
      ctx.addIssue({
        code: "custom",
        path: ["confirm"],
        message: "auth.passwordMismatch",
      });
    }
  });

//: Taxallus: lotin harf/raqam/pastki chiziq, 3–30 belgi. `core/usernames.py`
//: bilan BIR XIL — server ham xuddi shu naqshni talab qiladi.
export const USERNAME_MIN = 3;
export const USERNAME_MAX = 30;
const USERNAME = /^[a-zA-Z0-9_]{3,30}$/;

/**
 * Ro'yxatdan o'tishning 2-qadami.
 *
 * Faqat `username` MAJBURIY (3-qaror) — qolgani ixtiyoriy, ya'ni ular
 * bo'sh bo'lsa ham forma o'tadi. Shuning uchun sxema maydonlarni
 * `optional` qiladi va faqat to'ldirilgan qiymatni tekshiradi.
 */
export const onboardingSchema = z.object({
  username: z
    .string()
    .trim()
    .min(1, "auth.usernameRequired")
    .refine((value) => USERNAME.test(value), { message: "auth.usernameInvalid" }),
  display_name: z.string(),
  city: z.string(),
  school: z.string(),
  phone: z.string(),
});

/** Yuboriladigan manba kodi — 64 KB (judge chegarasi bilan bir xil). */
export const SOURCE_MAX_BYTES = 64 * 1024;

/**
 * Masala yechimini yuborish.
 *
 * ⚠️ Hajm BELGILARDA emas, BAYTLARDA o'lchanadi: kirill harf UTF-8 da
 * 2 bayt, emoji 4 bayt. Belgilar bo'yicha sanash 64 KB chegarani
 * yolg'on hisoblab, serverning 413 javobiga olib kelardi.
 */
export const sourceSchema = z.object({
  source: z.string().trim().min(1, "submit.sourceRequired"),
  bytes: z.number().max(SOURCE_MAX_BYTES, "submit.sourceTooLong"),
});

/**
 * Natijani maydon → kalit jadvaliga aylantiradi.
 *
 * ⚠️ `safeParse` ishlatiladi, `parse` EMAS: `parse` istisno tashlaydi va
 * uni forma ichida `try/catch` bilan o'rash kerak bo'lardi — natija esa
 * baribir bir xil obyekt. Bu yerdagi shakl React'ga qulay:
 * `errors.email && <p>{t(locale, errors.email)}</p>`.
 */
export function fieldErrors<K extends string>(
  result: z.ZodSafeParseResult<unknown>,
): FieldErrors<K> {
  if (result.success) return {};
  const out: FieldErrors<K> = {};
  for (const issue of result.error.issues) {
    const path = issue.path[0];
    if (typeof path !== "string") continue;
    //: Bir maydonda birinchi xato yetarli — ikkinchisini ko'rsatish
    //: odamni chalg'itadi (masalan «juda qisqa» va «raqamlardan iborat»).
    if (out[path as K] === undefined) {
      out[path as K] = issue.message as RuleKey;
    }
  }
  return out;
}
