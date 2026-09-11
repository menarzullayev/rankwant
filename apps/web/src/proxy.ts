import { NextResponse, type NextRequest } from "next/server";

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

export function proxy(request: NextRequest): NextResponse {
  const host = request.headers.get("host") ?? "";
  // Faqat haqiqiy ommaviy sayt (https): lokal va CI build'larda yo'naltirish yo'q.
  if (
    canonical.protocol !== "https:" ||
    !host ||
    host === canonical.host ||
    INTERNAL.test(host)
  ) {
    return NextResponse.next();
  }
  const target = new URL(`${request.nextUrl.pathname}${request.nextUrl.search}`, canonical);
  return NextResponse.redirect(target, 301);
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
