import type { Metadata } from "next";
import { api, ApiError, type Notification } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { getLocale } from "@/i18n/server";
import { dateTime, t } from "@/i18n/messages";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "notif.title") };
}
export const dynamic = "force-dynamic";

export default async function NotificationsPage() {
  const locale = await getLocale();

  let items: Notification[] = [];
  let signedIn = true;
  try {
    items = (await api.notifications()).results;
  } catch (error) {
    if (
      error instanceof ApiError &&
      (error.status === 401 || error.status === 403)
    ) {
      signedIn = false;
    } else {
      throw error;
    }
  }

  if (!signedIn) {
    return (
      <Card>
        <p className="text-theme-sm rw-dim">
          Bildirishnomalarni ko&apos;rish uchun tizimga kiring.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
        {t(locale, "notif.title")}
      </h1>

      <Card bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {items.map((n) => (
            <li key={n.id} className="flex gap-3 px-5 py-4">
              {/* O'qilmagan bildirishnoma — chap chetida brend nuqtasi */}
              <span
                className={`mt-1.5 size-2 shrink-0 rounded-full ${
                  n.is_read ? "bg-transparent" : "rw-accent-bg"
                }`}
              />
              <div className="min-w-0 flex-1">
                <p className="font-medium rw-strong">{n.title}</p>
                {n.body && (
                  <p className="mt-1 text-theme-sm rw-dim">{n.body}</p>
                )}
                <p className="mt-1 text-theme-xs rw-faint">
                  {dateTime(n.created_at, locale)}
                </p>
              </div>
            </li>
          ))}
          {items.length === 0 && (
            <li className="px-5 py-10 text-center text-theme-sm rw-faint">
              {t(locale, "empty")}
            </li>
          )}
        </ul>
      </Card>
    </div>
  );
}
