"use client";

import { AdminNav } from "@/components/admin/AdminNav";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Admin UI — faqat `is_staff`. Haqiqiy himoya API'da (IsAdminUser);
 * bu yerdagi tekshiruv faqat UI ni yashirish uchun. */
export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, ready } = useSession();
  const locale = useLocale();
  if (!ready) return null;
  if (!user?.is_staff) {
    return (
      <Card>
        <p className="text-theme-sm rw-dim">{t(locale, "admin.forbidden")}</p>
      </Card>
    );
  }
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "admin.title")}
        </h1>
        <div className="mt-3">
          <AdminNav />
        </div>
      </div>
      {children}
    </div>
  );
}
