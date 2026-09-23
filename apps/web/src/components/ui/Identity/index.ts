/** Foydalanuvchi identiteti — umumiy primitivlar.
 *
 *  `Avatar`, `UserName`, `MarkerText` bir necha sahifada ishlatiladi
 *  (reyting, standings, urinishlar, izohlar) — ya'ni profil sahifasiga
 *  xos emas. Shuning uchun `features/profile` ichida emas, global
 *  `components/ui` da turadi. */

export { Avatar } from "./Avatar";
export { MarkerText, splitMarker } from "./MarkerText";
export { UserName, rankClass } from "./UserName";
