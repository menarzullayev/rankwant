// ⚠️ jsdom ATAYLAB ishlatilmaydi — `document.cookie` uchun eng kichik stub
// qo'yiladi (`flags.test.ts` bilan bir xil sabab: jsdom loyihada yo'q va
// `variant` undan faqat cookie MATNINI o'qiydi).
//
// Bu test 2026-09-28 dagi xatoni qamraydi: `experiments.ts` da cookie
// naqshi `\s` bilan yozilgan edi, template literal ichida esa `\s` shunchaki
// `s` bo'lib qoladi. Naqsh `(?:^|;s*)` ga aylanib, bo'sh joyni emas, `s`
// harfini qidirardi ⇒ cookie BIRINCHI bo'lmasa topilmasdi. Brauzer esa
// cookie'larni `"; "` bilan ajratadi, ya'ni amalda deyarli har doim
// ikkinchi yoki undan keyingi o'rinda turadi.
import { afterEach, describe, expect, it } from "vitest";

import { variant } from "@/lib/experiments";

/** Cookie matnini berilgan satrga o'rnatadi. */
function withCookie(raw: string) {
  Object.defineProperty(globalThis, "document", {
    configurable: true,
    writable: true,
    value: { get cookie() { return raw; } },
  });
}

afterEach(() => {
  Reflect.deleteProperty(globalThis, "document");
});

describe("experiment variant — cookie o'rni", () => {
  it("birinchi cookie'dan o'qiydi", () => {
    withCookie("rw_exp=geo:b");
    expect(variant("geo")).toBe("b");
  });

  it("IKKINCHI cookie'dan ham o'qiydi (2026-09-28 xatosi)", () => {
    withCookie("other=1; rw_exp=geo:b");
    expect(variant("geo")).toBe("b");
  });

  it("bo'sh joysiz ajratilganda ham o'qiydi", () => {
    withCookie("other=1;rw_exp=geo:b");
    expect(variant("geo")).toBe("b");
  });

  it("boshqa guruh nomi 'a' qaytaradi", () => {
    withCookie("other=1; rw_exp=geo:b");
    expect(variant("boshqa")).toBe("a");
  });

  it("cookie yo'q bo'lsa 'a' qaytaradi", () => {
    withCookie("other=1");
    expect(variant("geo")).toBe("a");
  });
});
