// ⚠️ jsdom ATAYLAB ishlatilmaydi — `document.cookie` o'rniga eng kichik
// stub qo'yamiz. Sabab: (a) `jsdom` loyihada o'rnatilmagan, uni faqat shu
// test uchun tortib kelish og'ir; (b) `isOn` `document` dan faqat bitta
// narsa — `cookie` matnini — o'qiydi, ya'ni to'liq DOM kerak emas.
//
// Stub `isOn` ning O'Z kodini o'lchaydi: qavatlar tartibi, `!nom`,
// guruh ajratish — hammasi haqiqiy funksiya ichida qoladi.
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import {
  EXP_COOKIE,
  FLAGS,
  FLAG_OVERRIDES,
  isOn,
  isOnServer,
  parseVariant,
} from "@/lib/flags";

/** Cookie do'koni — `document.cookie` ning minimal o'rnini bosuvchi. */
const jar = new Map<string, string>();

function installCookieStub() {
  Object.defineProperty(globalThis, "document", {
    configurable: true,
    writable: true,
    value: {
      get cookie() {
        return [...jar].map(([k, v]) => `${k}=${v}`).join("; ");
      },
      set cookie(raw: string) {
        const [pair] = raw.split(";");
        const [name, ...rest] = pair.split("=");
        const key = name.trim();
        if (!key) return;
        if (raw.includes("expires=Thu, 01 Jan 1970")) {
          jar.delete(key);
          return;
        }
        jar.set(key, rest.join("="));
      },
    },
  });
}

beforeEach(() => {
  jar.clear();
  installCookieStub();
});
afterEach(() => {
  jar.clear();
  Reflect.deleteProperty(globalThis, "document");
});

describe("parseVariant — sof funksiya", () => {
  it("cookie yo'q bo'lsa 'a' (nazorat guruhi)", () => {
    expect(parseVariant(undefined, "geo")).toBe("a");
  });

  it("kutilgan guruhni topadi", () => {
    expect(parseVariant("geo:b", "geo")).toBe("b");
    expect(parseVariant("geo:a", "geo")).toBe("a");
  });

  it("boshqa nomlangan guruhlar orasidan o'zinikini oladi", () => {
    expect(parseVariant("other:a,geo:b,third:a", "geo")).toBe("b");
  });

  it("notanish qiymat 'a' ga qaytadi — jimgina b guruhga tushmaslik", () => {
    expect(parseVariant("geo:c", "geo")).toBe("a");
    expect(parseVariant("geo", "geo")).toBe("a");
    expect(parseVariant("", "geo")).toBe("a");
  });

  it("nom qismiy mosligi guruhni almashtirmasin", () => {
    // `geology` — boshqa eksperiment; `geo` ni yonmasligi kerak.
    expect(parseVariant("geology:b", "geo")).toBe("a");
  });
});

describe("isOn — qavatlar tartibi", () => {
  it("bayroq ro'yxatda bo'lmasa ham standart qaytadi", () => {
    // `FLAGS` standarti hozir hammasi `false`.
    for (const name of Object.keys(FLAGS) as (keyof typeof FLAGS)[]) {
      expect(typeof isOn(name)).toBe("boolean");
    }
  });

  it("dev override cookie'si bayroqni yondiradi", () => {
    document.cookie = `${FLAG_OVERRIDES}=newNav`;
    expect(isOn("newNav")).toBe(true);
    expect(isOn("optimisticSave")).toBe(false);
  });

  it("`!nom` majburan o'chiradi", () => {
    document.cookie = `${FLAG_OVERRIDES}=!newNav,newPalette`;
    expect(isOn("newNav")).toBe(false);
    expect(isOn("newPalette")).toBe(true);
  });

  it("override bo'sh joy va ortiqcha vergulga chidamli", () => {
    document.cookie = `${FLAG_OVERRIDES}=%20newNav%20%2C%20`;
    expect(isOn("newNav")).toBe(true);
  });

  it("eksperiment guruhi override'dan KEYIN keladi", () => {
    // `geoEarlyRegion` override'da yo'q, ya'ni guruh hal qiladi.
    document.cookie = `${EXP_COOKIE}=geo:b`;
    expect(isOn("geoEarlyRegion")).toBe(true);
    document.cookie = `${EXP_COOKIE}=geo:a`;
    expect(isOn("geoEarlyRegion")).toBe(false);
  });

  it("override eksperimentdan USTUN", () => {
    document.cookie = `${FLAG_OVERRIDES}=!geoEarlyRegion`;
    document.cookie = `${EXP_COOKIE}=geo:b`;
    expect(isOn("geoEarlyRegion")).toBe(false);
  });
});

describe("isOnServer — Cookie sarlavhasidan", () => {
  it("sarlavha yo'q bo'lsa standart", () => {
    expect(isOnServer("newNav", undefined)).toBe(FLAGS.newNav);
  });

  it("eksperiment guruhini sarlavhadan o'qiydi", () => {
    expect(isOnServer("geoEarlyRegion", "a=1; rw_exp=geo:b; z=2")).toBe(true);
    expect(isOnServer("geoEarlyRegion", "rw_exp=geo:a")).toBe(false);
  });

  it("sarlavhadagi boshqa cookie'ga aralashmaydi", () => {
    expect(isOnServer("geoEarlyRegion", "not_rw_exp=geo:b")).toBe(false);
  });
});

describe("isOnServer va isOn — bir xil javob (hidratsiya xatosi to'sig'i)", () => {
  it("eksperiment bayrog'i ikkala yo'lda bir xil bo'ladi", () => {
    // ⚠️ Bu ENG MUHIM test: SSR `isOnServer` ni, keyin brauzer `isOn` ni
    // chaqiradi. Ikkisi xilma-xil javob bersa React hidratsiya xatosi
    // beradi. Shuning uchun cookie'ni IKKALA manbaga bir xil beramiz.
    for (const variant of ["geo:a", "geo:b", ""]) {
      jar.clear();
      if (variant) {
        jar.set(EXP_COOKIE, variant);
        document.cookie = `${EXP_COOKIE}=${variant}`;
      }
      const header = variant ? `${EXP_COOKIE}=${variant}` : undefined;
      expect(isOnServer("geoEarlyRegion", header)).toBe(
        isOn("geoEarlyRegion"),
      );
    }
  });
});

describe("flags moduli — React'siz (Edge/middleware uchun)", () => {
  it("`flags.ts` da `react` importi YO'Q", async () => {
    // ⚠️ `middleware` (Edge runtime) React hook'ni ko'tarmaydi. Faylga
    // `import { useState } from "react"` qaytsa `next build` yiqiladi
    // (o'lchandi 2026-09-24). Bu test o'sha qoidani ushlab turadi.
    const { readFile } = await import("node:fs/promises");
    const { fileURLToPath } = await import("node:url");
    const path = fileURLToPath(new URL("../../src/lib/flags.ts", import.meta.url));
    const src = await readFile(path, "utf-8");
    // Izohlar hisobga olinmasin — faqat haqiqiy import satrlari.
    const code = src
      .split("\n")
      .filter((line) => !line.trim().startsWith("*") && !line.trim().startsWith("//"))
      .join("\n");
    expect(code).not.toMatch(/^\s*import\s.*["']react["']/m);
  });
});
