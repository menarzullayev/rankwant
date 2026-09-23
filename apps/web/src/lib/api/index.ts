/** RankWant API mijozi — barqaror kirish nuqtasi.
 *
 * SSR da server tomonda chaqiriladi — session cookie uzatiladi
 * (ADR-0008: birinchi tomon web uchun cookie, PAT emas).
 *
 * ## Qatlam
 *
 * Domen bo'yicha API funksiyalari endi o'z feature'i ichida yashaydi
 * (`features/<dom>/api/`), chunki ular o'sha domenning tip va
 * komponentlari bilan birga o'zgaradi. Masalan `problems` API'si
 * `features/problems/` da.
 *
 * Bu fayl — **yagona kirish nuqtasi**: `@/lib/api` import yo'li
 * o'zgarmaydi, ya'ni ko'chirish chaqiruvchilarga ko'rinmaydi.
 * Sabab (ADR-0009, monorepo qarori): repo tuzilishi o'zgarsa ham
 * import yo'li barqaror qolishi kerak — aks holda har ko'chirish
 * o'nlab faylni tahrirlashni talab qiladi.
 *
 * Infratuzilma shu yerda qoladi: `client.ts` (HTTP, `ApiError`),
 * `endpoints.ts` (`api` obyekti), `content.ts` va `platform.ts`
 * (bir necha domenni qamraydi, ya'ni bitta feature'ga tegishli emas).
 */

// `get` and `send` remain private to this package, as they were before the split.
export {
  API_BASE,
  ApiError,
  deleteJson,
  getJson,
  patchJson,
  postForm,
  postJson,
  putJson,
} from "./client";
export type { Paginated } from "./client";

// Domen API'lari — o'z feature'i ichidan qayta eksport.
export * from "@/features/account/api/account";
export * from "@/features/account/api/qvant";
export * from "@/features/profile/api/users";
export * from "@/features/problems/api/problems";
export * from "@/features/contests/api/contests";
export * from "@/features/hackathons/api/hacks";

// Domenlararo — shu qatlamda qoladi.
export * from "./content";
export * from "./platform";
export { api } from "./endpoints";
