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
