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

const isMode = (value: unknown): value is "light" | "dark" | "system" =>
  value === "light" || value === "dark" || value === "system";

/** `system` ni OS sozlamasi bo'yicha yechadi. */
const resolveMode = (mode: "light" | "dark" | "system"): boolean =>
  mode === "system"
    ? window.matchMedia("(prefers-color-scheme: dark)").matches
    : mode === "dark";

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

    // Mavzu: hisob ustun (D4), qurilma nusxasi faqat kesh. `system` ham
    // haqiqiy qiymat — u ham hisobdan qo'llanadi. Ilgari faqat
    // `light`/`dark` hisobga olinardi, ya'ni hisobda `system` turib
    // qurilmada `dark` bo'lsa qurilma ustun bo'lib qolardi.
    if (isMode(user.theme)) {
      root.classList.toggle("dark", resolveMode(user.theme));
      writeLocal("theme", user.theme);
    } else {
      const local = readLocal("theme");
      if (isMode(local)) patch.theme = local;
    }

    // Sxema v2: uslub `appearance` guruhida (D33). Yassi `prefs.style`
    // endi o'qilmaydi — eski qurilma nusxasi uchun `migrate` klientda
    // emas, `core/prefs.py` da bajariladi, ya'ni bu yerda faqat v2.
    const appearance = (prefs.appearance ?? {}) as Record<string, unknown>;
    if (isStyle(appearance.style)) {
      root.dataset.style = appearance.style;
      writeLocal("style", appearance.style);
    } else {
      const local = readLocal("style");
      if (isStyle(local)) {
        patch.ui_prefs = {
          ...prefs,
          version: 2,
          appearance: { ...appearance, style: local },
        };
      }
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
      if (change.style) {
        const appearance = ((user.ui_prefs ?? {}).appearance ?? {}) as Record<
          string,
          unknown
        >;
        body.ui_prefs = {
          ...(user.ui_prefs ?? {}),
          version: 2,
          appearance: { ...appearance, style: change.style },
        };
      }
      if (Object.keys(body).length)
        void patchJson("/me/", body).catch(() => {});
    };
    window.addEventListener(PREFS_EVENT, onChange);
    return () => window.removeEventListener(PREFS_EVENT, onChange);
  }, [user]);

  return null;
}
