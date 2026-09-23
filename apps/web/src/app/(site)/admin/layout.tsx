"use client";

import { AdminNav } from "@/components/admin/AdminNav";
import { Can, Forbidden } from "@/components/kit/Can";
import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Admin UI — faqat `is_staff`. Haqiqiy himoya API'da (IsAdminUser);
 * bu yerdagi tekshiruv faqat UI ni yashirish uchun. */
export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale = useLocale();
  return (
    <Can
      perm="staff"
      fallback={
        <Card>
          <Forbidden />
        </Card>
      }
    >
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
    </Can>
  );
}
