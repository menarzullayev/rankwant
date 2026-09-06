import type { NextConfig } from "next";

const config: NextConfig = {
  // SSR — masala va maqola sahifalari SEO uchun serverda render qilinadi
  // (ADR-0003 dagi Next.js tanlovining asosiy sababi).
  reactStrictMode: true,
  typedRoutes: true,  // Next 16 da experimental dan chiqdi
};

export default config;
