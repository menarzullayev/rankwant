/** Xavfsizlik sarlavhalari va CSP (RW-ARCH-008).
 *
 *  ## Nega kerak
 *
 *  Sarlavhalarsiz brauzer bizni **himoya qilmaydi**: uchinchi tomon
 *  skripti `document.cookie` ni o'qiy oladi, sayt iframe ichida
 *  ochiladi (clickjacking), `Referer` orqali tashqi saytga to'liq
 *  manzil ketadi. Bularning hammasi brauzer tomonida va faqat shu
 *  sarlavhalar bilan o'chiriladi — backend sozlamasi (`SECURE_*`,
 *  `SESSION_COOKIE_*`) ularni almashtirmaydi, chunki u API javobiga
 *  tegishli, sahifa HTML'iga emas.
 *
 *  ## Nega `Report-Only` emas
 *
 *  ⚠️ CSP'ni avval `Content-Security-Policy-Report-Only` qilib chiqarish
 *  odatiy yo'l. Bu yerda to'g'ridan-to'g'ri majburiy
 *  (`Content-Security-Policy`) qo'yiladi, sabab: sayt **bitta originda**
 *  ishlaydi (`PUBLIC_ORIGIN`), tashqi skript yo'q, ya'ni
 *  `default-src 'self'` ni buzadigan manba yo'q. Report-only qoldirish
 *  «keyinroq yoqamiz» degan va'da bo'lib qolardi.
 *
 *  ⚠️ **`'unsafe-inline'` skript uchun YO'Q.** Sabab: u CSP'ning asosiy
 *  foydasini (inline skript bloklash) yo'q qiladi. Next.js esa inline
 *  bootstrap skript yozadi — yechim **nonce**: har so'rovda yangi qiymat
 *  `script-src` ga qo'shiladi va Next uni o'sha skriptlarga o'zi
 *  yozadi.
 *
 *  ⚠️ **Uslub uchun `'unsafe-inline'` SHART.** Sabab: `next.config.ts`
 *  da `experimental.inlineCss: true` — FCP uchun CSS `<style>` ichiga
 *  solinadi. Nonce uslubga qo'yilmaydi (Next uni qo'llamaydi), ya'ni
 *  `style-src` da inline ruxsat qolishi kerak. Bu ongli almashinuv:
 *  uslub orqali hujum yuzasi skriptdan ancha tor (CSS exfiltration
 *  mumkin, lekin kod bajarmaydi).
 */

/** Brauzer loopback preview — web alohida portda, API `:8301` (see `api-base.ts`).
 *  Production build (`docker compose` `:8300` yoki `next start`) ham shu yerda
 *  ochiladi; `NODE_ENV === "production"` bo'lsa ham CSP ga API origin kerak. */
export function isLoopbackPreviewHost(host: string): boolean {
  if (!host) return false;
  const lower = host.toLowerCase();
  if (lower === "web" || lower.startsWith("web:")) return false;
  if (lower === "api" || lower.startsWith("api:")) return false;
  return /^(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$/.test(lower);
}

/** Local split-stack dev: web `:8310` / `:8300`, API `:8301`.
 *  `connect-src 'self'` blocks `fetch` to the API origin — login fails with
 *  "TypeError: Failed to fetch" and CSP console errors. */
function devApiConnectOrigins(): string[] {
  const origins = new Set<string>([
    "http://127.0.0.1:8301",
    "http://localhost:8301",
    "http://127.0.0.1:8302",
    "http://localhost:8302",
  ]);
  const base = process.env.NEXT_PUBLIC_API_BASE;
  if (base) {
    try {
      origins.add(new URL(base).origin);
    } catch {
      /* ignore malformed env */
    }
  }
  return [...origins];
}

/** CSP uchun `nonce` yasaydi — kriptografik tasodifiy, base64. */
export function makeNonce(): string {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary);
}

/** CSP sarlavhasini quradi.
 *
 *  @param nonce  Joriy so'rov uchun `makeNonce()` natijasi.
 *  @param dev    Ishlab chiqish rejimi — `eval` va `ws:` qo'shiladi.
 *                Next dev'da HMR `eval` ishlatadi va `ws://` orqali
 *                ulanadi; ularsiz sahifa umuman ochilmaydi.
 *  @param secure So'rov HAQIQATAN HTTPS orqali kelganmi. `false` bo'lsa
 *                `upgrade-insecure-requests` qo'shilmaydi.
 */
export function contentSecurityPolicy(
  nonce: string,
  dev: boolean,
  secure: boolean,
  loopbackSplitStack = false,
): string {
  const scriptSrc = [
    "'self'",
    `'nonce-${nonce}'`,
    // `'strict-dynamic'`: nonce olgan skript o'zi yuklagan skriptlarga
    // ruxsat beradi. Next.js kod bo'laklarini (`chunk`) shu yo'l bilan
    // tortadi — usiz har bir chunk alohida sanab chiqilishi kerak edi,
    // ya'ni har build'da CSP buzilardi.
    "'strict-dynamic'",
  ];
  if (dev) scriptSrc.push("'unsafe-eval'");

  const connectSrc = ["'self'"];
  if (dev) connectSrc.push("ws:", "wss:");
  if (dev || loopbackSplitStack) connectSrc.push(...devApiConnectOrigins());

  const directives: Record<string, string[]> = {
    "default-src": ["'self'"],
    "script-src": scriptSrc,
    // Uslub: inline SHART (`inlineCss`), lekin tashqi manba faqat o'zimiz.
    "style-src": ["'self'", "'unsafe-inline'"],
    "img-src": ["'self'", "data:", "blob:", "https:"],
    "font-src": ["'self'", "data:"],
    "connect-src": connectSrc,
    // `object`/`embed` butunlay o'chirilgan — Flash davri qoldig'i,
    // bizda ishlatilmaydi.
    "object-src": ["'none'"],
    // `base-uri 'self'`: `<base>` tegi bilan barcha nisbiy havolani
    // o'g'irlashning oldini oladi.
    "base-uri": ["'self'"],
    // `form-action 'self'`: forma tashqi manzilga yuborilmasin
    // (parolni o'g'irlashning eng oddiy yo'li).
    "form-action": ["'self'"],
    // `frame-ancestors 'none'` — `X-Frame-Options: DENY` ning zamonaviy
    // shakli, clickjacking'ga qarshi.
    "frame-ancestors": ["'none'"],
    "worker-src": ["'self'", "blob:"],
  };

  const parts = Object.entries(directives).map(([k, v]) => `${k} ${v.join(" ")}`);
  // `upgrade-insecure-requests` — faqat sahifa HAQIQATAN HTTPS bo'lsa.
  //
  // ⚠️ Ilgari shart `!dev` edi va bu YETARLI EMAS (o'lchandi 2026-09-28).
  // CI stack — production build, lekin HTTP ustida (`http://web:3000`),
  // ya'ni `NODE_ENV === "production"` ⇒ direktiva qo'shilardi ⇒ brauzer
  // HAR BIR skript so'rovini `https://web:3000/_next/...` ga ko'tarardi
  // va ular `net::ERR_SSL_PROTOCOL_ERROR` bilan yiqilardi ⇒ Next.js
  // gidratatsiyasi umuman ishlamasdi (`__reactFiber$` paydo bo'lmasdi) ⇒
  // brauzer testlarining bosishga tayanadigan 9 tasi yiqilardi.
  //
  // ⚠️ `localhost` bu ta'sirdan MUSTASNO (brauzer uni ishonchli deb
  // biladi), shuning uchun nuqson faqat `web` hostida ko'rinardi —
  // lokal `localhost:3000` da hammasi joyida edi.
  if (secure) parts.push("upgrade-insecure-requests");
  return parts.join("; ");
}

/** CSP bo'lmagan qolgan sarlavhalar.
 *
 *  ⚠️ Ba'zilari CSP bilan ustma-ust tushadi (`X-Frame-Options` ↔
 *  `frame-ancestors`). Ikkisi ham qoldiriladi: eski brauzer CSP
 *  `frame-ancestors` ni bilmasligi mumkin, ya'ni `X-Frame-Options`
 *  zaxira qavat. */
export const SECURITY_HEADERS: Record<string, string> = {
  // MIME-sniffing o'chirilgan: brauzer `Content-Type` ga ishonadi,
  // ya'ni `.txt` fayl skript bo'lib bajarilmaydi.
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  // Tashqi saytga faqat ORIGIN ketadi, to'liq manzil emas.
  // `strict-origin-when-cross-origin` HTTPS→HTTP o'tishda `Referer` ni
  // butunlay tashlaydi.
  "Referrer-Policy": "strict-origin-when-cross-origin",
  // Kerak bo'lmagan brauzer API'lari o'chirilgan. `interest-cohort` —
  // FLoC/TOPICS (Google reklama profilash) rad etiladi.
  "Permissions-Policy":
    "camera=(), microphone=(), geolocation=(), payment=(), usb=(), " +
    "magnetometer=(), gyroscope=(), accelerometer=(), interest-cohort=()",
  // Cross-origin izolyatsiya: boshqa origindagi sahifa bizning
  // sahifani `window.open` bilan o'qiy olmaydi.
  "Cross-Origin-Opener-Policy": "same-origin",
  // Kross-origin resurslar `CORP` sarlavhasiz yuklanmaydi — bizning
  // rasm/font tashqi saytga singdirilishi mumkin emas.
  "Cross-Origin-Resource-Policy": "same-origin",
};
