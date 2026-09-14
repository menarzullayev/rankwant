"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";

import { useCustomizer } from "@/context/CustomizerContext";
import { useTheme } from "@/context/ThemeContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t } from "@/i18n/messages";
import { CheckIcon, CloseIcon, PaletteIcon } from "@/icons";
import { STYLES, isDual, type StyleId } from "@/layout/styles";
import type { A11yPrefs } from "@/lib/api";
import { passes, type AccentError } from "@/lib/theme/apply";
import { TEMPLATES } from "@/lib/theme/templates";

/** Namuna tuslari (D7). 14 ta — kam bo'lsa «o'z rangimni qo'yaman»
 *  ehtiyoji qoladi, ko'p bo'lsa tanlash qiyinlashadi.
 *
 *  Qiymat TUS, rang emas: yorqinlikni tizim har muhit uchun hisoblaydi
 *  (D42), chunki bitta rang ikki muhitga sig'maydi. */
const SWATCHES: { hue: number; sat: number }[] = [
  { hue: 0, sat: 70 },
  { hue: 20, sat: 80 },
  { hue: 38, sat: 85 },
  { hue: 52, sat: 70 },
  { hue: 95, sat: 55 },
  { hue: 140, sat: 55 },
  { hue: 170, sat: 60 },
  { hue: 195, sat: 70 },
  { hue: 215, sat: 75 },
  { hue: 240, sat: 65 },
  { hue: 262, sat: 70 },
  { hue: 290, sat: 60 },
  { hue: 320, sat: 65 },
  { hue: 345, sat: 70 },
];

const HIDDEN_KEY = "rw:customizer-hidden";

/** Yopilgani `localStorage` da — ya'ni tashqi tizim, React holati emas.
 *  Shuning uchun `useSyncExternalStore`: effektda `setState` qilish
 *  kaskad render keltiradi va loyihada taqiqlangan. */
const hiddenListeners = new Set<() => void>();

function subscribeHidden(onChange: () => void) {
  hiddenListeners.add(onChange);
  return () => {
    hiddenListeners.delete(onChange);
  };
}

function readHidden() {
  try {
    return localStorage.getItem(HIDDEN_KEY) === "1";
  } catch {
    // Private rejim — ko'rinadi, bu xavfsiz tomon.
    return false;
  }
}

function writeHidden(value: boolean) {
  try {
    localStorage.setItem(HIDDEN_KEY, value ? "1" : "0");
  } catch {
    // Kesh yozilmadi — sessiyada ishlaydi.
  }
  for (const listener of hiddenListeners) listener();
}

const SIZES = [90, 100, 110, 120] as const;
const DENSITIES = ["compact", "comfortable", "spacious"] as const;

/** Panel va suzuvchi tugma.
 *
 *  MODAL EMAS (D29): fon qoraytirilmaydi, fokus tuzog'i yo'q — sozlagichning
 *  butun ma'nosi sahifani KO'RISH, tuzoq esa uni to'sadi. Shu sababli
 *  `aria-modal` ishlatilmaydi: uni yolg'on e'lon qilish ekran o'quvchini
 *  chalg'itardi.
 */
export function Customizer() {
  const { open, setOpen, toggle } = useCustomizer();
  const locale = useLocale();
  const [tab, setTab] = useState<"appearance" | "a11y">("appearance");
  const panel = useRef<HTMLDivElement>(null);
  // Suzuvchi tugma yopilgani eslab qolinadi (D28) — doimiy element
  // sahifaning o'ng chetini to'sib qo'yardi.
  const hidden = useSyncExternalStore(subscribeHidden, readHidden, () => false);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setOpen(false);
        // Fokus ochgan tugmaga qaytadi (D29).
        document.getElementById("rw-customizer-open")?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, setOpen]);

  if (hidden && !open) {
    return (
      <button
        id="rw-customizer-open"
        type="button"
        onClick={() => writeHidden(false)}
        title={t(locale, "customizer.show")}
        className="fixed end-0 top-1/3 z-40 hidden size-10 items-center justify-center rw-radius-sm border rw-line rw-surface rw-dim-2 shadow-lg transition rw-hover-bg lg:flex"
      >
        <PaletteIcon className="size-4" />
      </button>
    );
  }

  return (
    <>
      {/* Suzuvchi tugma — telefonda YO'Q (D32): tor ekranda suzuvchi
          elementlar bir-biriga tegib ketadi. U yerda kirish nuqtasi —
          header ikonkasi va sozlamalar sahifasi. */}
      {!open && (
        <button
          id="rw-customizer-open"
          type="button"
          onClick={toggle}
          aria-expanded={false}
          title={`${t(locale, "customizer.title")} (Ctrl+.)`}
          className="fixed end-0 top-1/3 z-40 hidden flex-col items-center gap-1 rw-radius-sm border rw-line rw-surface px-1.5 py-3 text-theme-xs rw-dim-2 shadow-lg transition rw-hover-bg lg:flex"
        >
          <PaletteIcon className="size-4" />
          <span className="[writing-mode:vertical-rl]">
            {t(locale, "customizer.short")}
          </span>
        </button>
      )}

      {open && (
        <>
          {/* Yopish tugmasi — panel ustida, telefonda sheet tepasida. */}
          <div
            ref={panel}
            role="region"
            aria-label={t(locale, "customizer.title")}
            className="fixed inset-x-0 bottom-0 z-50 flex max-h-[55dvh] flex-col rounded-t-2xl border rw-line rw-surface shadow-2xl lg:inset-y-0 lg:end-0 lg:start-auto lg:max-h-none lg:w-[22rem] lg:rounded-none"
          >
            <header className="flex items-center justify-between gap-2 border-b rw-divide px-4 py-3">
              <h2 className="text-theme-lg font-semibold rw-strong">
                {t(locale, "customizer.title")}
              </h2>
              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label={t(locale, "customizer.close")}
                className="flex size-9 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg"
              >
                <CloseIcon className="size-4" />
              </button>
            </header>

            <nav className="flex gap-2 border-b rw-divide px-4 py-2">
              {(["appearance", "a11y"] as const).map((value) => (
                <button
                  key={value}
                  type="button"
                  aria-pressed={tab === value}
                  onClick={() => setTab(value)}
                  className={`rw-radius-sm px-3 py-1.5 text-theme-sm font-medium transition ${
                    tab === value ? "rw-accent-soft" : "rw-dim-2 rw-hover-bg"
                  }`}
                >
                  {t(locale, `customizer.tab.${value}`)}
                </button>
              ))}
            </nav>

            <div className="min-h-0 flex-1 space-y-6 overflow-y-auto px-4 py-4">
              {tab === "appearance" ? <AppearanceTab /> : <A11yTab />}
            </div>

            <footer className="border-t rw-divide px-4 py-3">
              <ResetRow />
            </footer>
          </div>
        </>
      )}
    </>
  );
}

/* ── Ko'rinish ────────────────────────────────────────────────────────── */

function AppearanceTab() {
  const locale = useLocale();
  const { appearance, setAppearance, applyTemplate, template } = useCustomizer();
  const { mode, setMode } = useTheme();
  const dual = isDual((appearance.style ?? "clay") as StyleId);

  return (
    <>
      <Section title={t(locale, "customizer.templates")}>
        {template ? null : (
          // `rw-warn-soft` + `rw-warn-ink` — token shartnomasi shu:
          // `-ink` faqat o'z `-soft` foni ustida o'qiladi. Sirt ustida
          // ishlatilsa `clay` da 2.87:1 bo'ladi (o'lchandi).
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
                  {item.style}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </Section>

      <SavedTemplates />

      <Section title={t(locale, "customizer.theme")}>
        {dual ? (
          <div className="flex flex-wrap gap-2">
            {(["light", "dark", "system"] as const).map((value) => (
              <button
                key={value}
                type="button"
                aria-pressed={mode === value}
                onClick={() => setMode(value)}
                className={chip(mode === value)}
              >
                {t(locale, `theme.${value}`)}
              </button>
            ))}
          </div>
        ) : (
          // Bir muhitli uslub (D6) — tanlagich o'chadi va SABAB aytiladi.
          <p className="text-theme-sm rw-dim">
            {t(locale, "customizer.themeFixed")}
          </p>
        )}
      </Section>

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

      <AccentSection />

      <Section title={t(locale, "customizer.font")}>
        <div className="flex flex-wrap gap-2">
          {[null, "inter", "jakarta", "roboto", "dm-sans"].map((value) => (
            <button
              key={value ?? "default"}
              type="button"
              aria-pressed={(appearance.font ?? null) === value}
              onClick={() => setAppearance({ font: value })}
              className={chip((appearance.font ?? null) === value)}
            >
              {value
            ? // Shrift nomi BREND nomi — tarjima qilinmaydi ("Inter"
              // hamma tilda "Inter"). `t()` orqali o'tkazilsa, kalit
              // qo'shilmagani uchun xom nom chiqardi.
              { inter: "Inter", jakarta: "Plus Jakarta", roboto: "Roboto", "dm-sans": "DM Sans" }[
                value
              ]
            : t(locale, "customizer.font.default")}
            </button>
          ))}
        </div>
      </Section>

      <Section title={t(locale, "customizer.size")}>
        <div className="flex flex-wrap gap-2">
          {SIZES.map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={(appearance.size ?? 100) === value}
              onClick={() => setAppearance({ size: value })}
              className={chip((appearance.size ?? 100) === value)}
            >
              {value}%
            </button>
          ))}
        </div>
      </Section>

      <Section title={t(locale, "customizer.density")}>
        <div className="flex flex-wrap gap-2">
          {DENSITIES.map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={(appearance.density ?? "comfortable") === value}
              onClick={() => setAppearance({ density: value })}
              className={chip((appearance.density ?? "comfortable") === value)}
            >
              {t(locale, `customizer.density.${value}`)}
            </button>
          ))}
        </div>
      </Section>
    </>
  );
}

/** Rang bo'limi — namunalar + erkin tus, jonli kontrast ko'rsatkichi.
 *
 *  ⚠️ AA dan o'tmagan kombinatsiya SAQLANMAYDI (D11). Ogohlantirib ruxsat
 *  berish «o'qib bo'lmaydigan interfeys» holatini yaratardi va uni keyin
 *  jamoa tuzatishi kerak bo'lardi. */
function AccentSection() {
  const locale = useLocale();
  const { appearance, setAppearance, preview } = useCustomizer();
  const [hue, setHue] = useState(appearance.accent?.hue ?? 215);
  const [sat, setSat] = useState(appearance.accent?.sat ?? 70);
  // Accent qo'llanmay qolsa sabab shu yerda ko'rsatiladi. Ilgari
  // `AccentResult.error` da tayyor o'zbekcha satr bor edi, lekin uni
  // HECH KIM o'qimasdi — ya'ni nosozlik jimgina o'tardi.
  const [failure, setFailure] = useState<AccentError | null>(null);

  const trial = preview(hue, sat);
  const ok = passes(trial.button) && passes(trial.ink);
  // Joriy (qo'llangan) rang — holat o'rniga shu yerda o'lchanadi, chunki
  // `preview` DOM ni o'qiydi va panel faqat hidratsiyadan keyin chiziladi.
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
              aria-label={`hue ${swatch.hue}`}
              aria-pressed={appearance.accent?.hue === swatch.hue}
              onClick={() => {
                setHue(swatch.hue);
                setSat(swatch.sat);
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
          >
            <CheckIcon className="size-3.5" />
          </button>
        </li>
      </ul>

      <label className="block text-theme-xs rw-faint">
        {t(locale, "customizer.hue")}
        <input
          type="range"
          min={0}
          max={359}
          value={hue}
          onChange={(event) => setHue(Number(event.target.value))}
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
          onChange={(event) => setSat(Number(event.target.value))}
          className="mt-1 w-full"
        />
      </label>

      <div className="mt-3 space-y-1">
        <Indicator
          label={t(locale, "customizer.contrastButton")}
          ratio={trial.button}
        />
        <Indicator label={t(locale, "customizer.contrastText")} ratio={trial.ink} />
        {!ok && (
          <p className="rw-radius-sm rw-bad-soft px-2 py-1 text-theme-xs">
            {t(locale, "customizer.contrastBlocked")}
          </p>
        )}
        {ok && failure && (
          <p
            role="alert"
            className="rw-radius-sm rw-bad-soft px-2 py-1 text-theme-xs"
          >
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

/** Jonli kontrast ko'rsatkichi (D11). `null` — o'lchanmagan, ya'ni
 *  «o'tdi» EMAS: o'qib bo'lmagan qiymat xato. */
function Indicator({ label, ratio }: { label: string; ratio: number | null }) {
  const good = passes(ratio);
  return (
    // `-soft` foni SHART: `-ink` faqat shu fon ustida AA dan o'tadi.
    // Holat faqat rang bilan emas — ✓/✗ belgisi ham bor (WCAG 1.4.1).
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

/* ── Qulaylik ─────────────────────────────────────────────────────────── */

function A11yTab() {
  const locale = useLocale();
  const { a11y, setA11y } = useCustomizer();
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
          {(["system", "reduce"] as const).map((value) => (
            <button
              key={value}
              type="button"
              aria-pressed={(a11y.motion ?? "system") === value}
              onClick={() => setA11y({ motion: value })}
              className={chip((a11y.motion ?? "system") === value)}
            >
              {t(locale, `customizer.a11y.motion.${value}`)}
            </button>
          ))}
        </div>
      </Section>

      <Section title={t(locale, "customizer.a11y.more")}>
        <ul className="space-y-2">
          {rows.map((row) => (
            <li key={row.key}>
              <label className="flex items-center gap-2 text-theme-sm rw-dim-2">
                <input
                  type="checkbox"
                  checked={Boolean(a11y[row.key])}
                  onChange={(event) => setA11y({ [row.key]: event.target.checked })}
                  className="size-4"
                />
                {row.label}
              </label>
            </li>
          ))}
        </ul>
      </Section>
    </>
  );
}

/* ── Tiklash ──────────────────────────────────────────────────────────── */

/** Uch bosqichli tiklash (D25): bitta tugma bo'lsa, bitta xato rangni
 *  qaytarish uchun ham butun ko'rinish yo'qolardi. */
function ResetRow() {
  const locale = useLocale();
  const { undo, canUndo, resetAll } = useCustomizer();
  const [confirming, setConfirming] = useState(false);
  return (
    <div className="flex flex-wrap items-center gap-2">
      <button
        type="button"
        disabled={!canUndo}
        onClick={undo}
        className="rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-dim-2 transition rw-hover-bg disabled:opacity-40"
      >
        {t(locale, "customizer.undo")}
      </button>
      {confirming ? (
        <>
          <button
            type="button"
            onClick={() => {
              resetAll();
              setConfirming(false);
            }}
            className="rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-bad-ink"
          >
            {t(locale, "customizer.resetConfirm")}
          </button>
          <button
            type="button"
            onClick={() => setConfirming(false)}
            className="text-theme-sm rw-dim-2"
          >
            {t(locale, "customizer.cancel")}
          </button>
        </>
      ) : (
        <button
          type="button"
          onClick={() => setConfirming(true)}
          className="rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-dim-2 transition rw-hover-bg"
        >
          {t(locale, "customizer.reset")}
        </button>
      )}
    </div>
  );
}

/* ── Kichik bo'laklar ─────────────────────────────────────────────────── */

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h3 className="mb-2 text-theme-sm font-semibold rw-strong">{title}</h3>
      {children}
    </section>
  );
}

const chip = (active: boolean) =>
  `rw-radius-sm border px-3 py-1.5 text-theme-sm transition rw-focus-ring ${
    active ? "rw-accent-line rw-accent-soft" : "rw-line rw-dim-2 rw-hover-bg"
  }`;


/** Shaxsiy shablonlar (D21) — hisobda 5 tagacha, mehmonda 2 ta.
 *
 *  Nom oddiy matn maydonida kiritiladi, `window.prompt` bilan emas: u
 *  bloklaydi, uslubi yo'q va mobil brauzerda ba'zan umuman ko'rinmaydi. */
function SavedTemplates() {
  const locale = useLocale();
  const {
    templates,
    saveTemplate,
    removeTemplate,
    applySaved,
    templateLimit,
    shareLink,
  } = useCustomizer();
  const [name, setName] = useState("");
  const [copied, setCopied] = useState(false);
  const full = templates.length >= templateLimit;

  return (
    <Section title={t(locale, "customizer.myTemplates")}>
      <button
        type="button"
        onClick={() => {
          void navigator.clipboard.writeText(shareLink());
          setCopied(true);
        }}
        className="mb-2 w-full rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-dim-2 transition rw-hover-bg"
      >
        {copied ? t(locale, "customizer.linkCopied") : t(locale, "customizer.copyLink")}
      </button>

      {templates.length > 0 && (
        <ul className="mb-2 space-y-1">
          {templates.map((row) => (
            <li key={row.name} className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => applySaved(row)}
                className="min-w-0 flex-1 truncate rw-radius-sm border rw-line px-2.5 py-1.5 text-start text-theme-sm rw-strong transition rw-hover-bg"
              >
                {row.name}
              </button>
              <button
                type="button"
                onClick={() => removeTemplate(row.name)}
                aria-label={`${t(locale, "customizer.delete")}: ${row.name}`}
                className="flex size-8 shrink-0 items-center justify-center rw-radius-sm rw-dim-2 transition rw-hover-bg"
              >
                <CloseIcon className="size-3.5" />
              </button>
            </li>
          ))}
        </ul>
      )}

      {full ? (
        <p className="text-theme-xs rw-faint">
          {t(locale, "customizer.templateLimit")} — {templateLimit}
        </p>
      ) : (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            saveTemplate(name);
            setName("");
          }}
          className="flex items-center gap-2"
        >
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            maxLength={24}
            placeholder={t(locale, "customizer.templateName")}
            aria-label={t(locale, "customizer.templateName")}
            className="min-w-0 flex-1 rw-radius-sm border rw-line rw-field-bg px-2.5 py-1.5 text-theme-sm rw-strong"
          />
          <button
            type="submit"
            disabled={name.trim() === ""}
            className="rw-radius-sm border rw-line px-3 py-1.5 text-theme-sm rw-dim-2 transition rw-hover-bg disabled:opacity-40"
          >
            {t(locale, "customizer.save")}
          </button>
        </form>
      )}
    </Section>
  );
}
