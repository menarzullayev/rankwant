import type { Metadata } from "next";
import { api, ApiError, type Notification } from "@/lib/api";
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
      <p style={{ color: "var(--muted)" }}>
        Bildirishnomalarni ko&apos;rish uchun tizimga kiring.
      </p>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">{t(locale, "notif.title")}</h1>
      <ul className="space-y-2">
        {items.map((n) => (
          <li
            key={n.id}
            className="rounded-lg border p-4"
            style={{
              borderColor: n.is_read ? "var(--border)" : "var(--accent)",
              background: "var(--surface)",
            }}
          >
            <p className="font-medium">{n.title}</p>
            {n.body && (
              <p className="mt-1 text-sm" style={{ color: "var(--muted)" }}>
                {n.body}
              </p>
            )}
            <p className="mt-2 text-xs" style={{ color: "var(--muted)" }}>
              {new Date(n.created_at).toLocaleString(locale)}
            </p>
          </li>
        ))}
      </ul>
      {items.length === 0 && <p style={{ color: "var(--muted)" }}>{t(locale, "empty")}</p>}
    </div>
  );
}
