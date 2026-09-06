import type { Metadata } from "next";
import { api, ApiError, type Notification } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";

export const metadata: Metadata = { title: "Bildirishnomalar" };
export const dynamic = "force-dynamic";

export default async function NotificationsPage() {
  const locale = DEFAULT_LOCALE;

  let items: Notification[] = [];
  let signedIn = true;
  try {
    items = (await api.notifications()).results;
  } catch (error) {
    if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
      signedIn = false;
    } else {
      throw error;
    }
  }

  if (!signedIn) {
    return (
      <Card>
        <p className="text-theme-sm text-gray-500 dark:text-gray-400">
          Bildirishnomalarni ko&apos;rish uchun tizimga kiring.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">
        {t(locale, "notif.title")}
      </h1>

      <Card bodyClassName="p-0">
        <ul className="divide-y divide-gray-100 dark:divide-[#232936]">
          {items.map((n) => (
            <li key={n.id} className="flex gap-3 px-5 py-4">
              {/* O'qilmagan bildirishnoma — chap chetida brend nuqtasi */}
              <span
                className={`mt-1.5 size-2 shrink-0 rounded-full ${
                  n.is_read ? "bg-transparent" : "bg-brand-500"
                }`}
              />
              <div className="min-w-0 flex-1">
                <p className="font-medium text-gray-800 dark:text-white/90">{n.title}</p>
                {n.body && (
                  <p className="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">
                    {n.body}
                  </p>
                )}
                <p className="mt-1 text-theme-xs text-gray-400">
                  {new Date(n.created_at).toLocaleString(locale)}
                </p>
              </div>
            </li>
          ))}
          {items.length === 0 && (
            <li className="px-5 py-10 text-center text-theme-sm text-gray-400">
              {t(locale, "empty")}
            </li>
          )}
        </ul>
      </Card>
    </div>
  );
}
