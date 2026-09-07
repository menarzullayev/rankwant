import type { Metadata } from "next";

import { ClassroomHub } from "@/components/ClassroomHub";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export const metadata: Metadata = { title: "Auditoriya" };

export default function ClassroomPage() {
  const locale = DEFAULT_LOCALE;
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">
          {t(locale, "nav.classroom")}
        </h1>
        <p className="mt-2 max-w-2xl text-theme-sm text-gray-500 dark:text-gray-400">
          O&apos;qituvchi sinf yaratadi, o&apos;quvchilar kod bilan qo&apos;shiladi, uy vazifasi va progress bir joyda.
        </p>
      </header>
      <ClassroomHub />
    </div>
  );
}
