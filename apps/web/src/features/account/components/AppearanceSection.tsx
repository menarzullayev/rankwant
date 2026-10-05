"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useCustomizer } from "@/context/CustomizerContext";
import { useSession } from "@/context/SessionContext";
import { useStyle } from "@/context/StyleContext";
import { useTheme } from "@/context/ThemeContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { LOCALES, LOCALE_NAMES, t, type MessageKey } from "@/i18n/messages";
import { STYLES } from "@/layout/styles";
import { patchJson, type ThemeEffect, type UiPrefs } from "@/lib/api";
import { announcePrefs, playSuccess, rememberPrefs } from "@/lib/prefs";
import { accentToHex } from "@/lib/theme/color";
import { clampSize } from "@/lib/theme/typography";
import { FormRadios } from "@/components/form/FormKit";
import { Check, Hint, Select, Status, useAction } from "./section-kit";

const EFFECTS: ThemeEffect[] = ["none", "fade", "circle", "curtain"];

/** Til, ovoz va effekt — ko'rinish esa bitta joyda: customizer.
 *
 *  The page shows what is applied now and opens the panel; it does not
 *  edit appearance itself, so there is still one writer (2026-10-05). */
export function AppearanceSection() {
  const locale = useLocale();
  const router = useRouter();
  const { user, reload } = useSession();
  const { style } = useStyle();
  const { setOpen, appearance, template } = useCustomizer();
  const { mode } = useTheme();
  const action = useAction();
  const [pending, startTransition] = useTransition();
  const [local, setLocal] = useState<UiPrefs>({});
  if (!user) return null;

  const prefs = { ...user.ui_prefs, ...local };
  const sound = prefs.sound ?? false;
  const effect = prefs.effect ?? "fade";
  const styleDef = STYLES.find((item) => item.id === style);
  const accentHex = appearance.accent
    ? accentToHex(appearance.accent.hue, appearance.accent.sat)
    : null;
  const summary: { label: string; value: string; swatch?: string }[] = [
    {
      label: t(locale, "settings.currentTemplate"),
      value: template
        ? t(locale, `customizer.template.${template.id}`)
        : t(locale, "customizer.templateModified"),
    },
    { label: t(locale, "customizer.theme"), value: t(locale, `theme.${mode}`) },
    {
      label: t(locale, "customizer.style"),
      value: styleDef ? t(locale, styleDef.labelKey as MessageKey) : style,
    },
    {
      label: t(locale, "customizer.accent"),
      value: accentHex ?? t(locale, "customizer.accentDefault"),
      swatch: accentHex ?? undefined,
    },
    { label: t(locale, "customizer.size"), value: `${clampSize(appearance.size)}%` },
  ];

  async function savePrefs(next: { sound?: boolean; effect?: ThemeEffect }) {
    setLocal((current) => ({ ...current, ...next }));
    rememberPrefs(next);
    await action.run(async () => {
      await patchJson("/me/", {
        ui_prefs: {
          ...prefs,
          version: 2,
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

  return (
    <>
      <Card title={t(locale, "settings.nav.appearance")}>
        <Hint>{t(locale, "settings.appearanceHint")}</Hint>
        <dl
          data-appearance-summary
          className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3 xl:grid-cols-5"
        >
          {summary.map((row) => (
            <div key={row.label} className="min-w-0 rw-radius-sm border rw-line px-3 py-2">
              <dt className="truncate text-theme-xs rw-faint">{row.label}</dt>
              <dd className="mt-0.5 flex items-center gap-1.5 text-theme-sm font-medium rw-strong">
                {row.swatch ? (
                  <span
                    aria-hidden="true"
                    className="size-3 shrink-0 rounded-full border rw-line"
                    style={{ background: row.swatch }}
                  />
                ) : null}
                <span className="truncate">{row.value}</span>
              </dd>
            </div>
          ))}
        </dl>
        <div className="mt-4 grid gap-5 sm:grid-cols-2">
          <Select
            label={t(locale, "settings.language")}
            value={locale}
            disabled={pending}
            onChange={chooseLocale}
            options={LOCALES.map((code) => ({
              value: code,
              label: LOCALE_NAMES[code],
            }))}
          />
          <div className="flex items-end">
            <Button
              type="button"
              variant="outline"
              className="h-11 w-full"
              onClick={() => setOpen(true)}
            >
              {t(locale, "settings.openCustomizer")}
            </Button>
          </div>
        </div>
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
              className="h-11 px-4"
              onClick={() => playSuccess({ force: true })}
            >
              {t(locale, "settings.soundTry")}
            </Button>
          </div>
          <FormRadios
            name="effect"
            label={t(locale, "settings.effect")}
            tone="card"
            value={effect}
            onChange={(next) => void savePrefs({ effect: next as ThemeEffect })}
            options={EFFECTS.map((value) => ({
              value,
              label: t(locale, `settings.effect.${value}`),
            }))}
          />
          <p className="mt-2 text-theme-xs rw-faint">{t(locale, "settings.effectHint")}</p>
          <Status error={action.error} done={action.done} />
        </div>
      </Card>
    </>
  );
}
