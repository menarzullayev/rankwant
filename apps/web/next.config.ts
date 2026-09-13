import type { NextConfig } from "next";

const config: NextConfig = {
  // SSR — masala va maqola sahifalari SEO uchun serverda render qilinadi
  // (ADR-0003 dagi Next.js tanlovining asosiy sababi).
  reactStrictMode: true,
  typedRoutes: true,  // Next 16 da experimental dan chiqdi
  // Next `next dev` da apps/web/CLAUDE.md va AGENTS.md ni o'zi yozadi.
  // Repoda o'z ko'rsatmalarimiz bor — generatsiya ularni jimgina
  // almashtirib yuborishi mumkin.
  agentRules: false,

  /** Har javobga `Vary: Accept-Language`.
   *
   *  Sabab: `getLocale()` cookie bo'lmasa tilni `Accept-Language`
   *  sarlavhasidan aniqlaydi, ya'ni **bir xil URL turli til qaytaradi**
   *  (o'lchandi: `en`/`ru`/`zh`/`ky`). Bugun bu zararsiz, chunki javob
   *  `no-store` — hech qanday umumiy kesh uni saqlamaydi. Lekin kesh
   *  yoqilsa (CDN, `revalidate`) bu **bir zumda kesh-zaharlash xatosi**
   *  bo'ladi: rus foydalanuvchisining sahifasi ingliz tilida beriladi.
   *
   *  `Vary` keshga «bu javob sarlavhaga bog'liq» deb aytadi. Sarlavhani
   *  `getLocale()` ichida qo'yib bo'lmaydi: u `cookies()` va
   *  `headers()` ni o'qiydigan React keshlangan funksiya, javob
   *  sarlavhalariga yozish huquqi yo'q.
   */
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [{ key: "Vary", value: "Accept-Language" }],
      },
    ];
  },
};

export default config;
