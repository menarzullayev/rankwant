/** Transport: base URL, pagination envelope, `ApiError` and the fetch helpers. */

/**
 * Brauzer va server bir xil manzildan foydalana olmaydi: brauzer host'dagi
 * `localhost:8000` ni ko'radi, konteyner ichidagi SSR esa u yerda hech
 * nima topmaydi (ECONNREFUSED). Shuning uchun server tomon uchun alohida
 * ichki manzil — sozlanmasa, ommaviy manzilga qaytadi.
 */
export const API_BASE =
  (typeof window === "undefined"
    ? process.env.API_BASE_INTERNAL || process.env.NEXT_PUBLIC_API_BASE
    : process.env.NEXT_PUBLIC_API_BASE) ?? "http://localhost:8000/api/v1";

import { log } from "@/lib/log";

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

/** `Retry-After` sarlavhasini soniyaga aylantiradi (15-qaror).
 *
 *  Sarlavha ikki shaklda bo'ladi: soniya (`"42"`) yoki HTTP-sana.
 *  DRF soniya qo'yadi, lekin oraliq proksi ham qo'shishi mumkin — shu
 *  sababli ikkalasi ham o'qiladi. O'qib bo'lmasa `0`: matn umumiy
 *  qoladi va taymer ko'rsatilmaydi, ya'ni noto'g'ri raqam va'da
 *  qilinmaydi. */
function retryAfterOf(res: Response): number {
  const raw = res.headers.get("Retry-After");
  if (!raw) return 0;
  const seconds = Number(raw);
  if (Number.isFinite(seconds) && seconds > 0) return Math.ceil(seconds);
  const at = Date.parse(raw);
  if (Number.isNaN(at)) return 0;
  return Math.max(0, Math.ceil((at - Date.now()) / 1000));
}

class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    /** Maydon xatolari — `{"email": ["Bu email band"]}`. */
    readonly details: Record<string, unknown> = {},
    /** 429 da server aytgan kutish soniyalari (15-qaror).
     *
     *  `Retry-After` sarlavhasidan: DRF uni o'zi qo'yadi va qancha
     *  kutishni ANIQ aytadi. Sarlavha bo'lmasa `0` — matn umumiy
     *  qoladi va taymer ko'rinmaydi. O'lchandi: ilgari bu qiymat
     *  umuman o'qilmasdi va odam «juda tez-tez» degan xabarni ko'rib,
     *  qancha kutishni bilmasdan qayta bosardi. */
    readonly retryAfter: number = 0,
  ) {
    super(message);
  }

  /**
   * Foydalanuvchiga ko'rsatiladigan matn.
   *
   * API maydon xatosida umumiy «Kiritilgan ma'lumot noto'g'ri» qaytaradi,
   * haqiqiy sabab esa `details` da qoladi — o'lchandi: band username
   * bilan ro'yxatdan o'tganda foydalanuvchi qaysi maydon xato ekanini
   * umuman bilmasdi.
   */
  get text(): string {
    const first = Object.values(this.details)[0];
    if (Array.isArray(first) && typeof first[0] === "string") return first[0];
    if (typeof first === "string") return first;
    return this.message;
  }

  /**
   * Bitta maydonning xatosi, yo'q bo'lsa `null`.
   *
   * NEGA KERAK (14-qaror): DRF maydon xatolarida `code` HAR DOIM
   * `"invalid"` bo'ladi — `{"error":{"code":"invalid","details":{"email":
   * ["Bu email band"]}}}`. Ya'ni «band email» ni kod bo'yicha ajratib
   * bo'lmaydi; yagona ishonchli belgi — `details` kaliti. `text` esa
   * BIRINCHI maydonni oladi, tartib esa DRF'ga bog'liq.
   */
  field(name: string): string | null {
    const value = this.details[name];
    if (Array.isArray(value) && typeof value[0] === "string") return value[0];
    if (typeof value === "string") return value;
    return null;
  }
}

export async function get<T>(path: string, revalidate = 30): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    next: { revalidate },
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    let code = "error";
    let message = res.statusText;
    try {
      const body = await res.json();
      code = body?.error?.code ?? code;
      message = body?.error?.message ?? message;
    } catch {
      /* javob JSON emas */
    }
    throw new ApiError(res.status, code, message, {}, retryAfterOf(res));
  }
  return (await res.json()) as T;
}

/**
 * Brauzerdan sessiya bilan yuboriladigan so'rov — POST, PUT, PATCH, DELETE.
 *
 * `credentials: "include"` shart: sessiya cookie'si boshqa origin'da
 * (API alohida portda), CORS esa `allow-credentials` qaytaradi (ADR-0008).
 * `FormData` yuborilsa `Content-Type` qo'yilmaydi — chegarani (boundary)
 * brauzer o'zi yozadi, qo'lda yozilgani esa faylni buzardi.
 */
async function send<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  // Sessiya bilan yuborilgan so'rovda DRF CSRF token talab qiladi. Anonim
  // login/register da cookie hali yo'q — o'shanda sarlavha ham kerak emas.
  const csrf = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/)?.[1];
  if (csrf) headers["X-CSRFToken"] = decodeURIComponent(csrf);
  const form = body instanceof FormData;
  if (body !== undefined && !form) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    credentials: "include",
    headers,
    body: body === undefined ? undefined : form ? body : JSON.stringify(body),
  });
  // ⚠️ `JSON.parse` XOM chaqirilmaydi. O'lchandi: Cloudflare Tunnel
  // 502 qaytganda tana HTML bo'ladi (`<html>502 Bad Gateway`), ya'ni
  // `JSON.parse` `SyntaxError` tashlardi. Natijada foydalanuvchi
  // «kutilmagan xato» ko'rardi va jurnalda haqiqiy sabab (502) yo'q
  // edi — endpoint umuman ishlamayotgani bilinmasdi.
  //
  // 204 (No Content) va 304 da tana bo'sh — `text()` `""` qaytaradi,
  // ya'ni `raw` bo'sh satr bo'lib qoladi va parse o'tkazib yuboriladi.
  const raw = await res.text();
  let parsed: { error?: { code?: string; message?: string; details?: Record<string, unknown> } } | null =
    null;
  if (raw) {
    try {
      parsed = JSON.parse(raw);
    } catch {
      log.warn("api", "javob JSON emas", {
        path,
        status: res.status,
        body: raw.slice(0, 200),
      });
    }
  }
  if (!res.ok) {
    throw new ApiError(
      res.status,
      parsed?.error?.code ?? "error",
      parsed?.error?.message ?? res.statusText,
      parsed?.error?.details ?? {},
      retryAfterOf(res),
    );
  }
  return parsed as T;
}

export const postJson = <T>(path: string, body: unknown) =>
  send<T>("POST", path, body);

/** Butun ro'yxatni almashtirish — ko'nikma, ta'lim, tashqi profil. */
export const putJson = <T>(path: string, body: unknown) =>
  send<T>("PUT", path, body);

export const patchJson = <T>(path: string, body: unknown) =>
  send<T>("PATCH", path, body);

export const deleteJson = <T>(path: string, body?: unknown) =>
  send<T>("DELETE", path, body);

/** Fayl yuklash — avatar. */
export const postForm = <T>(path: string, form: FormData) =>
  send<T>("POST", path, form);

/** Brauzerdan sessiya bilan GET — shaxsiy ma'lumot (sinf, duel masalalari). */
export async function getJson<T>(
  path: string,
  /** `signal` — yozayotgandagi tekshiruvda eskirgan so'rovni bekor qilish
   *  uchun: javoblar tartibsiz kelib, oxirgisi eskisi bo'lib qolmasin. */
  init?: { signal?: AbortSignal },
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { Accept: "application/json" },
    cache: "no-store",
    signal: init?.signal,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(
      res.status,
      body?.error?.code ?? "error",
      body?.error?.message ?? res.statusText,
      body?.error?.details ?? {},
      retryAfterOf(res),
    );
  }
  return (await res.json()) as T;
}

export { ApiError };
