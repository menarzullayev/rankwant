import type { Metadata } from "next";

import { NotificationCenter } from "@/components/notifications/NotificationCenter";
import { t } from "@/i18n/messages";
import { getLocale } from "@/i18n/server";

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "notif.title"), robots: { index: false } };
}

/** The list is read in the browser: it is private, it changes while the
 *  page is open, and every time on it is drawn in the reader's own time
 *  zone — a server render would disagree with the first client one. */
export default function NotificationsPage() {
  return <NotificationCenter />;
}
