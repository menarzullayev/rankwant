"use client";

import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { patchJson, type NotifyPrefs } from "@/lib/api";
import { Hint, Status, useAction } from "./kit";

/** `notifications.models.Notification.Kind` — musobaqa natijasi birinchi:
 *  eng ko'p kutiladigan xabar. */
const KINDS = [
  "contest_result",
  "rating_changed",
  "problem_rerated",
  "duel",
  "quest_awarded",
  "streak_milestone",
  "system",
] as const;

const CHANNELS = ["site", "telegram"] as const;
type Channel = (typeof CHANNELS)[number];

export function NotificationsSection() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const action = useAction();
  const [edited, setEdited] = useState<NotifyPrefs | null>(null);
  if (!user) return null;

  const prefs = edited ?? user.notify_prefs ?? {};
  const telegram = user.social.includes("telegram");
  // Standart: saytda — ha, Telegram'da — yo'q (`notifications.services`).
  const value = (kind: string, channel: Channel) =>
    prefs[kind]?.[channel] ?? channel === "site";

  function set(kind: string, channel: Channel, on: boolean) {
    setEdited({
      ...prefs,
      [kind]: { site: value(kind, "site"), telegram: value(kind, "telegram"), [channel]: on },
    });
  }

  async function save() {
    const ok = await action.run(async () => {
      await patchJson("/me/", { notify_prefs: prefs });
      await reload();
    });
    if (ok) setEdited(null);
  }

  const channelLabel = (channel: Channel) =>
    t(locale, channel === "site" ? "settings.channelSite" : "settings.channelTelegram");

  return (
    <Card title={t(locale, "settings.notify")}>
      <Hint>{t(locale, "settings.notifyHint")}</Hint>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-theme-sm">
          <thead>
            <tr className="border-b rw-line">
              <th scope="col" className="py-2 pr-4 text-left font-medium rw-dim">
                {t(locale, "settings.kindColumn")}
              </th>
              {CHANNELS.map((channel) => (
                <th key={channel} scope="col" className="px-3 py-2 text-center font-medium rw-dim">
                  {channelLabel(channel)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y rw-divide">
            {KINDS.map((kind) => (
              <tr key={kind}>
                <th scope="row" className="py-3 pr-4 text-left font-normal rw-strong">
                  {t(locale, `settings.kind.${kind}`)}
                </th>
                {CHANNELS.map((channel) => (
                  <td key={channel} className="px-3 py-3 text-center">
                    <input
                      type="checkbox"
                      className="rw-accent-control size-4"
                      checked={value(kind, channel)}
                      disabled={channel === "telegram" && !telegram}
                      onChange={(event) => set(kind, channel, event.target.checked)}
                      aria-label={`${t(locale, `settings.kind.${kind}`)} — ${channelLabel(channel)}`}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-theme-xs rw-dim">
        {telegram ? (
          t(locale, "settings.telegramAccess")
        ) : (
          <>
            {t(locale, "settings.telegramMissing")}{" "}
            <Link href="/settings/ijtimoiy" className="rw-accent-ink hover:underline">
              {t(locale, "settings.nav.social")}
            </Link>
          </>
        )}
      </p>
      <p className="mt-1 text-theme-xs rw-faint">{t(locale, "settings.channelEmailSoon")}</p>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <Button busy={action.busy} disabled={edited === null} onClick={save}>
          {t(locale, "settings.save")}
        </Button>
        <Status error={action.error} done={action.done} />
      </div>
    </Card>
  );
}
