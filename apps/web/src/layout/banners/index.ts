/** Ilova qobig'i bannerlari — `AppShell` yuqorisida ko'rinadi.
 *
 *  ⚠️ Nega `layout/` da, feature ichida emas: bu bannerlar **sahifaga
 *  emas, butun ilovaga** tegishli. Ular sessiyaga va global holatga
 *  qarab chiziladi (`VerifyBanner` — pochta tasdiqlanmagan,
 *  `WelcomeNotice` — ro'yxatdan o'tish 1-bosqichi, `GeoNudge` — mamlakat
 *  bo'sh, `ContestInvite` — tashqi platforma taklifi).
 *
 *  Ilgari ular `features/account` va `features/contests` ichida edi va
 *  natijada `layout/AppShell` (global qatlam) feature'larga bog'lanib
 *  qolardi — ya'ni pastdagi qatlam yuqoridagini bilardi. Bu 25-prinsipning
 *  layer qoidasini buzar edi. */

export { ContestInvite } from "./ContestInvite";
export { GeoNudge } from "./GeoNudge";
export { VerifyBanner } from "./VerifyBanner";
export { WelcomeNotice } from "./WelcomeNotice";
