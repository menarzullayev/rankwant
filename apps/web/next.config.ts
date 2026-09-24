import path from "node:path";
import { fileURLToPath } from "node:url";

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
  turbopack: {
    // ⚠️⚠️ ENG MUHIM QATOR — `turbopack.root` = REPO ILDIZI.
    //
    // Next'ning o'z tipida shunday yozilgan (`config-shared.d.ts:178`):
    //
    //     /** This is the repo root usually and only files above this
    //      *  directory can be resolved by turbopack. */
    //     root?: string;
    //
    // Ya'ni Turbopack FAQAT shu papka ICHIDAGI fayllarni hal qiladi.
    // `next.config.ts` `apps/web` da bo'lsa, root ham `apps/web` bo'ladi
    // va `../../packages/shared/src/format.ts` — undan TASHQARIDA —
    // rad etiladi. Natijada o'lchangan xato (2026-09-24, Linux
    // konteynerida 17 marta):
    //
    //     Error: Module not found: Can't resolve '@rankwant/shared/format'
    //
    // Buning ustiga `node_modules` resolver chegarasi ham shu: `next`
    // ichki `postcss` i o'z bog'liqliklarini (hoist qilingan
    // `picocolors`/`nanoid`/`source-map-js`) topa olmasdi. Root kengaygach
    // ikkala muammo ham bir yo'la yopiladi.
    //
    // Windows'dagi mahalliy build bu farqni YASHIRGAN — u yerda Next
    // root'ni monorepo ildizi deb aniqlagan. Shu sababli xato faqat
    // Docker/CI da ko'rindi.
    //
    // `__dirname` ESM'da yo'q. `new URL(...).pathname` Windows'da
    // `/C:/...` beradi — buzuq yo'l. `fileURLToPath` ikkala
    // platformada ham to'g'ri ishlaydi.
    root: path.join(path.dirname(fileURLToPath(import.meta.url)), "..", ".."),
  },
  // Homepage Lighthouse (2026-09-20, Slow 4G lab): two render-blocking
  // `/_next/static/chunks/*.css` links (~4.5 KiB + 23 KiB, ~150 ms each)
  // sat in front of FCP. App Router cannot use `optimizeCss`/Critters
  // (streaming). `inlineCss` puts those sheets in `<style>` so the extra
  // request is gone. Trade-off: CSS is not cached apart from HTML.
  // Owner HITL 2026-09-20: first lever toward Performance 100.
  experimental: {
    inlineCss: true,
  },
};

export default config;
