import Link from "next/link";
import type { Metadata } from "next";

import { ADMIN_SECTIONS } from "@/components/admin/sections";
import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Admin" };

export default async function AdminIndex() {
  const locale = await getLocale();
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {ADMIN_SECTIONS.map((s) => (
        <Link key={s.href} href={s.href}>
          <Card>
            <p className="font-semibold rw-strong">
              {t(locale, s.labelKey)}
            </p>
          </Card>
        </Link>
      ))}
    </div>
  );
}
