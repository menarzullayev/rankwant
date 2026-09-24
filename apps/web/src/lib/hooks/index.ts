/** `lib/hooks` — feature'lar orasida bo'lishiladigan sof hook'lar.
 *
 * Bu yerdagi hook'lar **hech qanday feature'ni bilmaydi**. Aksincha:
 * feature'lar shu yerdan import qiladi. Shunday qilib umumiy mantiq
 * `features/account` kabi birorta feature ichida qolib ketmaydi.
 */

export { Cache, type Entry } from "./cache";
export { describeError, useAction } from "./useAction";
export { clearLoadCache, loadCacheSize, useLoad, type LoadOptions } from "./useLoad";
