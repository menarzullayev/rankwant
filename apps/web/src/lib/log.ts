/** Web jurnali — bitta qatlam, uchta chiqish.
 *
 *  ## Nega Sentry emas
 *
 *  Saidakbar aka qarori (2026-09-24): **Sentry o'rniga oddiy logging.**
 *  Sabab — tashqi xizmat talab qilmaydi, DSN va tarmoq ruxsati kerak
 *  emas, GDPR uchun uchinchi tomon bilan shartnoma kerak emas. Loyiha
 *  bitta mashinada ishlaydi (Cloudflare Tunnel), ya'ni xatoni yig'ish
 *  uchun ham shu mashina yetarli.
 *
 *  ## Uchta chiqish
 *
 *  | Muhit            | `debug`        | `info`/`warn`  | `error`        |
 *  |------------------|----------------|----------------|----------------|
 *  | `development`    | konsol         | konsol         | konsol (to'liq)|
 *  | `production`     | **jim**        | konsol         | konsol + beacon|
 *
 *  - **Konsol**: har doim `console.*` orqali — brauzer DevTools va
 *    `docker compose logs` uni ko'radi.
 *  - **Beacon**: faqat `error` va faqat productionda. `keepalive: true`
 *    bilan yuboriladi, ya'ni sahifa yopilayotganda ham yetib boradi
 *    (`sendBeacon` emas: u sarlavha qo'ya olmaydi va CSRF yiqilardi —
 *    xuddi `analytics.ts` dagi sabab).
 *
 *  ⚠️ **`debug` productionda jim.** Sabab: `console.log` har chaqiruvda
 *  satr quradi va profil嘈lamaydi, ya'ni ishlab chiqarishda qolib
 *  ketsa sekinlashtiradi. Konsol tarixi ham to'lib ketadi va haqiqiy
 *  xato ko'rinmay qoladi.
 *
 *  ⚠️ **Maxfiy ma'lumot yuborilmaydi.** `sanitize` token, parol va
 *  cookie nomli kalitlarni `[redacted]` bilan almashtiradi. Bu ataylab:
 *  jurnalga tushgan PAT yoki CSRF token — sizib chiqish.
 *
 *  ```ts
 *  import { log } from "@/lib/log";
 *  log.debug("cache", "hit", { key });
 *  log.error("submit", "so'rov yiqildi", { err, problemId });
 *  ```
 */

const isDev = process.env.NODE_ENV !== "production";

/** Yuborilmaydigan kalitlar — nom bo'yicha (registrga befarq). */
const SECRET_KEYS =
  /token|password|passwd|secret|authorization|cookie|csrf|session|pat|apikey|api_key/i;

export type LogLevel = "debug" | "info" | "warn" | "error";

/** Funksiya (`Error`) ni jurnalga yaroqli obyektga aylantiradi.
 *
 *  `JSON.stringify(new Error("x"))` bo'sh obyekt beradi — `message` va
 *  `stack` enumerable emas. Analitika bekonida xato **ko'rinmas**
 *  qolardi, ya'ni jurnal bor, foydasi yo'q edi. */
export function shapeError(err: Error): Record<string, unknown> {
  const out: Record<string, unknown> = {
    name: err.name,
    message: err.message,
  };
  // Stack'ning faqat dastlabki qatorlari — to'liq stack 10-20 KB bo'ladi
  // va bekon yukini behuda oshiradi.
  if (err.stack) out.stack = err.stack.split("\n").slice(0, 6).join("\n");
  return out;
}

/** Obyektdagi maxfiy kalitlarni almashtiradi (sayoz, bir daraja).
 *
 *  ⚠️ Eksport — test uchun. Bu funksiya xavfsizlik qarori qabul
 *  qiladi (`[redacted]`), ya'ni uni o'lchash shart: noto'g'ri ishlasa
 *  jurnalga token tushadi va bu **jimgina** sodir bo'ladi. */
export function sanitize(value: unknown): unknown {
  if (value instanceof Error) return shapeError(value);
  if (Array.isArray(value)) return value.map(sanitize);
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(value as Record<string, unknown>)) {
      out[key] = SECRET_KEYS.test(key) ? "[redacted]" : sanitize(val);
    }
    return out;
  }
  return value;
}

/** `error` darajasidagi yozuvni serverga yuboradi — faqat productionda,
 *  faqat brauzerda. Yiqilishi **jimgina** yutiladi: jurnal xatosi
 *  foydalanuvchi oqimini to'xtatmasligi kerak. */
function beacon(scope: string, message: string, fields: Record<string, unknown>): void {
  if (isDev || typeof window === "undefined") return;
  try {
    const body = JSON.stringify({
      level: "error",
      scope,
      message,
      fields: sanitize(fields),
      path: window.location.pathname,
      at: new Date().toISOString(),
    });
    // `API_BASE` ni import qilmaymiz: `lib/api` butun API qatlamini
    // tortadi, jurnal esa undan pastda turishi kerak (aylanma bog'lanish).
    const base = process.env.NEXT_PUBLIC_API_BASE ?? "";
    void fetch(`${base}/client-logs/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      keepalive: true,
      credentials: "include",
    }).catch(() => {});
  } catch {
    // Jurnal yuborilmadi — jim o'tamiz.
  }
}

const CONSOLE: Record<LogLevel, (...a: unknown[]) => void> = {
  debug: console.debug.bind(console),
  info: console.info.bind(console),
  warn: console.warn.bind(console),
  error: console.error.bind(console),
};

function emit(
  level: LogLevel,
  scope: string,
  message: string,
  fields: Record<string, unknown> = {},
): void {
  // ⚠️ `debug` ishlab chiqarishda TASHLAB KETILADI — shartsiz.
  //
  // Ilgari bu yerda `if (Object.keys(fields).length === 0) return;` bor
  // edi, ya'ni `fields` berilgan har bir `debug` **o'tib ketardi**:
  // yuqoridagi jadval va izoh «jim» deb yozgan bo'lsa-da, kod buni
  // bajarmasdi (o'lchandi 2026-09-24 salbiy test bilan). Aynan o'sha
  // holat eng ko'p uchraydi — `log.debug("cache", "miss", { key })`.
  if (level === "debug" && !isDev) return;
  CONSOLE[level](`[${scope}] ${message}`, sanitize(fields));
  if (level === "error") beacon(scope, message, fields);
}

/** Scope — modul nomi (`"submit"`, `"api"`, `"auth"`). Bitta jurnal
 *  funksiyasi yetarli, lekin scope majburiy: usiz 200 ta yozuv orasida
 *  qaysi modul yozganini topib bo'lmaydi. */
export const log = {
  debug: (scope: string, message: string, fields?: Record<string, unknown>) =>
    emit("debug", scope, message, fields),
  info: (scope: string, message: string, fields?: Record<string, unknown>) =>
    emit("info", scope, message, fields),
  warn: (scope: string, message: string, fields?: Record<string, unknown>) =>
    emit("warn", scope, message, fields),
  error: (scope: string, message: string, fields?: Record<string, unknown>) =>
    emit("error", scope, message, fields),
};
