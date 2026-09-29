/**
 * The shared i18n core, tested where it now lives.
 *
 * WHY A SECOND SUITE: the web suite tests the *app* wiring (dictionaries
 * loaded per locale, the provider, the eviction on the client). This suite
 * tests the *rules* — and it can run without React, without Next and
 * without a DOM. That is precisely the claim `packages/` makes: if these
 * tests cannot run here, the extraction did not achieve anything.
 *
 * `NODE_ENV` is `test` under vitest, which is not `production`, so the
 * missing-property policy is the *throw* branch. That branch is the one
 * worth pinning: the silent fallback hid bugs twice.
 */

import { beforeEach, describe, expect, it } from "vitest";

import {
  CONTENT_NAME_LOCALES,
  DEFAULT_LOCALE,
  LOCALES,
  LOCALE_NAMES,
  type Locale,
  errorText,
  fill,
  hasContentNames,
  hasMessages,
  isLocale,
  localName,
  localNameInfo,
  registerMessages,
  registrySize,
  resetRegistry,
  t,
  topicName,
  translate,
} from "../src/i18n/index";

const uz = { "a.one": "Bir", "a.two": "Ikki", "error.notFound": "Topilmadi" };
const en = { "a.one": "One", "a.two": "Two", "error.notFound": "Not found" };

beforeEach(() => {
  resetRegistry();
});

describe("locale identity", () => {
  it("o'nta til, takrorlanmas", () => {
    expect(LOCALES).toHaveLength(10);
    expect(new Set(LOCALES).size).toBe(10);
  });

  it("`DEFAULT_LOCALE` ro'yxatda bor", () => {
    expect(LOCALES).toContain(DEFAULT_LOCALE);
  });

  it("har bir til uchun ko'rsatiladigan nom bor", () => {
    for (const locale of LOCALES) {
      expect(LOCALE_NAMES[locale], locale).toBeTruthy();
    }
  });

  it("`isLocale` faqat ro'yxatdagini qabul qiladi", () => {
    expect(isLocale("uz")).toBe(true);
    expect(isLocale("de")).toBe(false);
    expect(isLocale(null)).toBe(false);
    expect(isLocale(undefined)).toBe(false);
    expect(isLocale("")).toBe(false);
  });
});

describe("registry", () => {
  it("ro'yxatga olish uni ko'rinadigan qiladi", () => {
    expect(hasMessages("uz")).toBe(false);
    registerMessages("uz", uz);
    expect(hasMessages("uz")).toBe(true);
    expect(registrySize()).toBe(1);
  });

  it("ikkinchi lug'at birinchisini O'CHIRMAYDI", () => {
    //: Bu regressiya bir marta sodir bo'lgan: `clear()` faqat oxirgi
    //: tilni qoldirib, SSR'da o'nlab kalitni xom ko'rsatgan.
    registerMessages("uz", uz);
    registerMessages("en", en);
    expect(registrySize()).toBe(2);
    expect(t("uz", "a.one")).toBe("Bir");
    expect(t("en", "a.one")).toBe("One");
  });

  it("o'sha tilni qayta ro'yxatga olish uni almashtiradi", () => {
    registerMessages("uz", uz);
    registerMessages("uz", { "a.one": "Yangi" });
    expect(registrySize()).toBe(1);
    expect(t("uz", "a.one")).toBe("Yangi");
  });
});

describe("t / translate — qidiruv qoidasi", () => {
  beforeEach(() => {
    registerMessages("uz", uz);
    registerMessages("en", en);
  });

  it("mavjud kalitni qaytaradi", () => {
    expect(t("uz", "a.two")).toBe("Ikki");
  });

  it("bir nechta kalitni TARTIB bilan qaytaradi", () => {
    expect(translate("uz", "a.one", "a.two")).toEqual(["Bir", "Ikki"]);
  });

  it("BOSHQA tilga tushmaydi — rivojlanishda istisno tashlaydi", () => {
    //: `en` lug'ati bor, lekin `xx` yo'q. Fallback til YO'Q: `uz` yoki
    //: `en` dan qarz olish o'rniga xato beriladi. Bu ataylab.
    expect(() => t("uz", "yoq.bunday")).toThrow(/missing from the "uz" dictionary/);
  });

  it("lug'at umuman yo'q bo'lsa boshqa xato matni", () => {
    expect(() => t("es" as Locale, "a.one")).toThrow(/is not registered/);
  });

  it("bo'sh satr ham «yo'q» hisoblanadi", () => {
    registerMessages("uz", { ...uz, "a.two": "" });
    expect(() => t("uz", "a.two")).toThrow();
  });
});

describe("errorText — API kodi → kalit", () => {
  beforeEach(() => {
    registerMessages("uz", { ...uz, "error.error": "Umumiy xato" });
  });

  it("kodni `error.<kod>` ga aylantiradi", () => {
    expect(errorText("uz", "notFound")).toBe("Topilmadi");
  });

  it("serverdagi MATNGA ishonmaydi (tarjima o'rnini bosmaydi)", () => {
    //: Server xabari inglizcha bo'lishi mumkin; uni ko'rsatish
    //: foydalanuvchiga tushunarsiz tilda matn berardi.
    expect(errorText("uz", "notFound", "Some English server text")).toBe("Topilmadi");
  });

  it("bo'sh kod `error.error` ga tushadi", () => {
    expect(errorText("uz", "")).toBe("Umumiy xato");
  });
});

describe("fill", () => {
  it("`{nom}` o'rinlarini to'ldiradi", () => {
    expect(fill("{n} ta masala", { n: 3 })).toBe("3 ta masala");
  });

  it("noma'lum o'rin QOLADI (bo'sh satrga aylanmaydi)", () => {
    //: Ataylab: `{n}` ko'rinib turgani nosozlikni bildiradi, jim
    //: yo'qolishi esa «matn shunday» degan taassurot beradi.
    expect(fill("{a} va {b}", { a: "x" })).toBe("x va {b}");
  });

  it("o'rinlar takrorlansa hammasi to'ladi", () => {
    expect(fill("{n}-{n}", { n: 7 })).toBe("7-7");
  });

  it("o'rin yo'q bo'lsa matn tegilmaydi", () => {
    expect(fill("o'zgarmas", { a: 1 })).toBe("o'zgarmas");
  });
});

describe("kontent nomlari — uchta ustun qoidasi", () => {
  const row = { name_uz: "Algoritmlar", name_ru: "Алгоритмы", name_en: "Algorithms", slug: "algo" };

  it("faqat uchta til ustunga ega", () => {
    expect(CONTENT_NAME_LOCALES).toEqual(["uz", "ru", "en"]);
    expect(hasContentNames("uz")).toBe(true);
    expect(hasContentNames("tr")).toBe(false);
  });

  it("ustuni bor tilda o'sha matn qaytadi", () => {
    expect(localName(row, "ru")).toBe("Алгоритмы");
  });

  it("ustuni YO'Q tilda slavyan/o'zbek matni meros qilinmaydi", () => {
    //: `tr` uchun ustun yo'q — `Algorithms` emas, `Алгоритмы` emas,
    //: balki SLUG ko'rsatiladi. O'zga tilni «tarjima» deb ko'rsatish
    //: yolg'on bo'lardi.
    expect(localName(row, "tr")).toBe("algo");
    expect(localNameInfo(row, "tr")).toEqual({ text: "algo", locale: null, source: null });
  });

  it("slug yo'q bo'lsa `name` xossasi ishlatiladi", () => {
    const { slug, ...noSlug } = row;
    void slug;
    expect(localName(noSlug, "es")).toBe("name");
  });

  it("bo'sh (faqat probel) ustun ham «yo'q» hisoblanadi", () => {
    expect(localName({ ...row, name_en: "   " }, "en")).toBe("algo");
  });

  it("haqiqiy tarjima `locale` va `source` ni to'ldiradi", () => {
    expect(localNameInfo(row, "uz")).toEqual({
      text: "Algoritmlar",
      locale: "uz",
      source: "uz",
    });
  });

  it("`topicName` — slug majburiy bo'lgan o'ram", () => {
    expect(topicName({ ...row, slug: "algo" }, "en")).toBe("Algorithms");
    expect(topicName({ ...row, slug: "algo" }, "zh")).toBe("algo");
  });
});
