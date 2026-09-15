/** Saytning OMMAVIY manzili — sitemap, canonical va Open Graph uchun.
 *
 * Nisbiy manzil ular uchun yaramaydi: sitemap to'liq URL talab qiladi va
 * Telegram ulashilgan havolani ko'rsatishda ham to'liq manzilni kutadi.
 *
 * `NEXT_PUBLIC_API_BASE` allaqachon `<origin>/api/v1` shaklida beriladi
 * (docker-compose.public.yml), shuning uchun origin o'shandan olinadi va
 * yangi sozlama kiritilmaydi.
 */
function fromApiBase(): string | null {
  const raw = process.env.NEXT_PUBLIC_API_BASE;
  if (!raw) return null;
  try {
    return new URL(raw, "http://localhost").origin;
  } catch {
    return null;
  }
}

export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/$/, "") ??
  fromApiBase() ??
  "http://localhost:3000";

export function absolute(path: string): string {
  return new URL(path, SITE_URL).toString();
}

/** Whether search engines and AI crawlers may index the site.
 *
 * `false` until launch. On 2026-09-15 crawlers sent ~246k requests a day
 * (82% GPTBot, 16% Google), mostly to the profiles of 10,001 seeded
 * `neytron_*` users, and used up the daily Cloudflare Workers quota.
 * Flip to `true` at launch: `robots.ts` reopens with the sitemap and the
 * root layout drops `noindex`.
 */
export const SITE_INDEXABLE = false;

/** `?next=` qiymatini xavfsiz ICHKI yo'lga aylantiradi.
 *
 * Qiymat ishonchsiz: uni har kim manzil qatorida tahrirlay oladi, ya'ni
 * tekshirilmasa sayt «ochiq redirect» beradigan bo'lib qoladi —
 * `rankwant.uz/login?next=https://soxta-sayt.uz` ga o'xshash havolani
 * firibgar yuborishi mumkin, odam esa manzilga ishonib kiradi.
 *
 * Rad etiladigan shakllar:
 *   `https://evil.com` — mutlaq manzil;
 *   `//evil.com`       — protokol-nisbiy, brauzer boshqa sayt deb o'qiydi;
 *   `/\evil.com`       — ba'zi brauzerlar buni ham tashqi deb hisoblaydi.
 *
 * Ya'ni oq ro'yxat emas, QAT'IY shakl tekshiruvi: bitta `/` bilan
 * boshlanadigan yo'l. Rad etilganda `null` — chaqiruvchi standart
 * manzilga o'tadi.
 */
/** `application/ld+json` blokining ichki matni.
 *
 *  ⚠️ `JSON.stringify` `<` belgisini qochirmaydi. Sarlavha `</script>`
 *  o'z ichiga olsa blok shu yerda uzilib, qolgan sahifa matn sifatida
 *  ko'rinadi — yoki yomonroq. Sarlavhalar API'dan keladi (musobaqa,
 *  masala), ya'ni bu nazariy xavf emas. `\u003c` JSON ichida xuddi shu
 *  belgi, lekin skript blokini buza olmaydi.
 */
export function jsonLd(data: unknown): string {
  return JSON.stringify(data).replace(/</g, "\\u003c");
}

export function safeNext(value: string | null | undefined): string | null {
  if (!value || !value.startsWith("/")) return null;
  if (value.startsWith("//") || value.startsWith("/\\")) return null;
  return value;
}
