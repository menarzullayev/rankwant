/**
 * `lib/validation.ts` — forma sxemalari.
 *
 * Nega test: sxema ilgari komponent ichida qo'lda yozilgan edi va unga
 * test yozib bo'lmasdi. Endi u SOF funksiya, ya'ni har qoida alohida
 * o'lchanadi. Salbiy tekshiruv: har bir `min`/`superRefine` shartini
 * buzib, xato HAQIQATAN chiqishini ko'rsatamiz.
 */

import { describe, expect, it } from "vitest";

import {
  PASSWORD_MIN,
  SOURCE_MAX_BYTES,
  USERNAME_MAX,
  USERNAME_MIN,
  authSchema,
  authSchemaFor,
  fieldErrors,
  loginSchema,
  onboardingSchema,
  passwordChangeSchema,
  registerSchema,
  resetRequestSchema,
  resetSchema,
  sourceSchema,
} from "../src/validation/index";

describe("authSchema — email", () => {
  const base = {
    identifier: "kim",
    email: "a@b.co",
    password: "parol123",
    password2: "parol123",
    terms_accepted: true,
  };

  it("to'g'ri email o'tadi", () => {
    expect(authSchema.safeParse(base).success).toBe(true);
  });

  it("nuqtasiz domen rad etiladi", () => {
    const r = authSchema.safeParse({ ...base, email: "a@b" });
    expect(r.success).toBe(false);
    expect(fieldErrors(r).email).toBe("auth.emailInvalid");
  });

  it("bo'shliqli email rad etiladi", () => {
    const r = authSchema.safeParse({ ...base, email: "a b@c.co" });
    expect(fieldErrors(r).email).toBe("auth.emailInvalid");
  });

  it("ko'p nuqtali domen o'tadi", () => {
    expect(authSchema.safeParse({ ...base, email: "a@b.co.uz" }).success).toBe(true);
  });
});

describe("authSchema — parol", () => {
  const base = {
    identifier: "kim",
    email: "a@b.co",
    password: "parol123",
    password2: "parol123",
    terms_accepted: true,
  };

  it(`${PASSWORD_MIN} dan qisqa parol rad etiladi`, () => {
    const r = authSchema.safeParse({ ...base, password: "p".repeat(PASSWORD_MIN - 1) });
    expect(fieldErrors(r).password).toBe("auth.passwordHint");
  });

  it(`aynan ${PASSWORD_MIN} belgi QABUL qilinadi (chegara)`, () => {
    const p = "p".repeat(PASSWORD_MIN);
    expect(authSchema.safeParse({ ...base, password: p, password2: p }).success).toBe(true);
  });

  it("mos kelmagan parol rad etiladi", () => {
    const r = authSchema.safeParse({ ...base, password2: "boshqa123" });
    expect(fieldErrors(r).password2).toBe("auth.passwordMismatch");
  });

  it("bo'sh parol `required` beradi, `hint` EMAS", () => {
    const r = authSchema.safeParse({ ...base, password: "", password2: "" });
    //: Bo'sh maydon «juda qisqa» emas — u umuman to'ldirilmagan.
    expect(fieldErrors(r).password).toBe("auth.required");
  });
});

describe("authSchema — rozilik", () => {
  const base = {
    identifier: "kim",
    email: "a@b.co",
    password: "parol123",
    password2: "parol123",
    terms_accepted: true,
  };

  it("rozilik belgilanmasa rad etiladi", () => {
    const r = authSchema.safeParse({ ...base, terms_accepted: false });
    expect(fieldErrors(r).terms_accepted).toBe("auth.termsRequired");
  });
});

describe("authSchema — identifikator", () => {
  it("bo'sh identifikator rad etiladi", () => {
    const r = authSchema.safeParse({
      identifier: "   ",
      email: "a@b.co",
      password: "parol123",
      password2: "parol123",
      terms_accepted: true,
    });
    expect(fieldErrors(r).identifier).toBe("auth.required");
  });
});

describe("resetSchema — parolni tiklash", () => {
  it("mos parollar o'tadi", () => {
    expect(resetSchema.safeParse({ password: "yangi12345", password2: "yangi12345" }).success).toBe(
      true,
    );
  });

  it("mos kelmasa xato", () => {
    const r = resetSchema.safeParse({ password: "yangi12345", password2: "boshqa123" });
    expect(fieldErrors(r).password2).toBe("auth.passwordMismatch");
  });

  it("qisqa parol rad etiladi", () => {
    const r = resetSchema.safeParse({ password: "qisqa", password2: "qisqa" });
    expect(fieldErrors(r).password).toBe("auth.passwordHint");
  });
});

describe("resetRequestSchema", () => {
  it("login to'ldirilsa o'tadi", () => {
    expect(resetRequestSchema.safeParse({ login: "kim" }).success).toBe(true);
  });

  it("bo'sh login rad etiladi", () => {
    const r = resetRequestSchema.safeParse({ login: "" });
    expect(fieldErrors(r).login).toBe("auth.required");
  });
});

describe("onboardingSchema — taxallus (yagona majburiy maydon)", () => {
  const base = {
    username: "kim",
    display_name: "",
    city: "",
    school: "",
    phone: "",
  };

  it("to'g'ri taxallus o'tadi, ixtiyoriy maydonlar bo'sh qolsa ham", () => {
    expect(onboardingSchema.safeParse(base).success).toBe(true);
  });

  it("bo'sh taxallus `usernameRequired` beradi", () => {
    const r = onboardingSchema.safeParse({ ...base, username: "   " });
    expect(fieldErrors(r).username).toBe("auth.usernameRequired");
  });

  it(`${USERNAME_MIN} dan qisqa taxallus rad etiladi`, () => {
    const r = onboardingSchema.safeParse({ ...base, username: "ab" });
    expect(fieldErrors(r).username).toBe("auth.usernameInvalid");
  });

  it(`${USERNAME_MAX} dan uzun taxallus rad etiladi`, () => {
    const r = onboardingSchema.safeParse({ ...base, username: "a".repeat(USERNAME_MAX + 1) });
    expect(fieldErrors(r).username).toBe("auth.usernameInvalid");
  });

  it("aynan chegaradagi uzunlik qabul qilinadi", () => {
    for (const n of [USERNAME_MIN, USERNAME_MAX]) {
      expect(onboardingSchema.safeParse({ ...base, username: "a".repeat(n) }).success).toBe(true);
    }
  });

  it("probel va kirill harf rad etiladi", () => {
    for (const bad of ["kim ocha", "ким", "kim-bek", "kim.bek"]) {
      const r = onboardingSchema.safeParse({ ...base, username: bad });
      expect(fieldErrors(r).username, bad).toBe("auth.usernameInvalid");
    }
  });

  it("raqam va pastki chiziq o'tadi", () => {
    expect(onboardingSchema.safeParse({ ...base, username: "kim_2010" }).success).toBe(true);
  });
});

describe("passwordChangeSchema — sozlamalar", () => {
  const base = { old_password: "eski12345", new_password: "yangi12345", confirm: "yangi12345" };

  it("mos parollar o'tadi", () => {
    expect(passwordChangeSchema.safeParse(base).success).toBe(true);
  });

  it("eski parol BO'SH bo'lsa ham o'tadi (qoidasi faqat serverda)", () => {
    //: Hisobda parol yo'q bo'lsa maydon umuman ko'rsatilmaydi — mijoz uni
    //: uzunlikka qarab baholay olmaydi, shuning uchun talab qilmaydi.
    expect(passwordChangeSchema.safeParse({ ...base, old_password: "" }).success).toBe(true);
  });

  it("tasdiq mos kelmasa xato", () => {
    const r = passwordChangeSchema.safeParse({ ...base, confirm: "boshqa123" });
    expect(fieldErrors(r).confirm).toBe("auth.passwordMismatch");
  });

  it("qisqa yangi parol rad etiladi", () => {
    const r = passwordChangeSchema.safeParse({
      old_password: "eski12345",
      new_password: "qisqa",
      confirm: "qisqa",
    });
    expect(fieldErrors(r).new_password).toBe("auth.passwordHint");
  });

  it("bo'sh yangi parol `required` beradi, `hint` EMAS", () => {
    const r = passwordChangeSchema.safeParse({
      old_password: "eski12345",
      new_password: "",
      confirm: "",
    });
    expect(fieldErrors(r).new_password).toBe("auth.required");
  });
});

describe("sourceSchema — yechim manbasi", () => {
  const bytes = (s: string) => new TextEncoder().encode(s).length;

  it("bo'sh manba `sourceRequired` beradi", () => {
    const r = sourceSchema.safeParse({ source: "   ", bytes: 3 });
    expect(fieldErrors(r).source).toBe("submit.sourceRequired");
  });

  it(`aynan ${SOURCE_MAX_BYTES} bayt o'tadi (chegara)`, () => {
    const atLimit = "a".repeat(SOURCE_MAX_BYTES);
    expect(sourceSchema.safeParse({ source: atLimit, bytes: bytes(atLimit) }).success).toBe(true);
  });

  it("chegaradan bir bayt oshsa rad etiladi", () => {
    const over = "a".repeat(SOURCE_MAX_BYTES + 1);
    const r = sourceSchema.safeParse({ source: over, bytes: bytes(over) });
    expect(fieldErrors(r).bytes).toBe("submit.sourceTooLong");
  });

  it("kirill harf BAYTDA hisoblanadi (belgida emas)", () => {
    //: 32 768 kirill harf = 65 536 bayt = chegara. Belgilar bo'yicha
    //: sanasak u «32 KB» ko'rinardi va server 413 qaytarardi.
    const cyrillic = "я".repeat(SOURCE_MAX_BYTES / 2);
    expect(bytes(cyrillic)).toBe(SOURCE_MAX_BYTES);
    expect(sourceSchema.safeParse({ source: cyrillic, bytes: bytes(cyrillic) }).success).toBe(true);
    const oneMore = "я".repeat(SOURCE_MAX_BYTES / 2 + 1);
    expect(
      fieldErrors(sourceSchema.safeParse({ source: oneMore, bytes: bytes(oneMore) })).bytes,
    ).toBe("submit.sourceTooLong");
  });
});

describe("loginSchema va registerSchema — rejim ajratmasi", () => {
  it("kirishda faqat identifikator va parol talab qilinadi", () => {
    expect(loginSchema.safeParse({ identifier: "kim", password: "parol123" }).success).toBe(true);
  });

  it("kirishda bo'sh identifikator rad etiladi", () => {
    const r = loginSchema.safeParse({ identifier: "  ", password: "parol123" });
    expect(fieldErrors(r).identifier).toBe("auth.required");
  });

  it("kirishda bo'sh parol rad etiladi", () => {
    const r = loginSchema.safeParse({ identifier: "kim", password: "" });
    expect(fieldErrors(r).password).toBe("auth.required");
  });

  it("kirishda QISQA parol rad ETILMAYDI (uzunlik qoidasi faqat ro'yxatda)", () => {
    //: Ataylab: mavjud hisobning paroli 8 belgidan qisqa bo'lishi mumkin
    //: (qoida keyin kiritilgan bo'lsa) va uni kirishda rad etish odamni
    //: umuman kiritmay qo'yardi. To'g'ri/noto'g'ri — faqat server biladi.
    expect(loginSchema.safeParse({ identifier: "kim", password: "q" }).success).toBe(true);
  });

  it("kirishda email/rozilik UMUMAN talab qilinmaydi", () => {
    //: Ya'ni chaqiruvchi soxta `email` to'qishi shart emas — bu ilgari
    //: qattiq yozilgan matn tug'dirardi (`check_hardcoded` uni tutgan).
    const r = loginSchema.safeParse({ identifier: "kim", password: "parol123" });
    expect(Object.keys(fieldErrors(r))).toEqual([]);
  });

  it("`authSchemaFor` rejimga qarab to'g'ri sxemani beradi", () => {
    expect(authSchemaFor("login")).toBe(loginSchema);
    expect(authSchemaFor("register")).toBe(registerSchema);
  });

  it("`registerSchema` — `authSchema` bilan bir xil qoida", () => {
    expect(registerSchema).toBe(authSchema);
  });
});

describe("fieldErrors", () => {
  it("muvaffaqiyatda bo'sh obyekt", () => {
    const r = resetRequestSchema.safeParse({ login: "kim" });
    expect(fieldErrors(r)).toEqual({});
  });

  it("bir maydonda birinchi xato qaytadi", () => {
    //: `password2` ham bo'sh, ham mos emas — natijada bitta kalit bo'lishi
    //: kerak, aks holda UI ikki qatorni ustma-ust chizardi.
    const r = resetSchema.safeParse({ password: "", password2: "" });
    const errors = fieldErrors(r);
    expect(Object.keys(errors).length).toBe(1);
    expect(errors.password).toBe("auth.required");
  });

  it("ommaviy kirishda ham bir xil ishlaydi (`result.error.issues`)", () => {
    const r = authSchema.safeParse({
      identifier: "",
      email: "x",
      password: "",
      password2: "",
      terms_accepted: false,
    });
    const errors = fieldErrors(r);
    expect(errors.email).toBe("auth.emailInvalid");
    expect(errors.terms_accepted).toBe("auth.termsRequired");
  });
});
