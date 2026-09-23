import { describe, expect, it } from "vitest";

import { Cache } from "@/lib/hooks/cache";

// `Cache` — `useLoad` ning yuragi va u React'siz o'lchanadi. Sabab:
// `@testing-library/react` loyihada yo'q, lekin kesh xatosi JIMGINA
// sodir bo'ladi — dedup buzuq bo'lsa ortiqcha so'rov ketadi, kesh buzuq
// bo'lsa eskirgan ma'lumot ko'rinadi. Ikkisini ham shu yerda o'lchaymiz.

const T0 = 1_000_000;

describe("Cache — yangilik (freshness)", () => {
  it("yozuv yo'q bo'lsa 'yangi emas'", () => {
    expect(new Cache().isFresh("a", 30_000, T0)).toBe(false);
  });

  it("qiymat kelmagan (faqat so'rov uchgan) bo'lsa 'yangi emas'", () => {
    const cache = new Cache();
    cache.startFlight("a", Promise.resolve(1), T0);
    // So'rov uchayapti, qiymat yo'q — keshdan javob berib bo'lmaydi.
    expect(cache.isFresh("a", 30_000, T0 + 1)).toBe(false);
  });

  it("vaqt oynasi ichida 'yangi'", () => {
    const cache = new Cache();
    cache.settle("a", 42, T0);
    expect(cache.isFresh("a", 30_000, T0 + 29_999)).toBe(true);
  });

  it("vaqt oynasidan chiqsa 'eski' — qayta so'raladi", () => {
    const cache = new Cache();
    cache.settle("a", 42, T0);
    expect(cache.isFresh("a", 30_000, T0 + 30_000)).toBe(false);
  });

  it("kalitlar bir-biriga aralashmaydi", () => {
    const cache = new Cache();
    cache.settle("/me/skills/", [1, 2], T0);
    expect(cache.isFresh("/skills/catalog/", 30_000, T0)).toBe(false);
    expect(cache.value("/skills/catalog/")).toBeUndefined();
  });
});

describe("Cache — dedup (uchayotgan so'rov)", () => {
  it("uchayotgan so'rov qaytariladi — ikkinchi chaqiruv unga ulanadi", () => {
    const cache = new Cache();
    const p = Promise.resolve("v");
    cache.startFlight("/x/", p, T0);
    expect(cache.promise("/x/")).toBe(p);
  });

  it("natija kelgach `promise` bo'shaydi, qiymat qoladi", () => {
    // ⚠️ Eng nozik joy: `promise` bo'shamasa keyingi chaqiruv «hali
    // uchayapti» deb eski (tugagan) natijani kutib qolardi.
    const cache = new Cache();
    const p = Promise.resolve("v");
    cache.startFlight("/x/", p, T0);
    cache.settle("/x/", "v", T0 + 5);
    expect(cache.promise("/x/")).toBeUndefined();
    expect(cache.value("/x/")).toBe("v");
  });

  it("xatodan keyin so'rov ham, qiymat ham yo'q — qayta urinish mumkin", () => {
    const cache = new Cache();
    // Rad etilgan promis `startFlight` dan OLDIN tutulishi shart, aks
    // holda Vitest uni «unhandled rejection» deb belgilaydi. Bo'sh
    // `.catch` — bu tozalash, mantiq emas.
    const failing = Promise.reject(new Error("boom"));
    failing.catch(() => {});
    cache.startFlight("/x/", failing, T0);
    cache.fail("/x/");
    expect(cache.promise("/x/")).toBeUndefined();
    expect(cache.value("/x/")).toBeUndefined();
    expect(cache.isFresh("/x/", 30_000, T0)).toBe(false);
  });

  it("ikkinchi chaqiruv paytida uchayotgan bo'lsa, yangi so'rov boshlanmaydi", () => {
    const cache = new Cache();
    const first = Promise.resolve("v");
    cache.startFlight("/x/", first, T0);
    // Chaqiruvchi shu mantiqni yurgizadi:
    const reused = cache.promise("/x/") ?? Promise.resolve("YANGI");
    expect(reused).toBe(first);
  });
});

describe("Cache — invalidate (reload)", () => {
  it("`invalidate` yozuvni butunlay tashlaydi", () => {
    const cache = new Cache();
    cache.settle("/x/", "v", T0);
    expect(cache.isFresh("/x/", 30_000, T0)).toBe(true);
    cache.invalidate("/x/");
    expect(cache.isFresh("/x/", 30_000, T0)).toBe(false);
    expect(cache.value("/x/")).toBeUndefined();
    expect(cache.size()).toBe(0);
  });

  it("`invalidate` boshqa kalitga tegmaydi", () => {
    const cache = new Cache();
    cache.settle("/a/", 1, T0);
    cache.settle("/b/", 2, T0);
    cache.invalidate("/a/");
    expect(cache.value("/b/")).toBe(2);
  });

  it("`clear` hammasini tashlaydi", () => {
    const cache = new Cache();
    cache.settle("/a/", 1, T0);
    cache.settle("/b/", 2, T0);
    cache.clear();
    expect(cache.size()).toBe(0);
  });
});
