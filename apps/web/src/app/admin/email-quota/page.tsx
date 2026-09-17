import type { Metadata } from "next";

import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

import { EmailQuotaPanel } from "@/components/admin/EmailQuotaPanel";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  return { title: `${t(locale, "admin.title")} · ${t(locale, "admin.section.emailQuota")}` };
}

/** Kunlik email kvota paneli.
 *
 *  Sahifaning o'zi faqat qobiq: ma'lumot client komponentda olinadi
 *  (`/staff/email-quota/`), chunki kun davomida sarf o'zgarib turadi va
 *  sahifani qayta yuklamasdan yangilash kerak bo'ladi.
 *
 *  Django admin paneli bu yerda ISHLAMAYDI: `ADMIN_ENABLED` produksiyada
 *  `False` (o'lchandi 2026-09-17: `/admin/core/emaildelivery/` → 404).
 *  Shuning uchun kvota aynan shu — staff — panelda ko'rsatiladi.
 */
export default function AdminEmailQuotaPage() {
  return <EmailQuotaPanel />;
}
