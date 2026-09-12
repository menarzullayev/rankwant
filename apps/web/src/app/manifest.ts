import type { MetadataRoute } from "next";

import { SITE_URL } from "@/lib/site";

/** PWA manifesti — telefonga "bosh ekranga qo'shish" uchun.
 *
 * Ikonkalar bu yerda YARATILMAYDI: ular `tools/brand.py` bilan bitta
 * SVG dan generatsiya qilinadi va `public/brand/` da turadi. Ikki joyda
 * saqlansa, logotip o'zgarganda biri eskirib qolardi.
 *
 * `background_color` — ilova ochilishidagi fon. Sayt standart holatda
 * QORONG'I mavzuda ochiladi (`layout.tsx` dagi `THEME_INIT`), shuning
 * uchun brend navy'si olinadi: oq fon bir zum yonib o'chgan kabi
 * ko'rinardi.
 */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "RankWant — reyting xohlaganlar uchun",
    short_name: "RankWant",
    description:
      "Sport dasturlash va informatika olimpiadasi platformasi: " +
      "masala arxivi, musobaqa va ochiq reyting.",
    start_url: "/",
    scope: "/",
    display: "standalone",
    background_color: "#102038",
    theme_color: "#102038",
    lang: "uz",
    id: SITE_URL,
    icons: [
      {
        src: "/brand/mark-192.png",
        sizes: "192x192",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/brand/mark-512.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
    ],
  };
}
