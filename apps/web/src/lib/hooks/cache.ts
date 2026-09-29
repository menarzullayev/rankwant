/** Server state keshi — hook'dan AJRATILGAN sof mantiq.
 *
 *  ⚠️ **Nega alohida modul.** `useLoad` ni React'siz o'lchab bo'lmaydi
 *  (`@testing-library/react` loyihada yo'q), kesh esa aynan **o'lchashga
 *  arziydigan** qism: dedup xato bo'lsa ortiqcha so'rov ketadi, kesh xato
 *  bo'lsa eskirgan ma'lumot ko'rsatiladi. Ikkisi ham jimgina sodir
 *  bo'ladi. Shuning uchun mantiq shu yerga chiqarildi — `Cache` sof
 *  obyekt, hook esa faqat React qobig'i.
 */

/** Bitta yozuv — tayyor qiymat ham, uchayotgan so'rov ham shu shaklda. */
export type Entry<T> = {
  /** Tayyor javob. `undefined` — hali kelmagan. */
  value?: T;
  /** Hozir uchayotgan so'rov — dedup uchun. */
  promise?: Promise<T>;
  /** Yozuv vaqti (ms) — `isFresh` shunga qaraydi. */
  at: number;
};

/** Kesh — `path` → yozuv. */
export class Cache<T = unknown> {
  private readonly map = new Map<string, Entry<T>>();

  /** Yozuv `staleMs` ichida olinganmi. */
  isFresh(key: string, staleMs: number, now: number = Date.now()): boolean {
    const entry = this.map.get(key);
    if (!entry) return false;
    if (entry.value === undefined) return false;
    return now - entry.at < staleMs;
  }

  /** Tayyor qiymat — yo'q bo'lsa `undefined`. */
  value(key: string): T | undefined {
    return this.map.get(key)?.value;
  }

  /** Uchayotgan so'rov — dedup uchun. */
  promise(key: string): Promise<T> | undefined {
    return this.map.get(key)?.promise;
  }

  /** So'rov uchirilishini qayd etadi. */
  startFlight(key: string, promise: Promise<T>, now: number = Date.now()): void {
    this.map.set(key, { promise, at: now });
  }

  /** Natijani saqlaydi va `promise` maydonini bo'shatadi. */
  settle(key: string, value: T, now: number = Date.now()): void {
    this.map.set(key, { value, at: now });
  }

  /** Xatoni qayd etadi: qiymat yo'q, yozuv o'chiriladi.
   *
   *  ⚠️ Xato KESHLANMAYDI. Sabab: xato ko'pincha vaqtinchalik (tarmoq,
   *  502), ya'ni uni `STALE_MS` saqlash foydalanuvchini shu vaqt ichida
   *  qayta urinishdan mahrum qilardi. Keyingi chaqiruv yana so'raydi. */
  fail(key: string): void {
    this.map.delete(key);
  }

  /** Yozuvni tashlaydi — `reload()` shuni chaqiradi. */
  invalidate(key: string): void {
    this.map.delete(key);
  }

  clear(): void {
    this.map.clear();
  }

  /** Faqat test/diagnostika uchun. */
  size(): number {
    return this.map.size;
  }
}
