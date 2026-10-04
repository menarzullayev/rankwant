/** `auth` — **server** komponentlari yuzasi.
 *
 *  ⚠️ Bu faylni faqat server komponentlari import qilsin. Bu yerdagilar
 *  `@/i18n/server` orqali `next/headers` ga bog'lanadi, ya'ni mijoz
 *  to'plamiga tortilsa build yiqiladi.
 *
 *  Mijoz komponentlari uchun — `@/features/auth`. */

export { AuthShell } from "./components/AuthShell";
export { AuthTabs } from "./components/AuthTabs";
