"use client";

import { useState } from "react";

import { useCustomizer } from "@/context/CustomizerContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t } from "@/i18n/messages";
import { accentGateKind, passes, type AccentError } from "@/lib/theme/apply";
import { accentToHex, hexToAccent } from "@/lib/theme/color";
import { Icon } from "@/components/ui/Icon";

import { SWATCHES } from "./chrome";
import { Section } from "./Group";

export function AccentSection() {
  const locale = useLocale();
  const { appearance, setAppearance, preview } = useCustomizer();
  const [hue, setHue] = useState(appearance.accent?.hue ?? 215);
  const [sat, setSat] = useState(appearance.accent?.sat ?? 70);
  const [hex, setHex] = useState(() => accentToHex(hue, sat));
  const [failure, setFailure] = useState<AccentError | null>(null);

  const trial = preview(hue, sat);
  const ok = passes(trial.button) && passes(trial.ink);
  const gate = ok ? null : accentGateKind(trial);
  const current = appearance.accent
    ? preview(appearance.accent.hue, appearance.accent.sat)
    : trial;

  const apply = (patch: Parameters<typeof setAppearance>[0]) => {
    const result = setAppearance(patch);
    setFailure(result.ok ? null : (result.error ?? null));
  };

  return (
    <Section title={t(locale, "customizer.accent")}>
      <ul className="mb-3 flex flex-wrap gap-2">
        {SWATCHES.map((swatch) => (
          <li key={`${swatch.hue}-${swatch.sat}`}>
            <button
              type="button"
              aria-label={t(locale, swatch.nameKey)}
              aria-pressed={appearance.accent?.hue === swatch.hue}
              onClick={() => {
                setHue(swatch.hue);
                setSat(swatch.sat);
                setHex(accentToHex(swatch.hue, swatch.sat));
                apply({ accent: { hue: swatch.hue, sat: swatch.sat } });
              }}
              style={{ background: `hsl(${swatch.hue} ${swatch.sat}% 45%)` }}
              className={`size-8 rounded-full border-2 transition ${
                appearance.accent?.hue === swatch.hue ? "rw-accent-line" : "border-transparent"
              }`}
            />
          </li>
        ))}
        <li>
          <button
            type="button"
            aria-pressed={!appearance.accent}
            onClick={() => apply({ accent: null })}
            className="flex size-8 items-center justify-center rounded-full border rw-line text-theme-xs rw-dim-2"
            title={t(locale, "customizer.accentDefault")}
            aria-label={t(locale, "customizer.accentDefault")}
          >
            <Icon name="action.confirm" className="size-3.5" />
          </button>
        </li>
      </ul>

      <label className="mt-3 block text-theme-xs rw-faint">
        {t(locale, "customizer.hex")}
        <div className="mt-1 flex items-center gap-2">
          <input
            type="text"
            value={hex}
            spellCheck={false}
            maxLength={7}
            placeholder="#5B8CFF"
            onChange={(event) => setHex(event.target.value)}
            onBlur={() => {
              const next = hexToAccent(hex);
              if (next) {
                setHue(next.hue);
                setSat(next.sat);
                apply({ accent: next });
              } else {
                setHex(accentToHex(hue, sat));
              }
            }}
            aria-label={t(locale, "customizer.hex")}
            className="min-w-0 flex-1 rw-radius-sm border rw-line rw-field-bg px-2.5 py-1.5 font-mono text-theme-sm rw-strong uppercase rw-fm-inp"
          />
          <span
            aria-hidden="true"
            className="size-7 shrink-0 rounded-full border rw-line"
            style={{ background: hexToAccent(hex) ? hex : accentToHex(hue, sat) }}
          />
        </div>
      </label>

      <label className="mt-3 block text-theme-xs rw-faint">
        {t(locale, "customizer.hue")}
        <input
          type="range"
          min={0}
          max={359}
          value={hue}
          onChange={(event) => {
            const next = Number(event.target.value);
            setHue(next);
            setHex(accentToHex(next, sat));
          }}
          className="mt-1 w-full"
        />
      </label>
      <label className="block text-theme-xs rw-faint">
        {t(locale, "customizer.saturation")}
        <input
          type="range"
          min={0}
          max={100}
          value={sat}
          onChange={(event) => {
            const next = Number(event.target.value);
            setSat(next);
            setHex(accentToHex(hue, next));
          }}
          className="mt-1 w-full"
        />
      </label>

      <div className="mt-3 space-y-1">
        <Indicator label={t(locale, "customizer.contrastButton")} ratio={trial.button} />
        <Indicator label={t(locale, "customizer.contrastText")} ratio={trial.ink} />
        {gate && (
          <p role="alert" className="rw-radius-sm rw-bad-soft px-2 py-1 text-theme-xs">
            {gate === "aa"
              ? t(locale, "customizer.contrastBlocked")
              : errorText(locale, gate, "")}
          </p>
        )}
        {ok && failure && (
          <p role="alert" className="rw-radius-sm rw-bad-soft px-2 py-1 text-theme-xs">
            {errorText(locale, failure, "")}
          </p>
        )}
      </div>

      <button
        type="button"
        disabled={!ok}
        onClick={() => apply({ accent: { hue, sat } })}
        className="mt-3 w-full rw-radius-sm rw-accent-bg px-3 py-2 text-theme-sm font-medium disabled:opacity-50"
      >
        {t(locale, "customizer.accentApply")}
      </button>
      {appearance.accent && current.ink !== null && (
        <p className="mt-2 text-theme-xs rw-faint">
          {t(locale, "customizer.accentCurrent")}: {current.ink.toFixed(2)}:1
        </p>
      )}
    </Section>
  );
}

function Indicator({ label, ratio }: { label: string; ratio: number | null }) {
  const good = passes(ratio);
  return (
    <p
      className={`flex items-center justify-between rw-radius-sm px-2 py-1 text-theme-xs ${
        good ? "rw-ok-soft" : "rw-bad-soft"
      }`}
    >
      <span>{label}</span>
      <span className="tabular-nums">
        {ratio === null ? "—" : `${ratio.toFixed(2)}:1`} {good ? "✓" : "✗"}
      </span>
    </p>
  );
}
