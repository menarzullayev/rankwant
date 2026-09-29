"use client";

import type { Route } from "next";
import Link from "next/link";
import { useSyncExternalStore } from "react";

import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

const KEY = "rw_geo_nudge_dismissed";

/** Yopilganini `localStorage` da saqlaydi.
 *
 * `useSyncExternalStore` — effekt ichida `setState` qilmaslik uchun:
 * `localStorage` serverda yo'q, ya'ni dastlabki holatni render paytida
 * o'qib bo'lmaydi. Bu hook aynan shu holat uchun (tashqi manba) va
 * server snapshot'ini alohida beradi. */
const listeners = new Set<() => void>();

function subscribe(onChange: () => void) {
  listeners.add(onChange);
  return () => {
    listeners.delete(onChange);
  };
}

function isDismissed() {
  try {
    return localStorage.getItem(KEY) === "1";
  } catch {
    // Maxfiy rejimda `localStorage` yopiq bo'lishi mumkin — banner
    // ko'rinmasligi yaxshiroq (aks holda har sahifada qaytardi).
    return true;
  }
}

function dismiss() {
  try {
    localStorage.setItem(KEY, "1");
  } catch {
    // Saqlanmasa ham joriy sessiyada yopiladi.
  }
  listeners.forEach((notify) => notify());
}

/** Kontekstli nudge (qaror 16): mavjud foydalanuvchi davlat va maktabni
 *  to'ldirsin.
 *
 * Nega kerak: mamlakat maydoni endigina ro'yxat formasiga qo'shildi,
 * mavjud 10 000+ hisobda esa u bo'sh — ya'ni global statistika faqat
 * yangi hisoblardan yig'ila boshlaydi. Bu banner o'sha bo'shliqni
 * yumshoq yo'l bilan yopadi.
 *
 * Nega YUMSHOQ: majburiy to'ldirish faol foydalanuvchini ham to'xtatadi
 * (qaror 16 da rad etilgan variant). Shu sababli banner yopiladi va
 * qaytmaydi — bezor qilmaydi, lekin xohlagan odam yo'lni topadi.
 */
export function GeoNudge() {
  const locale = useLocale();
  const { user } = useSession();
  const dismissed = useSyncExternalStore(subscribe, isDismissed, () => true);

  if (dismissed) return null;
  // Faqat kirgan va mamlakatni to'ldirmagan odamga.
  if (!user || user.country) return null;

  return (
    <div className="rw-accent-soft px-4 py-3 text-theme-sm rw-accent-ink">
      <div className="rw-content mx-auto flex flex-wrap items-center justify-center gap-3">
        <span>
          <strong>{t(locale, "geo.nudgeTitle")}</strong>{" "}
          {t(locale, "geo.nudgeBody")}
        </span>
        <Link
          href={"/onboarding" as Route}
          className="rw-radius-sm rw-accent-bg px-3 py-1.5 font-medium rw-focus-ring"
        >
          {t(locale, "geo.nudgeCta")}
        </Link>
        <button
          type="button"
          onClick={dismiss}
          className="underline rw-focus-ring"
        >
          {t(locale, "auth.dismiss")}
        </button>
      </div>
    </div>
  );
}
