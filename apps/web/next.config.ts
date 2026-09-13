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
};

export default config;
