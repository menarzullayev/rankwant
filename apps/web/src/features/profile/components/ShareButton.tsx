"use client";

import { CopyButton } from "@/components/kit/CopyControl";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Telefonda tizimning ulashish oynasi, kompyuterda havolani nusxalash.
 *  Havola ulashilganda OG karta (`opengraph-image.tsx`) chiqadi. */
export function ShareButton({ username, name }: { username: string; name: string }) {
  const locale = useLocale();
  return (
    <CopyButton
      shape="label"
      icon="action.share"
      text={async () => `${window.location.origin}/users/${username}`}
      shareTitle={`${name} · RankWant`}
      label={t(locale, "profile.share")}
      copiedLabel={t(locale, "profile.shareCopied")}
    />
  );
}
