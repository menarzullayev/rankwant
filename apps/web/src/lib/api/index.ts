/** RankWant API mijozi.
 *
 * SSR da server tomonda chaqiriladi — session cookie uzatiladi
 * (ADR-0008: birinchi tomon web uchun cookie, PAT emas).
 */

// The module was split by domain; `@/lib/api` stays the only import path.
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
export * from "./account";
export * from "./users";
export * from "./problems";
export * from "./hacks";
export * from "./contests";
export * from "./content";
export * from "./platform";
export * from "./qvant";
export { api } from "./endpoints";
