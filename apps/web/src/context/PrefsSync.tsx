"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

import { useSession } from "@/context/SessionContext";
import { DEFAULT_LOCALE, isLocale } from "@/i18n/messages";
import { STYLE_IDS, type StyleId } from "@/layout/styles";
import {
  ApiError,
  patchJson,
  type A11yPrefs,
  type AppearancePrefs,
  type ThemeTemplate,
} from "@/lib/api";
import { track } from "@/lib/analytics";
import {
  PREFS_EVENT,
  TEMPLATES_KEY,
  rememberAppearance,
  rememberPrefs,
  writeLocal,
  type PrefsChange,
} from "@/lib/prefs";
import { applyA11y, applyAll } from "@/lib/theme/apply";
import {
  SIGNED_IN_TEMPLATE_LIMIT,
  accountTemplates,
  mergeSavedTemplates,
} from "@/lib/theme/saved-templates";

const isStyle = (value: unknown): value is StyleId =>
  typeof value === "string" && STYLE_IDS.includes(value as StyleId);

const isMode = (value: unknown): value is "light" | "dark" | "system" =>
  value === "light" || value === "dark" || value === "system";

/** `system` ni OS sozlamasi bo'yicha yechadi. */
const resolveMode = (mode: "light" | "dark" | "system"): boolean =>
  mode === "system"
    ? window.matchMedia("(prefers-color-scheme: dark)").matches
    : mode === "dark";

/** Sinxronizatsiya xatosi — jim qolmaydi.
 *
 * ⚠️ 2026-09-18 gacha bu `catch(() => {})` edi. Server `appearance` da
 * beshta kalitni bilardi, klient esa o'n sakkiztasini yuborardi: har
 * saqlash `400` bilan tugardi, interfeys esa hech narsa demasdi va odam
 * boshqa qurilmada eski ko'rinishni ko'rardi. Sxema tuzatildi
 * (`apps/api/core/prefs.py`), lekin jim yutish o'shanday holatni yana
 * yashirib qo'yardi — shuning uchun xato endi konsolga ham, analitikaga
 * ham chiqadi.
 */
function reportSyncFailure(error: unknown): void {
  const status = error instanceof ApiError ? String(error.status) : "network";
  console.warn(`[prefs] hisobga yozilmadi (${status})`, error);
  track("prefs.sync_failed", { status });
}

function readLocal(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

/** This device's saved templates; anything unreadable counts as none. */
function readTemplates(): ThemeTemplate[] {
  try {
    const parsed: unknown = JSON.parse(readLocal(TEMPLATES_KEY) ?? "[]");
    return Array.isArray(parsed) ? (parsed as ThemeTemplate[]) : [];
  } catch {
    return [];
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

    // Saved templates (APP-13): the account's list joins this device's.
    // `CustomizerProvider` renders the same merge from the same two lists.
    // It rides in this one PATCH: a second request would carry the stale
    // `prefs` snapshot and undo the style migration above.
    const fromAccount = accountTemplates(prefs);
    const templates = mergeSavedTemplates(fromAccount, readTemplates(), SIGNED_IN_TEMPLATE_LIMIT);
    writeLocal(TEMPLATES_KEY, JSON.stringify(templates));
    if (JSON.stringify(templates) !== JSON.stringify(fromAccount)) {
      patch.ui_prefs = {
        ...((patch.ui_prefs as Record<string, unknown> | undefined) ?? { ...prefs, version: 2 }),
        templates,
      };
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
    if (Object.keys(patch).length) void patchJson("/me/", patch).catch(reportSyncFailure);
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
        void patchJson("/me/", body).catch(reportSyncFailure);
    };
    window.addEventListener(PREFS_EVENT, onChange);
    return () => window.removeEventListener(PREFS_EVENT, onChange);
  }, [user]);

  return null;
}
