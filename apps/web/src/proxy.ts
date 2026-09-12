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

  // Guruh yo'naltirishda ham belgilanadi: eski domendan kelgan birinchi
  // so'rov yangisiga o'tadi, cookie esa shu javobda qo'yiladi.
  assignExperiments(request, response);
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
