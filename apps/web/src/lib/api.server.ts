import "server-only";

import { cookies } from "next/headers";

import { API_BASE, ApiError } from "./api";

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
