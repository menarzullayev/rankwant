"use client";

import Link from "next/link";
import { useState } from "react";

import { FormBox } from "@/components/form/FormKit";
import { InfoMark } from "@/components/kit/FormExtras";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { patchJson, type NotifyPrefs } from "@/lib/api";
import { useSaveSlot } from "./SaveBar";
import { Hint, Status, useAction } from "./section-kit";

/** `notifications.models.Notification.Kind` — musobaqa natijasi birinchi:
 *  eng ko'p kutiladigan xabar. */
const KINDS = [
  "contest_result",
  "rating_changed",
  "problem_rerated",
  "duel",
  // Hack natijasi IKKALA tomonga ham boradi (ADR-0020): hackerga
  // natijasi, himoyachiga yechimi nega bekor qilingani. Backend uni
  // allaqachon yuborardi, lekin bu ro'yxatda bo'lmagani uchun uni
  // o'chirib qo'yishning iloji yo'q edi.
  "hack",
  "quest_awarded",
  "streak_milestone",
  "system",
] as const;

const CHANNELS = ["site", "telegram", "email"] as const;
type Channel = (typeof CHANNELS)[number];

const CHANNEL_LABEL = {
  site: "settings.channelSite",
  telegram: "settings.channelTelegram",
  email: "settings.channelEmail",
} as const;

export function NotificationsSection() {
  const locale = useLocale();
  const { user, reload } = useSession();
  const action = useAction();
  const [edited, setEdited] = useState<NotifyPrefs | null>(null);
  const prefs = edited ?? user?.notify_prefs ?? {};
  const telegram = user?.social.includes("telegram") ?? false;
  // Email goes to a confirmed address only (`notifications.email.reachable`).
  const email = Boolean(user?.email && user.email_verified);
  // Standart: saytda — ha; Telegram va email — yo'q, foydalanuvchi o'zi
  // yoqadi (`notifications.services.DEFAULT_CHANNELS`, 2026-11-10).
  const value = (kind: string, channel: Channel) =>
    prefs[kind]?.[channel] ?? channel === "site";

  function set(kind: string, channel: Channel, on: boolean) {
    setEdited({
      ...prefs,
      [kind]: {
        site: value(kind, "site"),
        telegram: value(kind, "telegram"),
        email: value(kind, "email"),
        [channel]: on,
      },
    });
  }

  const save = async () => {
    const ok = await action.run(async () => {
      await patchJson("/me/", { notify_prefs: prefs });
      await reload();
    });
    if (ok) setEdited(null);
    return ok;
  };
  useSaveSlot(edited !== null, save, () => setEdited(null));

  if (!user) return null;

  const channelLabel = (channel: Channel) => t(locale, CHANNEL_LABEL[channel]);
  const available = (channel: Channel) =>
    channel === "site" || (channel === "telegram" ? telegram : email);

  return (
    <Card
      title={
        <h2 className="flex items-center gap-2 text-theme-xl font-semibold rw-strong">
          {t(locale, "settings.notify")}
          <InfoMark text={t(locale, "settings.notifyHint")} />
        </h2>
      }
    >
      <Hint>{t(locale, "settings.notifyHint")}</Hint>
      <div className="mt-4 rw-scroll-x">
        <table className="w-full text-theme-sm">
          <thead>
            <tr className="border-b rw-divider">
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
                    <FormBox
                      shape="switch"
                      checked={value(kind, channel)}
                      disabled={!available(channel)}
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
            <Link href="/settings/xavfsizlik" className="rw-accent-ink hover:underline">
              {t(locale, "settings.nav.security")}
            </Link>
          </>
        )}
      </p>
      <p className="mt-2 text-theme-xs rw-dim">
        {email ? (
          t(locale, "settings.notifyEmailHint")
        ) : (
          <>
            {t(locale, "settings.emailNeedsVerify")}{" "}
            <Link href="/verify-email" className="rw-accent-ink hover:underline">
              {t(locale, "settings.emailVerifyLink")}
            </Link>
          </>
        )}
      </p>
      <div className="mt-4">
        <Status error={action.error} done={action.done} />
      </div>
    </Card>
  );
}
