/** Manbadagi daraja (ADR-0026) — Codeforces'ning kanonik ranglari.
 *
 * RankWant'ning o'z unvoni (`title`) 9 daraja va u `rw-rank-N` sinflari
 * bilan chiziladi. Bu yerdagi daraja **saqlanadi**, hisoblanmaydi, va
 * 10 daraja. Ikkisi bir xil nom bilan chiqsa frontend chalkashardi —
 * shuning uchun alohida fayl va alohida nom (`cf`).
 */

/** 10 daraja — pastdan yuqoriga. Indeks = daraja raqami (1..10). */
export const CF_TIERS = [
  "newbie",
  "pupil",
  "specialist",
  "expert",
  "candidate master",
  "master",
  "international master",
  "grandmaster",
  "international grandmaster",
  "legendary grandmaster",
] as const;

export type CfTier = (typeof CF_TIERS)[number];

/** Kichik harflarga keltirib tekshiradi (manba shunday qaytaradi). */
export function isCfTier(value: string): value is CfTier {
  return (CF_TIERS as readonly string[]).includes(value.toLowerCase());
}

/** Ranglar — Codeforces saytining o'z palitrasi (kanonik).
 *
 * `text` va `border` alohida: fonda emas, matn va chegara sifatida
 * ishlatiladi, shuning uchun qorong'i mavzuda ham o'qiladi.
 */
export const CF_TIER_COLOR: Record<CfTier, string> = {
  newbie: "#808080",
  pupil: "#008000",
  specialist: "#03a89e",
  expert: "#0000ff",
  "candidate master": "#aa00aa",
  master: "#ff8c00",
  "international master": "#ff8c00",
  grandmaster: "#ff0000",
  "international grandmaster": "#ff0000",
  "legendary grandmaster": "#ff0000",
};

/** i18n kaliti — har daraja uchun tarjima (`cfTier.*`). */
export function cfTierLabelKey(tier: string): string {
  return `cfTier.${tier.replace(/ /g, "")}`;
}
