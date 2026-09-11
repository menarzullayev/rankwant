"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { patchJson } from "@/lib/api";

/** Server bilan bir xil chegara — `profiles.achievements.PINNED_MAX`. */
const PINNED_MAX = 3;

/** Yutuqni profil kartasiga qo'yish yoki olish — faqat egasiga ko'rinadi. */
export function PinButton({ code, pinned }: { code: string; pinned: string[] }) {
  const locale = useLocale();
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const on = pinned.includes(code);
  const full = !on && pinned.length >= PINNED_MAX;

  async function toggle() {
    setBusy(true);
    try {
      await patchJson("/me/", {
        pinned_achievements: on ? pinned.filter((item) => item !== code) : [...pinned, code],
      });
      router.refresh();
    } catch {
      // Holat o'zgarmadi — tugma avvalgi ko'rinishida qoladi.
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      disabled={busy || full}
      aria-pressed={on}
      title={full ? t(locale, "profile.pinLimit") : undefined}
      className="rw-radius-sm border rw-line px-2.5 py-1 text-theme-xs font-medium rw-strong transition rw-hover-bg rw-focus-ring disabled:opacity-50"
    >
      {t(locale, on ? "profile.unpin" : "profile.pin")}
    </button>
  );
}
