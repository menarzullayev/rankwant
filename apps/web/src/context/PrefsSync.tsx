"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

import { useSession } from "@/context/SessionContext";
import { DEFAULT_LOCALE, isLocale } from "@/i18n/messages";
import { STYLE_IDS, type StyleId } from "@/layout/styles";
import { patchJson } from "@/lib/api";
import {
  PREFS_EVENT,
  rememberPrefs,
  writeLocal,
  type PrefsChange,
} from "@/lib/prefs";

const isStyle = (value: unknown): value is StyleId =>
  typeof value === "string" && STYLE_IDS.includes(value as StyleId);

function readLocal(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

/** Ko'rinish sozlamalarini hisob bilan moslaydi.
 *
 * Kirganda: hisobda qiymat bo'lsa — u qo'llanadi va qurilmaga ham
 * yoziladi (keyingi yuklanishda chaqnash bo'lmasin); bo'lmasa —
 * qurilmadagi tanlov hisobga ko'chiriladi.
 *
 * Til bundan mustasno: hisob tili ko'pchilikda ro'yxatdan o'tgandagi
 * standart `uz`. Uni har kirishda qo'llash rus tilini tanlagan odamni
 * har safar o'zbekchaga qaytarardi. Shuning uchun qurilmada ONGLI tanlov
 * (cookie) bo'lsa, u ustun va hisobga yoziladi — xatlar ham shu tilda.
 */
export function PrefsSync() {
  const { user } = useSession();
  const router = useRouter();
  const synced = useRef<number | null>(null);

  useEffect(() => {
    if (!user || synced.current === user.id) return;
    synced.current = user.id;
    const root = document.documentElement;
    const prefs = user.ui_prefs ?? {};
    const patch: Record<string, unknown> = {};

    if (user.theme === "light" || user.theme === "dark") {
      root.classList.toggle("dark", user.theme === "dark");
      writeLocal("theme", user.theme);
    } else {
      const local = readLocal("theme");
      if (local === "light" || local === "dark") patch.theme = local;
    }

    if (isStyle(prefs.style)) {
      root.dataset.style = prefs.style;
      writeLocal("style", prefs.style);
    } else {
      const local = readLocal("style");
      if (isStyle(local)) patch.ui_prefs = { ...prefs, style: local };
    }

    const cookie = document.cookie.match(/(?:^|;\s*)rw_locale=([^;]+)/)?.[1];
    if (isLocale(cookie)) {
      if (cookie !== user.locale) patch.locale = cookie;
    } else if (isLocale(user.locale) && user.locale !== DEFAULT_LOCALE) {
      document.cookie = `rw_locale=${user.locale}; path=/; max-age=31536000; samesite=lax`;
      router.refresh();
    }

    rememberPrefs({ sound: prefs.sound, effect: prefs.effect });
    if (Object.keys(patch).length) void patchJson("/me/", patch).catch(() => {});
  }, [user, router]);

  useEffect(() => {
    if (!user) return;
    const onChange = (event: Event) => {
      const change = (event as CustomEvent<PrefsChange>).detail;
      const body: Record<string, unknown> = {};
      if (change.theme) body.theme = change.theme;
      if (change.locale) body.locale = change.locale;
      if (change.style)
        body.ui_prefs = { ...(user.ui_prefs ?? {}), style: change.style };
      if (Object.keys(body).length)
        void patchJson("/me/", body).catch(() => {});
    };
    window.addEventListener(PREFS_EVENT, onChange);
    return () => window.removeEventListener(PREFS_EVENT, onChange);
  }, [user]);

  return null;
}
