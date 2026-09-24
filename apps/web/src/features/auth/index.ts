/** `auth` — ommaviy yuzasi (**mijoz xavfsiz**).
 *
 *  ⚠️ Bu barrel FAQAT `"use client"` komponentlarni chiqaradi.
 *
 *  Nega ajratilgan: `AuthTabs`, `AuthShell`, `AuthProof` — server
 *  komponentlari (`@/i18n/server` → `next/headers` ishlatadi). Ular
 *  shu barrel orqali chiqsa, mijoz komponenti (`AuthForm`) barrel'ni
 *  import qilganda butun `next/headers` zanjiri mijoz to'plamiga
 *  tortiladi va build yiqiladi:
 *
 *      You're importing a module that depends on "next/headers".
 *
 *  Server komponentlari — `@/features/auth/server`.
 *
 *  Bu umumiy qoida: **bir barrel mijoz va serverni aralashtirmasin.** */

export { Turnstile } from "./components/Turnstile";
