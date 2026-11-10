/** "49000" → "49 000": the same in Node and every browser, unlike
 *  `toLocaleString`, whose ICU data differs and breaks hydration. */
export function groupDigits(amount: number): string {
  return String(Math.round(amount)).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

/** Whole percent off a struck-through price, or 0 without one. */
export function discountPercent(amount: number, listAmount: number): number {
  if (!listAmount || listAmount <= amount) return 0;
  return Math.round(100 * (1 - amount / listAmount));
}
