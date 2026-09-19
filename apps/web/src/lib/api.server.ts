import "server-only";

import { cookies } from "next/headers";

import { API_BASE, ApiError } from "./api";
import { SESSION_COOKIE } from "./home-cache";

/**
 * SSR da shaxsiy ma'lumot uchun GET.
 *
 * `api.ts` dagi `get()` cookie uzatmaydi — u ochiq va keshlanadigan
 * ma'lumot uchun. Shu sababli tavsiya kabi sessiyaga bog'liq chaqiriqlar
 * serverda har doim 401 olardi va sahifada jimgina yo'qolardi. Bu yerda
 * kiruvchi so'rovning cookie'si uzatiladi, kesh esa o'chiriladi:
 * javob foydalanuvchiga xos.
 */
export async function getWithSession<T>(path: string): Promise<T> {
  const jar = await cookies();
  const header = jar
    .getAll()
    .map((c) => `${c.name}=${c.value}`)
    .join("; ");

  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    headers: header
      ? { Accept: "application/json", Cookie: header }
      : { Accept: "application/json" },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(
      res.status,
      body?.error?.code ?? "error",
      body?.error?.message ?? res.statusText,
    );
  }
  return (await res.json()) as T;
}

/**
 * SSR da joriy foydalanuvchini o'qiydi; anonim bo'lsa `null`.
 *
 * Cookie yo'q bo'lsa so'rov UMUMAN yuborilmaydi. Sabab: `/me/`
 * `IsAuthenticated` talab qiladi, ya'ni anonim tashrifchiga 401 qaytaradi.
 * Bu javob to'g'ri, lekin brauzer uni konsolga xato qilib yozadi va
 * Lighthouse `errors-in-console` auditini yiqitadi (o'lchandi: Best
 * Practices 96). Cookie bor bo'lsa foydalanuvchi SSR dayoq ma'lum bo'ladi
 * va mijoz mount'da ortiqcha so'rov yubormaydi — ya'ni bu shunchaki
 * ogohlantirishni yashirish emas, bitta aylanma yo'lni ham yo'q qiladi.
 */
export async function getSessionUser<T>(): Promise<T | null> {
  const jar = await cookies();
  if (!jar.has(SESSION_COOKIE)) return null;
  return getWithSession<T>("/me/").catch(() => null);
}
