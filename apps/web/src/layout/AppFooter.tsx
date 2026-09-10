"use client";

import Link from "next/link";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Huquqiy havolalar. Ular saytning HAR sahifasida turishi kerak:
 *  Google OAuth tasdig'i maxfiylik siyosati manzilini talab qiladi va
 *  uni topib bo'ladigan joyda kutadi (ADR-0016). */
export default function AppFooter() {
  const locale = useLocale();
  return (
    <footer className="mx-auto max-w-[1400px] px-4 pb-8 pt-2 md:px-6">
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 border-t rw-line pt-5 text-theme-xs rw-dim">
        <span>RankWant</span>
        <Link href="/shartlar" className="hover:underline">
          {t(locale, "footer.terms")}
        </Link>
        <Link href="/maxfiylik" className="hover:underline">
          {t(locale, "footer.privacy")}
        </Link>
      </div>
    </footer>
  );
}
