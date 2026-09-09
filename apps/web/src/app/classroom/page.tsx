import type { Metadata } from "next";

import { ClassroomHub } from "@/components/ClassroomHub";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.classroom") };
}

export default async function ClassroomPage() {
  const locale = await getLocale();
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {t(locale, "nav.classroom")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm rw-dim">
          O&apos;qituvchi sinf yaratadi, o&apos;quvchilar kod bilan
          qo&apos;shiladi, uy vazifasi va progress bir joyda.
        </p>
      </header>
      <ClassroomHub />
    </div>
  );
}
