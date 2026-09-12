/** Auth funnel hodisalari (qaror 17).
 *
 * Hodisalar YIG'ILADI va partiya bo'lib yuboriladi: har biri uchun
 * alohida so'rov yuborilsa mobil tarmoqda ularning bir qismi yo'qolardi
 * va sahifa yuklanishini sekinlashtirardi.
 *
 * `sendBeacon` ATAYLAB ishlatilmaydi: u sarlavha qo'ya olmaydi, ya'ni
 * kirgan foydalanuvchida DRF ning CSRF tekshiruvi yiqilardi. Buning
 * o'rniga `fetch(..., { keepalive: true })` — sahifa yopilayotganda ham
 * so'rov yetib boradi.
 */

import { API_BASE } from "./api";

const ENDPOINT = `${API_BASE}/analytics/events/`;
const MAX_BATCH = 25;
const FLUSH_MS = 1500;

type Tracked = { name: string; path: string; props?: Record<string, unknown> };

let queue: Tracked[] = [];
let timer: ReturnType<typeof setTimeout> | null = null;

function csrfToken(): string {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

function flush() {
  timer = null;
  if (queue.length === 0) return;

  const events = queue.splice(0, MAX_BATCH);
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = csrfToken();
  if (token) headers["X-CSRFToken"] = token;

  fetch(ENDPOINT, {
    method: "POST",
    headers,
    body: JSON.stringify({ events }),
    keepalive: true,
    credentials: "include",
  }).catch(() => {
    // Funnel yiqilishi foydalanuvchiga KO'RINMASLIGI kerak: hodisa
    // yo'qoladi, sahifa esa ishlashda davom etadi.
  });

  if (queue.length > 0) schedule();
}

function schedule() {
  if (timer) return;
  timer = setTimeout(flush, FLUSH_MS);
}

/** Hodisani navbatga qo'shadi. Yuborish biroz kechiktiriladi, ya'ni
 *  ketma-ket hodisalar (forma boshlandi → xato → yuborildi) bitta
 *  so'rovda ketadi. */
export function track(name: string, props?: Record<string, unknown>) {
  if (typeof window === "undefined") return;
  queue.push({ name, path: window.location.pathname, props });
  schedule();
}

/** Sahifa yopilishidan oldin navbatni bo'shatadi — `visibilitychange`
 *  ishlatiladi (`unload` mobil brauzerlarda ishonchsiz). */
if (typeof window !== "undefined") {
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden" && queue.length > 0) flush();
  });
}
