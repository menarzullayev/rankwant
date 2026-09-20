"use client";

import type { Route } from "next";
import Link from "next/link";
import { useState } from "react";

import { OverlayDialog } from "@/components/overlay/OverlayHost";
import { UpdateKindBadge } from "@/components/UpdateKindBadge";
import { useSession } from "@/context/SessionContext";
import { useUpdates } from "@/context/UpdatesContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { date, t } from "@/i18n/messages";
import { Icon } from "@/components/ui/Icon";
import { fetchUpdateUnread, type SystemUpdate } from "@/lib/api";

/** O'qilmagan o'zgarishlar — header belgisi va overlay modal (qaror 6).
 *
 *  Mehmon hech narsa ko'rmaydi: o'qilmagan holat `UpdateRead` yozuviga
 *  tayanadi, mehmonda esa u yo'q (qaror 7, 8).
 *
 *  Bildirishnomalar qo'ng'irog'idan ALOHIDA belgi: ikkita bir xil
 *  qo'ng'iroq yonma-yon turganda qaysi biri nima ekanini ajratib
 *  bo'lmasdi. Bu yerda ikonka boshqa (ro'yxat + uchqun), ya'ni "shaxsiy
 *  xabar" va "platforma o'zgarishi" ko'rinishda ajralib turadi.
 */
export default function UpdatesBell() {
  const { user, ready } = useSession();
  const { count, actionable, markRead } = useUpdates();
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  /** `null` — ro'yxat hali o'qilmagan (panel ochilishida o'qiladi). */
  const [items, setItems] = useState<SystemUpdate[] | null>(null);

  /** Panel HAR ochilganda ro'yxat qaytadan o'qiladi.
   *
   *  Effekt emas, hodisa ishlovchisi: effekt ichida `setState` chaqirish
   *  taqiqlangan (`react-hooks/set-state-in-effect`) va bu yerda unga
   *  ehtiyoj ham yo'q — sabab hodisaning o'zi. Belgi mount paytida
   *  olingan bo'lishi mumkin, ya'ni oradagi o'zgarish eski ro'yxatda
   *  ko'rinmasdi.
   */
  async function openPanel() {
    setOpen(true);
    setItems(null);
    const body = await fetchUpdateUnread("?page_size=20").catch(() => null);
    setItems(body?.results ?? []);
  }

  /** O'qilgan deb belgilangan yozuv ro'yxatdan DARHOL olib tashlanadi.
   *  Server javobini kutib qayta so'rash ortiqcha aylanma yo'l bo'lardi —
   *  son baribir `markRead` ichida yangilanadi. */
  function dismiss(ids?: number[]) {
    setItems((prev) =>
      ids === undefined ? [] : (prev?.filter((r) => !ids.includes(r.id)) ?? prev),
    );
    void markRead(ids);
    setOpen(false);
  }

  // Hooklar yuqorida — bu qaytish ulardan KEYIN turadi.
  if (!ready || !user) return null;

  const iconBtn =
    "flex size-10 items-center justify-center rw-radius-sm border rw-line rw-dim-2 transition rw-hover-bg";

  return (
    <>
      <button
        type="button"
        onClick={() => void openPanel()}
        aria-label={t(locale, "nav.updates")}
        title={count > 0 ? `${count}` : t(locale, "update.allRead")}
        className={`relative ${iconBtn}`}
      >
        <Icon name="notification.changelog" className="size-5" />
        {count > 0 && (
          <span
            className={`absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[10px] font-semibold ${
              actionable > 0 ? "rw-kind-breaking" : "rw-accent-bg"
            }`}
          >
            {count > 99 ? "99+" : count}
          </span>
        )}
      </button>

      <OverlayDialog
        open={open}
        onClose={() => setOpen(false)}
        title={t(locale, "nav.updates")}
        footer={
          <>
            <Link
              href={"/updates" as Route}
              onClick={() => setOpen(false)}
              className="text-theme-sm font-medium rw-accent-ink hover:underline"
            >
              {t(locale, "update.back")}
            </Link>
            {items !== null && items.length > 0 ? (
              <button
                type="button"
                onClick={() => dismiss()}
                className="rw-ov-btn rw-ov-go"
              >
                {t(locale, "update.markAllRead")}
              </button>
            ) : null}
          </>
        }
      >
        {items !== null &&
          (items.length === 0 ? (
            <p className="py-6 text-center text-theme-sm rw-faint">
              {t(locale, "update.allRead")}
            </p>
          ) : (
            <ul className="divide-y rw-divide">
              {items.map((row) => (
                <li key={row.id}>
                  <Link
                    href={`/updates/${row.id}`}
                    onClick={() => dismiss([row.id])}
                    className="block py-3 transition rw-hover-bg"
                  >
                    <span className="flex flex-wrap items-center gap-2">
                      <UpdateKindBadge kind={row.kind} locale={locale} />
                      <span className="text-theme-xs rw-faint">
                        {date(row.released_at, locale)}
                      </span>
                    </span>
                    <span className="mt-2 block font-medium rw-strong">
                      {row.title}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          ))}
      </OverlayDialog>
    </>
  );
}
