/** Combobox qidiruvi — variant matni, kalit so'zlar, kod.

 *  Headless UI dan AJRATILGAN: filtrni test qilish uchun DOM kerak emas.
 */

export type SearchableOption = {
  value: string;
  label: string;
  keywords?: string;
  hint?: string;
  group?: string;
};

export function optionNeedle(option: SearchableOption): string {
  return `${option.label} ${option.keywords ?? ""} ${option.hint ?? ""} ${option.group ?? ""} ${option.value}`.toLowerCase();
}

export function filterDropdownOptions<T extends SearchableOption>(
  options: readonly T[],
  query: string,
): T[] {
  const needle = query.trim().toLowerCase();
  if (!needle) return [...options];
  return options.filter((option) => optionNeedle(option).includes(needle));
}

/** Guruh tartibi manba ro'yxatdagi birinchi uchrashuvga teng. */
export function groupDropdownOptions<T extends SearchableOption>(
  options: readonly T[],
): { group?: string; options: T[] }[] {
  const order: (string | undefined)[] = [];
  const buckets = new Map<string | undefined, T[]>();
  for (const option of options) {
    const group = option.group;
    if (!buckets.has(group)) {
      buckets.set(group, []);
      order.push(group);
    }
    buckets.get(group)!.push(option);
  }
  return order.map((group) => ({ group, options: buckets.get(group)! }));
}
