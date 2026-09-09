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
