/** Do'kondagi kosmetika — kod → ko'rinish.
 *
 * `ShopItem.asset_ref` hozircha bo'sh: rasm fayli yo'q, muqova va ramka
 * CSS bilan chiziladi (`globals.css`, «Profil kosmetikasi»). Noma'lum kod
 * (do'konga yangi narsa qo'shilib, bu yer yangilanmagan bo'lsa) standart
 * ko'rinishga tushadi — bo'sh joy yoki xato emas.
 */

const COVERS: Record<string, string> = {
  "cover-night": "rw-cover-night",
  "cover-steppe": "rw-cover-steppe",
};

const FRAMES: Record<string, string> = {
  "frame-bronze": "rw-frame-bronze",
  "frame-silver": "rw-frame-silver",
  "neytron-ramka": "rw-frame-neytron",
};

const BADGES: Record<string, string> = {
  "badge-solver": "Solver",
};

export const coverClass = (code: string | null) =>
  (code && COVERS[code]) || "rw-cover";

/** Do'kon ramkasi ustun; kiyilmagan bo'lsa unvon ramkasi (ADR-0018). */
export const frameClass = (
  code: string | null,
  title?: { colour_group: string } | null,
) => (code && FRAMES[code]) || (title ? `rw-frame-${title.colour_group}` : "");

export const badgeLabel = (code: string | null) =>
  code ? (BADGES[code] ?? code) : null;

/** Do'kon turkumi → profildagi joy. */
export const SLOT_OF: Record<string, "cover" | "frame" | "badge"> = {
  profile_cover: "cover",
  avatar_frame: "frame",
  username_badge: "badge",
};
