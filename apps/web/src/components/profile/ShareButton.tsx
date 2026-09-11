"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";

/** Telefonda tizimning ulashish oynasi, kompyuterda havolani nusxalash.
 *  Havola ulashilganda OG karta (`opengraph-image.tsx`) chiqadi. */
export function ShareButton({ username, name }: { username: string; name: string }) {
  const locale = useLocale();
  const [copied, setCopied] = useState(false);

  async function share() {
    const url = `${window.location.origin}/users/${username}`;
    if (navigator.share) {
      try {
        await navigator.share({ title: `${name} · RankWant`, url });
      } catch {
        // Odam oynani yopdi — xato emas.
      }
      return;
    }
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
    } catch {
      // Clipboard ruxsati yo'q — manzil baribir brauzer satrida.
    }
  }

  return (
    <Button variant="outline" onClick={share} aria-live="polite">
      {copied ? t(locale, "profile.shareCopied") : t(locale, "profile.share")}
    </Button>
  );
}
