"use client";

import { useCustomizer } from "@/context/CustomizerContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import type { A11yPrefs } from "@/lib/api";
import { FormCheck } from "@/components/form/FormKit";

import { chip } from "./chrome";
import { Section } from "./Group";

export function A11yTab() {
  const locale = useLocale();
  const { a11y, setA11y } = useCustomizer();
  const motion = a11y.motion ?? "system";
  const rows: { key: keyof A11yPrefs; label: string }[] = [
    { key: "bigTargets", label: t(locale, "customizer.a11y.bigTargets") },
    { key: "strongFocus", label: t(locale, "customizer.a11y.strongFocus") },
  ];
  return (
    <>
      <Section title={t(locale, "customizer.a11y.vision")}>
        <div className="flex flex-wrap gap-2">
          {(["normal", "protan", "tritan"] as const).map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={(a11y.vision ?? "normal") === value}
              onClick={() => setA11y({ vision: value })}
              className={chip((a11y.vision ?? "normal") === value)}
            >
              {t(locale, `customizer.a11y.vision.${value}`)}
            </button>
          ))}
        </div>
        <p className="mt-2 text-theme-xs rw-faint">
          {t(locale, "customizer.a11y.visionHint")}
        </p>
      </Section>

      <Section title={t(locale, "customizer.a11y.motion")}>
        <div className="flex flex-wrap gap-2">
          {(["system", "full", "mild", "off"] as const).map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={motion === value}
              onClick={() => setA11y({ motion: value })}
              className={chip(motion === value)}
            >
              {t(locale, `customizer.a11y.motion.${value}`)}
            </button>
          ))}
        </div>
        <p className="mt-2 text-theme-xs rw-faint">
          {t(locale, `customizer.a11y.motionHint.${motion}`)}
        </p>
      </Section>

      <Section title={t(locale, "customizer.a11y.more")}>
        <ul className="space-y-2">
          {rows.map((row) => (
            <li key={row.key}>
              <FormCheck
                label={row.label}
                checked={Boolean(a11y[row.key])}
                onChange={(event) => setA11y({ [row.key]: event.target.checked })}
              />
            </li>
          ))}
        </ul>
      </Section>
    </>
  );
}
