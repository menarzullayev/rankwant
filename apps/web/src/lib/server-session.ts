import { cookies } from "next/headers";

import { API_BASE } from "@/lib/api";

/** Server komponentida joriy sessiya bor-yo'qligi.
 *
 * `fetch` serverda brauzerning cookie'larini O'ZI uzatmaydi — ular
 * qo'lda qo'shiladi. Shu sababli bu `lib/api.ts` da emas: u yerda
 * `next/headers` bo'lsa mijoz bundle'i yig'ilmay qolardi.
 *
 * Faqat «kirganmi» degan savolga javob beradi: kirish sahifalari uchun
 * shundan ortig'i kerak emas va tarmoq yiqilsa sahifa baribir ochiladi.
 */
export async function isSignedIn(): Promise<boolean> {
  const cookie = (await cookies()).toString();
  if (!cookie) return false;
  try {
    const res = await fetch(`${API_BASE}/me/`, {
      headers: { Accept: "application/json", cookie },
      cache: "no-store",
    });
    return res.ok;
  } catch {
    return false;
  }
}
