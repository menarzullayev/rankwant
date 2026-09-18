import { NextResponse, type NextRequest } from "next/server";

import { EXP_COOKIE, GEO_EXPERIMENT } from "@/lib/experiments";
import { SITE_URL } from "@/lib/site";

/** Kanonik manzil — `PUBLIC_ORIGIN` dan (build paytida).
 *
 *  Boshqa ommaviy nom bilan (eski `rankwant.bugvector.uz`, `www.`) kelgan sahifa
 *  so'rovi shu manzilga 301 bilan yo'naltiriladi: eski havola, sertifikatdagi
 *  QR va qidiruv indeksi yangi domenga o'tadi. `/api/*` bu yerga kelmaydi —
 *  tunnel uni to'g'ridan-to'g'ri API'ga beradi, ya'ni eski domendagi avatar
 *  manzillari ishlashda davom etadi. */
const canonical = new URL(SITE_URL);

/** Konteyner ichi, healthcheck, CI (`web:3000`) va lokal ishlab chiqish. */
const INTERNAL = /^(localhost|127\.0\.0\.1|\[::1\]|web|api)(:\d+)?$/;

/** Eksperiment guruhini belgilaydi — bir marta, keyin cookie'da qoladi.
 *
 *  Nega SERVERDA: mijozda tasodifiy tanlansa, har sahifa yuklanishida
 *  guruh o'zgarib ketardi va bir odam ikki guruhda ham hisoblanardi —
 *  ya'ni o'lchov ma'nosini yo'qotardi.
 *
 *  `crypto.getRandomValues` — `Math.random` emas: guruhlar teng
 *  bo'lishi kerak, `Math.random` taqsimoti esa kafolatlanmagan.
 */
function assignExperiments(request: NextRequest, response: NextResponse): void {
  if (request.cookies.has(EXP_COOKIE)) return;
  const byte = new Uint8Array(1);
  crypto.getRandomValues(byte);
  response.cookies.set(EXP_COOKIE, `${GEO_EXPERIMENT}:${byte[0] < 128 ? "a" : "b"}`, {
    path: "/",
    maxAge: 60 * 60 * 24 * 180,
    sameSite: "lax",
    // `HttpOnly` ATAYLAB emas: mijoz formani guruhga qarab chizadi.
    // Bu xavfsiz — guruh qiymati hech qanday huquq bermaydi.
    httpOnly: false,
  });
}

export function proxy(request: NextRequest): NextResponse {
  const host = request.headers.get("host") ?? "";
  // Faqat haqiqiy ommaviy sayt (https): lokal va CI build'larda yo'naltirish yo'q.
  const boshqa_domen =
    canonical.protocol === "https:" &&
    !!host &&
    host !== canonical.host &&
    !INTERNAL.test(host);

  const response = boshqa_domen
    ? NextResponse.redirect(
        new URL(`${request.nextUrl.pathname}${request.nextUrl.search}`, canonical),
        301,
      )
    : NextResponse.next();

  // `Vary: Accept-Language` — javob tilga bog'liq bo'lganda MAJBURIY.
  //
  // ⚠️⚠️ O'LCHANDI VA BU YERDA HAM ISHLAMAYDI — Next.js 16 `Vary` ni
  // javob chizig'ining ENG OXIRIDA o'z ro'yxati bilan ALMASHTIRADI:
  //
  //     Vary: rsc, next-router-state-tree, next-router-prefetch,
  //           next-router-segment-prefetch, Accept-Encoding
  //
  // Uch joy sinaldi va uchalasi ham o'lchov bilan rad etildi:
  //   1. `next.config.ts` `headers()` — qoida `routes-manifest.json` ga
  //      yoziladi (tekshirildi), javobda esa yo'q.
  //   2. shu fayl (proxy) — `x-rw-probe: alive` omon qoladi, `Vary` esa
  //      yo'q. Ya'ni proxy ISHLAYDI; klobbers faqat `Vary` ga tegishli.
  //   3. `set()` o'rniga `append()` — "qiymat almashtiriladi, ro'yxat
  //      saqlanadi" degan gipoteza. O'LCHANDI: javob (2) bilan AYNAN bir
  //      xil. Ya'ni almashtirish SHARTSIZ va KALIT darajasida — Next.js
  //      ichida header qo'shib bo'lmaydi, tuzatish tashqarida bo'lishi
  //      shart.
  //
  // Bu Next.js'ning ichki xatti-harakati, hujjatda yozilmagan
  // (`/docs/app/api-reference/file-conventions/proxy` da `Vary` umuman
  // tilga olinmaydi; `headers()` konfiguratsiya sahifasida ham yo'q).
  //
  // NEGA HOZIR ZARARSIZ: javob `Cache-Control: private, no-cache,
  // no-store, max-age=0, must-revalidate` bilan keladi (o'lchandi) —
  // ya'ni hech qanday umumiy kesh uni saqlay olmaydi. Xat xavfi
  // KESHLASH YOQILGAN KUNI paydo bo'ladi.
  //
  // TODO(keshlashdan OLDIN): `Vary` ni Next.js'dan TASHQARIDA qo'shish
  // kerak — cloudflared tunnel ingress header rewrite qo'llamaydi
  // (o'lchandi: `cloudflared 2026.9.1`, bunday direktiva yo'q), ya'ni
  // oldiga kichik proxy qo'yiladi yoki CDN darajasida Transformation
  // Rule yoziladi. Batafsil: `docs/08-technical-spec/i18n-precedence.md`.
  if (!boshqa_domen) {
    response.headers.set("Vary", "Accept-Language");
  }

  // Guruh yo'naltirishda ham belgilanadi: eski domendan kelgan birinchi
  // so'rov yangisiga o'tadi, cookie esa shu javobda qo'yiladi.
  assignExperiments(request, response);
  return response;
}

export const config = {
  // `i18n/` holds the static dictionary files (`app/i18n/[file]/route.ts`).
  // Through here they would get `Vary: Accept-Language` and possibly an
  // experiment cookie, and a CDN keeps neither kind of response. Their
  // content never depends on the request.
  matcher: ["/((?!_next/static|_next/image|favicon.ico|i18n/).*)"],
};
