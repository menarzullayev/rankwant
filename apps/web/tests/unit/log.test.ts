import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { log, sanitize, shapeError } from "@/lib/log";

// `log` modul yuklanishida `NODE_ENV` ni bir marta o'qiydi
// (`const isDev = ...`). Ya'ni production yo'lini o'lchash uchun modulni
// `vi.resetModules()` bilan qayta yuklash SHART — aks holda test
// «development» mantiqini o'lchab, production haqida yolg'on xulosa
// beradi.

/** Konsolni ushlab oladi va chaqiruvlarni yozib boradi. */
function spyConsole() {
  return {
    debug: vi.spyOn(console, "debug").mockImplementation(() => {}),
    info: vi.spyOn(console, "info").mockImplementation(() => {}),
    warn: vi.spyOn(console, "warn").mockImplementation(() => {}),
    error: vi.spyOn(console, "error").mockImplementation(() => {}),
  };
}

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
});

describe("sanitize — maxfiy kalitlarni yashiradi", () => {
  it("token/parol/cookie kalitlarini `[redacted]` qiladi", () => {
    const out = sanitize({
      token: "abc",
      password: "hunter2",
      csrfToken: "x",
      Authorization: "Bearer y",
      cookie: "sid=1",
      apiKey: "k",
      api_key: "k",
      sessionId: "s",
      secret: "s",
      pat: "p",
    }) as Record<string, unknown>;
    for (const key of Object.keys(out)) {
      expect(out[key]).toBe("[redacted]");
    }
  });

  it("registrga befarq", () => {
    const out = sanitize({ PASSWD: "x", Cookie: "y", APIKEY: "z" }) as Record<
      string,
      unknown
    >;
    expect(out.PASSWD).toBe("[redacted]");
    expect(out.Cookie).toBe("[redacted]");
    expect(out.APIKEY).toBe("[redacted]");
  });

  it("zararsiz kalitlarni QOLDIRADI (yishiradigan narsa ko'p bo'lmasin)", () => {
    const out = sanitize({ problemId: 7, slug: "two-sum", count: 0 }) as Record<
      string,
      unknown
    >;
    expect(out).toEqual({ problemId: 7, slug: "two-sum", count: 0 });
  });

  it("ichma-ich obyektlarni ham tozalaydi", () => {
    const out = sanitize({ user: { name: "A", token: "t" } }) as Record<
      string,
      Record<string, unknown>
    >;
    expect(out.user.name).toBe("A");
    expect(out.user.token).toBe("[redacted]");
  });

  it("massiv ichidagi maxfiy kalitlarni ham yashiradi", () => {
    const out = sanitize([{ token: "a" }, { ok: 1 }]) as Record<
      string,
      unknown
    >[];
    expect(out[0].token).toBe("[redacted]");
    expect(out[1].ok).toBe(1);
  });

  it("Error'ni o'qiladigan obyektga aylantiradi", () => {
    const out = sanitize(new Error("boom")) as Record<string, unknown>;
    expect(out.name).toBe("Error");
    expect(out.message).toBe("boom");
    expect(typeof out.stack).toBe("string");
  });
});

describe("shapeError — xato ko'rinadigan bo'lsin", () => {
  it("`message` va `name` ni saqlaydi (JSON.stringify ularni yo'qotardi)", () => {
    const shaped = shapeError(new TypeError("bad type"));
    expect(shaped.name).toBe("TypeError");
    expect(shaped.message).toBe("bad type");
    // Nazorat: xom `JSON.stringify` bo'sh obyekt beradi.
    expect(JSON.stringify(new TypeError("bad type"))).toBe("{}");
  });

  it("stack'ni 6 qatorgacha qisqartiradi", () => {
    const err = new Error("x");
    err.stack = Array.from({ length: 40 }, (_, i) => `at frame ${i}`).join("\n");
    const shaped = shapeError(err) as { stack: string };
    expect(shaped.stack.split("\n").length).toBe(6);
  });

  it("stack bo'lmasa maydon qo'shilmaydi", () => {
    const err = new Error("x");
    delete err.stack;
    expect("stack" in shapeError(err)).toBe(false);
  });
});

describe("log — daraja filtri (development)", () => {
  it("har bir daraja konsolga chiqadi", async () => {
    vi.stubEnv("NODE_ENV", "development");
    vi.resetModules();
    const spied = spyConsole();
    const { log: devLog } = await import("@/lib/log");

    devLog.debug("s", "d");
    devLog.info("s", "i");
    devLog.warn("s", "w");
    devLog.error("s", "e");

    expect(spied.debug).toHaveBeenCalledTimes(1);
    expect(spied.info).toHaveBeenCalledTimes(1);
    expect(spied.warn).toHaveBeenCalledTimes(1);
    expect(spied.error).toHaveBeenCalledTimes(1);
  });
});

describe("log — production filtri", () => {
  it("`debug` FIELDS bilan ham yuborilmaydi", async () => {
    // ⚠️ Bu — o'lchangan xatoning qo'riqchisi: ilgari `fields` berilsa
    // `debug` productionda o'tib ketardi, izoh esa «jim» deb yozardi.
    vi.stubEnv("NODE_ENV", "production");
    vi.resetModules();
    const spied = spyConsole();
    const { log: prodLog } = await import("@/lib/log");

    prodLog.debug("cache", "miss", { key: "hot" });

    expect(spied.debug).not.toHaveBeenCalled();
  });

  it("`debug` maydonsiz ham jim", async () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.resetModules();
    const spied = spyConsole();
    const { log: prodLog } = await import("@/lib/log");

    prodLog.debug("cache", "miss");

    expect(spied.debug).not.toHaveBeenCalled();
  });

  it("info/warn/error SAQLANADI (filtr faqat debug'ni kesadi)", async () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.resetModules();
    const spied = spyConsole();
    const { log: prodLog } = await import("@/lib/log");

    prodLog.info("s", "i");
    prodLog.warn("s", "w");
    prodLog.error("s", "e");

    expect(spied.info).toHaveBeenCalledTimes(1);
    expect(spied.warn).toHaveBeenCalledTimes(1);
    expect(spied.error).toHaveBeenCalledTimes(1);
  });

  it("konsolga yozilgan maydonlar tozalangan bo'ladi", async () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.resetModules();
    const spied = spyConsole();
    const { log: prodLog } = await import("@/lib/log");

    prodLog.warn("auth", "urindi", { token: "leak-me", userId: 3 });

    const arg = spied.warn.mock.calls[0]?.[1] as Record<string, unknown>;
    expect(arg.token).toBe("[redacted]");
    expect(arg.userId).toBe(3);
  });

  it("scope xabar boshida ko'rinadi (qaysi modul yozgani bilinsin)", async () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.resetModules();
    const spied = spyConsole();
    const { log: prodLog } = await import("@/lib/log");

    prodLog.error("submit", "yiqildi");

    expect(spied.error.mock.calls[0]?.[0]).toBe("[submit] yiqildi");
  });
});

describe("log — bitta jurnal funksiyasi yetarli", () => {
  it("to'rt daraja ham mavjud va funksiya", () => {
    expect(typeof log.debug).toBe("function");
    expect(typeof log.info).toBe("function");
    expect(typeof log.warn).toBe("function");
    expect(typeof log.error).toBe("function");
  });
});
