"use client";

import { KitSection } from "@/components/kit/KitPlayground";
import { IconGallery } from "@/components/customizer/IconGallery";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Design-system lab — not the contestant customizer. */
export default function AdminKitPage() {
  const locale = useLocale();
  return (
    <div className="mx-auto max-w-3xl space-y-8 py-6">
      <header>
        <h1 className="text-theme-xl font-semibold rw-strong">
          {t(locale, "admin.kit.title")}
        </h1>
        <p className="mt-2 text-theme-sm rw-dim">{t(locale, "admin.kit.hint")}</p>
      </header>
      <KitSection />
      <IconGallery />
    </div>
  );
}
