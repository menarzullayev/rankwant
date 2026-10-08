"use client";

import { AdminNav } from "@/components/admin/AdminNav";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** The heading and the section menu every admin page sits under. */
export function AdminFrame({ children }: { children: React.ReactNode }) {
  const locale = useLocale();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "admin.title")}</h1>
        <div className="mt-3">
          <AdminNav />
        </div>
      </div>
      {children}
    </div>
  );
}
