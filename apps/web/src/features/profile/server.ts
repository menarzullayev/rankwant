/** `profile` — **server** komponentlari yuzasi.
 *
 *  ⚠️ Faqat server komponentlari import qilsin. Bu yerdagilar
 *  `@/lib/api.server` orqali `next/headers` ga bog'lanadi.
 *
 *  Mijoz komponentlari uchun — `@/features/profile`. */

export { AchievementsTab, ActivityTab, PeopleTab, PurchasesTab } from "./components/ActivityTabs";
export { CertificateCard, CertificatesTab } from "./components/CertificatesTab";
