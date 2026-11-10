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
import { experimentGroup } from "./flags";

const ENDPOINT = `${API_BASE}/analytics/events/`;
const MAX_BATCH = 25;
const FLUSH_MS = 1500;

type Tracked = { name: string; path: string; props?: Record<string, unknown> };

let queue: Tracked[] = [];
let timer: ReturnType<typeof setTimeout> | null = null;

/** This tab's funnel id — 32 random hex digits, kept for the tab's life.
 *
 *  A visitor who has not signed in has no server session, so every one of
 *  their events reached the table with an EMPTY `session_key` and all of
 *  them counted as one "session". Measured in production 2026-11-10: 34 of
 *  38 `auth.form_started` rows were blank — the funnel's first step read 1
 *  whatever the traffic. The server files an event under `f:<id>` when it
 *  has no session of its own; the id names a tab, not a person, and is not
 *  stored in `props`. */
const FUNNEL_KEY = "rw:funnel";
let funnelId: string | null = null;

function newFunnelId(): string {
  // `getRandomValues`, not `randomUUID`: the latter needs a secure context.
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

function funnel(): string {
  if (funnelId) return funnelId;
  let kept: string | null = null;
  try {
    kept = sessionStorage.getItem(FUNNEL_KEY);
  } catch {
    // Storage blocked: one id per page load is still far better than none.
  }
  funnelId = kept && /^[0-9a-f]{32}$/.test(kept) ? kept : newFunnelId();
  try {
    sessionStorage.setItem(FUNNEL_KEY, funnelId);
  } catch {
    // As above.
  }
  return funnelId;
}

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
 *  so'rovda ketadi.
 *
 *  Eksperiment guruhi hodisaga FAQAT sinov ishlayotganda qo'shiladi
 *  (`NEXT_PUBLIC_FLAG_GEO_EARLY_REGION` yoniq va cookie'da guruh bor):
 *  usiz A/B natijasini hodisalardan ajratib bo'lmasdi. Ilgari guruh har
 *  doim yozilardi, cookie yo'q bo'lsa esa `a` deb — sinov o'chiq paytda
 *  ikkala guruh bir xil formani ko'rgan hodisalar ham, guruhsiz
 *  tashrifchilar ham natijaga aralashardi.
 */
export function track(name: string, props?: Record<string, unknown>) {
  if (typeof window === "undefined") return;
  const group = experimentGroup("geoEarlyRegion");
  queue.push({
    name,
    path: window.location.pathname,
    props: { ...props, fid: funnel(), ...(group ? { exp: group } : {}) },
  });
  schedule();
}

/** Sahifa yopilishidan oldin navbatni bo'shatadi — `visibilitychange`
 *  ishlatiladi (`unload` mobil brauzerlarda ishonchsiz). */
if (typeof window !== "undefined") {
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden" && queue.length > 0) flush();
  });
}
