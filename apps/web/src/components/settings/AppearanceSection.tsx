"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { useStyle } from "@/context/StyleContext";
import { useTheme } from "@/context/ThemeContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { LOCALES, LOCALE_NAMES, t } from "@/i18n/messages";
import { STYLES, isDual } from "@/layout/styles";
import { patchJson, type ThemeEffect, type UiPrefs } from "@/lib/api";
import { announcePrefs, playSuccess, rememberPrefs } from "@/lib/prefs";
import { Check, Hint, Select, Status, useAction } from "./kit";

const EFFECTS: ThemeEffect[] = ["none", "fade", "circle"];

/** Til, mavzu va uslub darhol qo'llanadi va hisobga yoziladi
 *  (`PrefsSync`) — boshqa qurilmadan kirganda ham shunday ko'rinadi. */
export function AppearanceSection() {
  const locale = useLocale();
  const router = useRouter();
  const { user, reload } = useSession();
  const { mode, setMode } = useTheme();
  const { style, setStyle } = useStyle();
  const action = useAction();
  const [pending, startTransition] = useTransition();
  // Javob kelguncha ham belgi darhol o'zgarsin.
  const [local, setLocal] = useState<UiPrefs>({});
  if (!user) return null;

  const prefs = { ...user.ui_prefs, ...local };
  const sound = prefs.sound ?? false;
  const effect = prefs.effect ?? "fade";

  async function savePrefs(next: { sound?: boolean; effect?: ThemeEffect }) {
    setLocal((current) => ({ ...current, ...next }));
    rememberPrefs(next);
    await action.run(async () => {
      await patchJson("/me/", {
        ui_prefs: {
          ...prefs,
          version: 2,
          // Uslub sarlavhadan ham o'zgarishi mumkin — joriysi yoziladi, aks
          // holda eski `ui_prefs` bilan birga eski uslub qaytib yozilardi.
          appearance: { ...(prefs.appearance ?? {}), style },
          ...next,
        },
      });
      await reload();
    });
  }

  function chooseLocale(next: string) {
    document.cookie = `rw_locale=${next}; path=/; max-age=31536000; samesite=lax`;
    announcePrefs({ locale: next });
    startTransition(() => router.refresh());
  }

  const option = (active: boolean) =>
    `flex h-11 items-center justify-center rw-radius-sm border px-4 text-theme-sm font-medium transition rw-focus-ring ${
      active ? "rw-accent-line rw-accent-soft" : "rw-line rw-dim-2 rw-hover-bg"
    }`;

  return (
    <>
      <Card title={t(locale, "settings.nav.appearance")}>
        <Hint>{t(locale, "settings.appearanceHint")}</Hint>
        <div className="mt-4 grid gap-5 sm:grid-cols-2">
          <Select
            label={t(locale, "settings.language")}
            value={locale}
            disabled={pending}
            onChange={(event) => chooseLocale(event.target.value)}
          >
            {LOCALES.map((code) => (
              <option key={code} value={code}>
                {LOCALE_NAMES[code]}
              </option>
            ))}
          </Select>
          <fieldset>
            <legend className="mb-1.5 text-theme-sm font-medium rw-strong">
              {t(locale, "settings.theme")}
            </legend>
            {isDual(style) ? (
              <div className="flex flex-wrap gap-2">
                {(["light", "dark", "system"] as const).map((value) => (
                  <button
                    key={value}
                    type="button"
                    aria-pressed={mode === value}
                    onClick={() => setMode(value)}
                    className={option(mode === value)}
                  >
                    {t(locale, `theme.${value}`)}
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-theme-sm rw-dim">{t(locale, "settings.themeFixed")}</p>
            )}
          </fieldset>
        </div>
      </Card>

      <Card title={t(locale, "settings.style")}>
        <ul className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
          {STYLES.map((s) => (
            <li key={s.id}>
              <button
                type="button"
                aria-pressed={s.id === style}
                onClick={() => setStyle(s.id)}
                className={`flex w-full items-center gap-3 rw-radius border px-3 py-2.5 text-left transition rw-focus-ring ${
                  s.id === style ? "rw-accent-line" : "rw-line rw-hover-bg"
                }`}
              >
                <span
                  data-style={s.id}
                  aria-hidden="true"
                  className="flex size-9 shrink-0 items-center justify-center gap-1 rw-radius-sm border rw-line rw-surface rw-shadow"
                >
                  <span className="size-2 rounded-full rw-accent-bg" />
                  <span className="h-2 w-1 rw-chip" />
                </span>
                <span className="min-w-0">
                  <span className="block truncate text-theme-sm font-medium rw-strong">
                    {t(locale, s.labelKey)}
                  </span>
                  <span className="block truncate text-theme-xs rw-faint">
                    {t(locale, s.hintKey)}
                  </span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      </Card>

      <Card title={t(locale, "settings.effectsTitle")}>
        <div className="space-y-6">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <Check
              label={t(locale, "settings.sound")}
              hint={t(locale, "settings.soundHint")}
              checked={sound}
              onChange={(event) => void savePrefs({ sound: event.target.checked })}
            />
            <Button
              variant="outline"
              className="h-9 px-3"
              onClick={() => playSuccess({ force: true })}
            >
              {t(locale, "settings.soundTry")}
            </Button>
          </div>
          <fieldset>
            <legend className="mb-2 text-theme-sm font-medium rw-strong">
              {t(locale, "settings.effect")}
            </legend>
            <div className="flex flex-wrap gap-2">
              {EFFECTS.map((value) => (
                <label key={value} className={option(effect === value)}>
                  <input
                    type="radio"
                    name="effect"
                    value={value}
                    checked={effect === value}
                    onChange={() => void savePrefs({ effect: value })}
                    className="sr-only"
                  />
                  {t(locale, `settings.effect.${value}`)}
                </label>
              ))}
            </div>
            <p className="mt-2 text-theme-xs rw-faint">{t(locale, "settings.effectHint")}</p>
          </fieldset>
          <Status error={action.error} done={action.done} />
        </div>
      </Card>
    </>
  );
}
