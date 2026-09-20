"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useCustomizer } from "@/context/CustomizerContext";
import { useSession } from "@/context/SessionContext";
import { useStyle } from "@/context/StyleContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { LOCALES, LOCALE_NAMES, t } from "@/i18n/messages";
import { patchJson, type ThemeEffect, type UiPrefs } from "@/lib/api";
import { announcePrefs, playSuccess, rememberPrefs } from "@/lib/prefs";
import { FormRadios } from "@/components/form/FormKit";
import { Check, Hint, Select, Status, useAction } from "./kit";

const EFFECTS: ThemeEffect[] = ["none", "fade", "circle"];

/** Til, ovoz va effekt — ko'rinish esa bitta joyda: customizer. */
export function AppearanceSection() {
  const locale = useLocale();
  const router = useRouter();
  const { user, reload } = useSession();
  const { style } = useStyle();
  const { setOpen } = useCustomizer();
  const action = useAction();
  const [pending, startTransition] = useTransition();
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
              className="h-9 px-3"
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
