"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

import { useSession } from "@/context/SessionContext";
import { DEFAULT_LOCALE, isLocale } from "@/i18n/messages";
import { STYLE_IDS, type StyleId } from "@/layout/styles";
import { patchJson, type A11yPrefs, type AppearancePrefs } from "@/lib/api";
import {
  PREFS_EVENT,
  rememberAppearance,
  rememberPrefs,
  writeLocal,
  type PrefsChange,
} from "@/lib/prefs";
import { applyA11y, applyAll } from "@/lib/theme/apply";

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

    // Sozlagich guruhlari: hisob ustun (D4). Qurilmadagi nusxa faqat
    // chaqnashni oldini oluvchi kesh — kirgandan keyin hisob qiymati
    // qo'llanadi va qurilmaga ham yoziladi.
    const accountAppearance = (prefs.appearance ?? null) as AppearancePrefs | null;
    const accountA11y = (prefs.a11y ?? null) as A11yPrefs | null;
    if (accountAppearance) {
      applyAll(accountAppearance, accountA11y ?? {});
      rememberAppearance(accountAppearance, accountA11y ?? {});
    } else if (accountA11y) {
      // Faqat qulaylik sozlamasi bo'lsa uslubga TEGILMAYDI: `applyAll`
      // `appearance.style` bo'sh bo'lsa standartga qaytarib qo'yardi.
      applyA11y(accountA11y);
      rememberAppearance({}, accountA11y);
    }

    // ── Til: QURILMA ustun, hisob — urug' ───────────────────────────
    //
    // ⚠️ Bu D4 dan ATAYLAB chetlanish (u yerda mavzu uchun hisob ustun).
    // Sabab: til — qurilmaning xususiyati. Bitta odam telefonda
    // o'zbekcha, ish kompyuterida inglizcha o'qishi mumkin; hisob
    // ularning ikkalasini ham bosib ketmasligi kerak. Shuning uchun:
    //
    //   cookie bor    → u ustun (odam shu qurilmada tanlagan).
    //   cookie yo'q   → hisobdagi til URUG' bo'lib qurilmaga yoziladi.
    //
    // «Avtomatik» tanlansa cookie o'chiriladi va bu tarmoq ishga
    // tushmasligi SHART — aks holda tanlov darhol bekor bo'lardi.
    // Buni `rw_locale=auto` markeri ajratib turadi: u «tanlov yo'q
    // emas, ataylab avtomatik» ma'nosini bildiradi va `server.ts` uni
    // sarlavhadan aniqlashga o'tkazadi.
    const cookie = document.cookie.match(/(?:^|;\s*)rw_locale=([^;]+)/)?.[1];
    const explicitAuto = cookie === "auto";
    if (explicitAuto) {
      // Odam avtomatikni tanlagan — hisob urug'i qo'llanmaydi.
    } else if (isLocale(cookie)) {
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
      // `locale` da `null` — «Avtomatik» tanlandi. Hisobga YOZILMAYDI:
      // `User.locale` da `blank=False` va `choices` bor, ya'ni bo'sh satr
      // 400 beradi (o'lchandi). «Avtomatik» faqat cookie'ni o'chiradi —
      // hisobdagi til urug' bo'lib qoladi va qurilma tanlovi bo'lmaganda
      // ishlatiladi. Bu D4 dan ataylab chetlanish: qurilma ustun
      // (`docs/i18n-precedence.md`).
      if (typeof change.locale === "string") body.locale = change.locale;
      if (change.style || change.appearance || change.a11y || change.templates) {
        const current = user.ui_prefs ?? {};
        const appearance = (current.appearance ?? {}) as Record<string, unknown>;
        body.ui_prefs = {
          ...current,
          version: 2,
          appearance: {
            ...appearance,
            ...(change.appearance ?? {}),
            ...(change.style ? { style: change.style } : {}),
          },
          ...(change.a11y
            ? { a11y: { ...(current.a11y ?? {}), ...change.a11y } }
            : {}),
          // Shablonlar BUTUN ro'yxat bo'lib keladi: ularni birlashtirish
          // o'chirishni imkonsiz qilardi.
          ...(change.templates ? { templates: change.templates } : {}),
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
