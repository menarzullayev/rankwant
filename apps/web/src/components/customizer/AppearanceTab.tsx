"use client";

import { useState } from "react";

import { useCustomizer } from "@/context/CustomizerContext";
import { useTheme } from "@/context/ThemeContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";
import { STYLES, isDual, type StyleId } from "@/layout/styles";
import { FormSeg3, FormStepper } from "@/components/kit/FormExtras";
import { TEMPLATES } from "@/lib/theme/templates";
import {
  LINE_HEIGHT_MAX,
  LINE_HEIGHT_MIN,
  SCALE_MAX,
  SCALE_MIN,
  SIZE_MAX,
  SIZE_MIN,
  SIZE_STEP,
  TRACKING_MAX,
  TRACKING_MIN,
  WIDTH_MAX,
  WIDTH_MIN,
  WIDTH_STEP,
  WIDTH_STEPS,
  clampLineHeight,
  clampScale,
  clampSize,
  clampTracking,
  clampWidth,
} from "@/lib/theme/typography";
import {
  DEFAULT_NAV_MODE,
  DEFAULT_NAV_SHAPE,
  NAV_MODES,
  NAV_SHAPES,
} from "@/layout/nav-config";
import { DEFAULT_CARD, DEFAULT_PATTERN } from "@/lib/theme/apply";
import {
  VERDICT_VARIANTS,
  clampVerdictVariant,
} from "@/lib/theme/verdict";
import { STATUS_VARIANTS, clampStatusVariant } from "@/lib/theme/status";
import { LOADING_VARIANTS, clampLoadingVariant } from "@/lib/theme/loading";
import { SELECTABLE_PACKS, clampIconPack } from "@/lib/theme/icon-packs";
import { OVERLAY_VARIANTS, clampOverlayVariant } from "@/lib/theme/overlay";
import { FORM_VARIANTS, clampFormVariant } from "@/lib/theme/form";
import { Verdict } from "@/components/ui/Verdict";
import { Status } from "@/components/ui/Status";
import { Icon } from "@/components/ui/Icon";
import { Loading } from "@/components/ui/Loading";

import { AccentSection } from "./AccentSection";
import { DENSITIES, chip, type GroupId } from "./chrome";
import { Group, Section } from "./Group";
import { SavedTemplates } from "./SavedTemplates";

export function AppearanceTab() {
  const locale = useLocale();
  const [group, setGroup] = useState<GroupId>("look");
  return (
    <div className="space-y-4">
      <Group
        id="look"
        title={t(locale, "customizer.group.look")}
        open={group === "look"}
        onOpen={setGroup}
      >
        <TemplatesSection />
        <SavedTemplates />
      </Group>
      <Group
        id="color"
        title={t(locale, "customizer.group.color")}
        open={group === "color"}
        onOpen={setGroup}
      >
        <ThemeSection />
        <StyleSection />
        <AccentSection />
      </Group>
      <Group
        id="type"
        title={t(locale, "customizer.group.type")}
        open={group === "type"}
        onOpen={setGroup}
      >
        <FontSection />
        <SizeSection />
        <DensitySection />
      </Group>
      <Group
        id="system"
        title={t(locale, "customizer.group.system")}
        open={group === "system"}
        onOpen={setGroup}
      >
        <NavSection />
        <NavShapeSection />
        <WidthSection />
        <LookSection />
        <VerdictSection />
        <StatusSection />
        <LoadingSection />
        <OverlaySection />
        <FormSection />
        <IconPackSection />
      </Group>
    </div>
  );
}

function TemplatesSection() {
  const locale = useLocale();
  const { applyTemplate, template } = useCustomizer();
  return (
    <Section title={t(locale, "customizer.templates")}>
      {template ? null : (
        <p className="mb-2 rw-radius-sm rw-warn-soft px-2 py-1 text-theme-xs">
          {t(locale, "customizer.templateModified")}
        </p>
      )}
      <ul className="grid grid-cols-2 gap-2">
        {TEMPLATES.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              aria-pressed={template?.id === item.id}
              onClick={() => applyTemplate(item)}
              className={`w-full rw-radius-sm border px-3 py-2 text-start text-theme-sm transition rw-focus-ring ${
                template?.id === item.id ? "rw-accent-line" : "rw-line rw-hover-bg"
              }`}
            >
              <span className="block truncate font-medium rw-strong">
                {t(locale, `customizer.template.${item.id}`)}
              </span>
                <span className="block truncate text-theme-xs rw-faint">
                {t(
                  locale,
                  (STYLES.find((style) => style.id === item.style)?.labelKey ??
                    "customizer.style") as MessageKey,
                )}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </Section>
  );
}

function ThemeSection() {
  const locale = useLocale();
  const { appearance } = useCustomizer();
  const { mode, setMode } = useTheme();
  const dual = isDual((appearance.style ?? "clay") as StyleId);
  return (
    <Section title={t(locale, "customizer.theme")}>
      {dual ? (
        <FormSeg3
          label={t(locale, "customizer.theme")}
          value={mode}
          onChange={setMode}
          options={
            [
              { value: "light", label: t(locale, "theme.light") },
              { value: "dark", label: t(locale, "theme.dark") },
              { value: "system", label: t(locale, "theme.system") },
            ] as const
          }
        />
      ) : (
        <p className="text-theme-sm rw-dim">{t(locale, "customizer.themeFixed")}</p>
      )}
    </Section>
  );
}

function StyleSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  return (
    <Section title={t(locale, "customizer.style")}>
      <ul className="grid grid-cols-2 gap-2">
        {STYLES.map((style) => (
          <li key={style.id}>
            <button
              type="button"
              aria-pressed={appearance.style === style.id}
              onClick={() => setAppearance({ style: style.id })}
              className={`w-full rw-radius-sm border px-2.5 py-2 text-start text-theme-sm transition rw-focus-ring ${
                appearance.style === style.id ? "rw-accent-line" : "rw-line rw-hover-bg"
              }`}
            >
              <span className="block truncate font-medium rw-strong">
                {t(locale, style.labelKey)}
              </span>
              <span className="block truncate text-theme-xs rw-faint">
                {t(locale, style.hintKey)}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </Section>
  );
}

function DensitySection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  return (
    <Section title={t(locale, "customizer.density")}>
      <FormStepper
        label={t(locale, "customizer.density")}
        value={Math.max(0, DENSITIES.indexOf(appearance.density ?? "comfortable"))}
        options={DENSITIES.map((value) => t(locale, `customizer.density.${value}`))}
        onChange={(next) => setAppearance({ density: DENSITIES[next] })}
      />
    </Section>
  );
}

function NavSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const current = appearance.navMode ?? DEFAULT_NAV_MODE;
  return (
    <Section title={t(locale, "customizer.nav")}>
      <div className="flex flex-wrap gap-2">
        {NAV_MODES.map((mode) => (
          <button
            key={mode.id}
            type="button"
            aria-pressed={current === mode.id}
            onClick={() => setAppearance({ navMode: mode.id })}
            className={chip(current === mode.id)}
          >
            {t(locale, mode.labelKey)}
          </button>
        ))}
      </div>
      <p className="mt-2 text-theme-xs rw-faint">
        {t(locale, `navMode.${current}.hint`)}
      </p>
    </Section>
  );
}

function NavShapeSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const mode = appearance.navMode ?? DEFAULT_NAV_MODE;
  if (mode !== "topnav") return null;
  const current = appearance.navShape ?? DEFAULT_NAV_SHAPE;
  return (
    <Section title={t(locale, "customizer.navShape")}>
      <div className="flex flex-wrap gap-2">
        {NAV_SHAPES.map((shape) => (
          <button
            key={shape.id}
            type="button"
            aria-pressed={current === shape.id}
            onClick={() => setAppearance({ navShape: shape.id })}
            className={chip(current === shape.id)}
          >
            {t(locale, shape.labelKey)}
          </button>
        ))}
      </div>
      <p className="mt-2 text-theme-xs rw-faint">
        {t(locale, `navShape.${current}.hint`)}
      </p>
    </Section>
  );
}

function SizeSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const value = clampSize(appearance.size);
  const scale = clampScale(appearance.scale);
  const lineHeight = clampLineHeight(appearance.lineHeight);
  const tracking = clampTracking(appearance.tracking);
  const quick = [90, 100, 110, 120];
  return (
    <Section title={t(locale, "customizer.size")}>
      <label className="block text-theme-xs rw-faint">
        {t(locale, "customizer.size")} — {value}%
        <input
          type="range"
          min={SIZE_MIN}
          max={SIZE_MAX}
          step={SIZE_STEP}
          value={value}
          onChange={(event) => setAppearance({ size: Number(event.target.value) })}
          className="mt-1 w-full"
        />
      </label>
      <div className="mt-2 flex flex-wrap gap-2">
        {quick.map((preset) => (
          <button
            key={preset}
            type="button"
            aria-pressed={value === preset}
            onClick={() => setAppearance({ size: preset })}
            className={chip(value === preset)}
          >
            {preset}%
          </button>
        ))}
      </div>
      <p className="mt-2 text-theme-xs rw-faint">{t(locale, "customizer.sizeHint")}</p>
      <label className="mt-4 block text-theme-xs rw-faint">
        {t(locale, "customizer.scale")} — ×{scale.toFixed(2)}
        <input
          type="range"
          min={SCALE_MIN}
          max={SCALE_MAX}
          step={0.05}
          value={scale}
          onChange={(event) => setAppearance({ scale: Number(event.target.value) })}
          className="mt-1 w-full"
        />
      </label>
      <div className="mt-2 flex flex-wrap gap-2">
        {[0.9, 1, 1.1].map((preset) => (
          <button
            key={preset}
            type="button"
            aria-pressed={scale === preset}
            onClick={() => setAppearance({ scale: preset })}
            className={chip(scale === preset)}
          >
            ×{preset.toFixed(2)}
          </button>
        ))}
      </div>
      <p className="mt-2 text-theme-xs rw-faint">{t(locale, "customizer.scaleHint")}</p>
      <label className="mt-4 block text-theme-xs rw-faint">
        {t(locale, "customizer.lineHeight")} — ×{lineHeight.toFixed(2)}
        <input
          type="range"
          min={LINE_HEIGHT_MIN}
          max={LINE_HEIGHT_MAX}
          step={0.05}
          value={lineHeight}
          onChange={(event) =>
            setAppearance({ lineHeight: Number(event.target.value) })
          }
          className="mt-1 w-full"
        />
      </label>
      <label className="mt-3 block text-theme-xs rw-faint">
        {t(locale, "customizer.tracking")} — {tracking.toFixed(3)}em
        <input
          type="range"
          min={TRACKING_MIN}
          max={TRACKING_MAX}
          step={0.005}
          value={tracking}
          onChange={(event) =>
            setAppearance({ tracking: Number(event.target.value) })
          }
          className="mt-1 w-full"
        />
      </label>
      <p className="mt-2 text-theme-xs rw-faint">{t(locale, "customizer.typeHint")}</p>
    </Section>
  );
}

function FontSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const NAMES: Record<string, string> = {
    inter: "Inter",
    jakarta: "Plus Jakarta",
    roboto: "Roboto",
    "dm-sans": "DM Sans",
    lexend: "Lexend",
  };
  const FONTS: (string | null)[] = [null, "inter", "jakarta", "roboto", "dm-sans", "lexend"];
  const body = appearance.font ?? null;
  const heading = appearance.fontHeading ?? null;
  return (
    <>
      <Section title={t(locale, "customizer.font")}>
        <div className="flex flex-wrap gap-2">
          {FONTS.map((value) => (
            <button
              key={value ?? "default"}
              type="button"
              aria-pressed={body === value}
              onClick={() => setAppearance({ font: value })}
              className={chip(body === value)}
            >
              {value ? NAMES[value] : t(locale, "customizer.font.default")}
            </button>
          ))}
        </div>
        <p className="mt-2 text-theme-xs rw-faint">{t(locale, "customizer.fontHint")}</p>
      </Section>
      <Section title={t(locale, "customizer.fontHeading")}>
        <div className="flex flex-wrap gap-2">
          {FONTS.map((value) => (
            <button
              key={value ?? "same"}
              type="button"
              aria-pressed={heading === value}
              onClick={() => setAppearance({ fontHeading: value })}
              className={chip(heading === value)}
            >
              {value ? NAMES[value] : t(locale, "customizer.font.same")}
            </button>
          ))}
        </div>
        <p className="mt-2 text-theme-xs rw-faint">
          {t(locale, "customizer.fontHeadingHint")}
        </p>
      </Section>
    </>
  );
}

function LookSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const CARDS = ["default", "outline", "flat", "soft", "square"] as const;
  const PATTERNS = ["none", "grid", "dots", "diagonal", "mesh"] as const;
  const card = appearance.card ?? DEFAULT_CARD;
  const pattern = appearance.pattern ?? DEFAULT_PATTERN;
  return (
    <>
      <Section title={t(locale, "customizer.card")}>
        <div className="flex flex-wrap gap-2">
          {CARDS.map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={card === value}
              onClick={() => setAppearance({ card: value })}
              className={chip(card === value)}
            >
              {t(locale, `customizer.card.${value}`)}
            </button>
          ))}
        </div>
        <p className="mt-2 text-theme-xs rw-faint">{t(locale, "customizer.cardHint")}</p>
      </Section>
      <Section title={t(locale, "customizer.pattern")}>
        <div className="flex flex-wrap gap-2">
          {PATTERNS.map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={pattern === value}
              onClick={() => setAppearance({ pattern: value })}
              className={chip(pattern === value)}
            >
              {t(locale, `customizer.pattern.${value}`)}
            </button>
          ))}
        </div>
        <p className="mt-2 text-theme-xs rw-faint">{t(locale, "customizer.patternHint")}</p>
      </Section>
    </>
  );
}

function WidthSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const value = clampWidth(appearance.width);
  return (
    <Section title={t(locale, "customizer.width")}>
      <label className="block text-theme-xs rw-faint">
        {t(locale, "customizer.width")} — {value}px
        <input
          type="range"
          min={WIDTH_MIN}
          max={WIDTH_MAX}
          step={WIDTH_STEP}
          value={value}
          onChange={(event) => setAppearance({ width: Number(event.target.value) })}
          className="mt-1 w-full"
        />
      </label>
      <div className="mt-2 flex flex-wrap gap-2">
        {WIDTH_STEPS.map((preset) => (
          <button
            key={preset}
            type="button"
            aria-pressed={value === preset}
            onClick={() => setAppearance({ width: preset })}
            className={chip(value === preset)}
          >
            {preset}
          </button>
        ))}
      </div>
      <p className="mt-2 text-theme-xs rw-faint">{t(locale, "customizer.widthHint")}</p>
    </Section>
  );
}

function VerdictSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const current = clampVerdictVariant(appearance.verdictStyle);
  const def = VERDICT_VARIANTS.find((v) => v.id === current) ?? VERDICT_VARIANTS[0];
  const sample = ["AC", "WA", "TLE", "PARTIAL", "WRONG_TEST"];
  return (
    <Section title={t(locale, "customizer.verdict")}>
      <div className="flex flex-wrap gap-2">
        {VERDICT_VARIANTS.map((v) => (
          <button
            key={v.id}
            type="button"
            aria-pressed={current === v.id}
            onClick={() => setAppearance({ verdictStyle: v.id })}
            className={chip(current === v.id)}
          >
            {t(locale, v.labelKey)}
          </button>
        ))}
      </div>
      <div inert className="mt-3 flex flex-wrap items-center gap-3 rw-radius-sm border rw-divider p-3">
        {sample.map((v) => (
          <Verdict key={v} verdict={v} variant={current} percent={v === "AC" ? 100 : undefined} />
        ))}
      </div>
      <p className="mt-2 text-theme-xs rw-faint">{t(locale, def.hintKey)}</p>
    </Section>
  );
}

function StatusSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const current = clampStatusVariant(appearance.statusStyle);
  const def = STATUS_VARIANTS.find((v) => v.id === current) ?? STATUS_VARIANTS[0];
  return (
    <Section title={t(locale, "customizer.status")}>
      <div className="flex flex-wrap gap-2">
        {STATUS_VARIANTS.map((v) => (
          <button
            key={v.id}
            type="button"
            aria-pressed={current === v.id}
            onClick={() => setAppearance({ statusStyle: v.id })}
            className={chip(current === v.id)}
          >
            {t(locale, v.labelKey)}
          </button>
        ))}
      </div>
      <div inert className="mt-3 flex flex-wrap items-center gap-3 rw-radius-sm border rw-divider p-3">
        {(["ok", "warn", "bad", "info"] as const).map((s) => (
          <Status key={s} status={s} variant={current} />
        ))}
      </div>
      <p className="mt-2 text-theme-xs rw-faint">{t(locale, def.hintKey)}</p>
    </Section>
  );
}

function LoadingSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const current = clampLoadingVariant(appearance.loadingStyle);
  const def = LOADING_VARIANTS.find((v) => v.id === current) ?? LOADING_VARIANTS[0];
  return (
    <Section title={t(locale, "customizer.loading")}>
      <div className="flex flex-wrap gap-2">
        {LOADING_VARIANTS.map((v) => (
          <button
            key={v.id}
            type="button"
            aria-pressed={current === v.id}
            onClick={() => setAppearance({ loadingStyle: v.id })}
            className={chip(current === v.id)}
          >
            {t(locale, v.labelKey)}
          </button>
        ))}
      </div>
      <div inert className="mt-3 flex items-center justify-center rw-radius-sm border rw-divider p-4">
        <span className="w-full max-w-[14rem]">
          <Loading variant={current} />
        </span>
      </div>
      <p className="mt-2 text-theme-xs rw-faint">{t(locale, def.hintKey)}</p>
    </Section>
  );
}

function OverlaySection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const current = clampOverlayVariant(appearance.overlayStyle);
  const def = OVERLAY_VARIANTS.find((v) => v.id === current) ?? OVERLAY_VARIANTS[0];
  return (
    <Section title={t(locale, "customizer.overlay")}>
      <div className="flex flex-wrap gap-2">
        {OVERLAY_VARIANTS.map((v) => (
          <button
            key={v.id}
            type="button"
            aria-pressed={current === v.id}
            onClick={() => setAppearance({ overlayStyle: v.id })}
            className={chip(current === v.id)}
          >
            {t(locale, v.labelKey)}
          </button>
        ))}
      </div>
      <p className="mt-2 text-theme-xs rw-faint">
        {t(locale, def.hintKey)} {t(locale, "customizer.overlayHint")}
      </p>
    </Section>
  );
}

function FormSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const current = clampFormVariant(appearance.formStyle);
  const def = FORM_VARIANTS.find((v) => v.id === current) ?? FORM_VARIANTS[0];
  return (
    <Section title={t(locale, "customizer.form")}>
      <div className="flex flex-wrap gap-2">
        {FORM_VARIANTS.map((v) => (
          <button
            key={v.id}
            type="button"
            aria-pressed={current === v.id}
            onClick={() => setAppearance({ formStyle: v.id })}
            className={chip(current === v.id)}
          >
            {t(locale, v.labelKey)}
          </button>
        ))}
      </div>
      <p className="mt-2 text-theme-xs rw-faint">
        {t(locale, def.hintKey)} {t(locale, "customizer.formHint")}
      </p>
    </Section>
  );
}

function IconPackSection() {
  const locale = useLocale();
  const { appearance, setAppearance } = useCustomizer();
  const current = clampIconPack(appearance.iconPack);
  return (
    <Section title={t(locale, "customizer.iconPack")}>
      <div className="flex flex-wrap gap-2">
        {SELECTABLE_PACKS.map((p) => (
          <button
            key={p.id}
            type="button"
            aria-pressed={current === p.id}
            onClick={() => setAppearance({ iconPack: p.id })}
            className={chip(current === p.id)}
          >
            {p.name}
          </button>
        ))}
      </div>
      <div inert className="mt-3 space-y-3 rw-radius-sm border rw-divider p-3">
        <div className="flex flex-wrap items-center gap-3">
          <Icon name="nav.problems" />
          <Icon name="nav.leaderboard" />
          <Icon name="action.search" />
          <Icon name="action.edit" />
          <Icon name="status.warning" />
          <Icon name="ranking.trophy" />
        </div>
        <div className="flex flex-wrap items-center gap-3 border-t rw-divider pt-3">
          <Verdict verdict="AC" variant="icon" />
          <Verdict verdict="WA" variant="icon" />
          <span className="text-theme-xs rw-faint">
            {t(locale, "customizer.iconPackFixed")}
          </span>
        </div>
      </div>
      <p className="mt-2 text-theme-xs rw-faint">{t(locale, "customizer.iconPackHint")}</p>
    </Section>
  );
}
