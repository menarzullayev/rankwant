"use client";

import { Icon } from "@/components/ui/Icon";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, type MessageKey } from "@/i18n/messages";
import { passwordRules, strength, type Strength } from "@rankwant/shared/password";

/** Show/hide button for a password input: an icon (never the old `●/○`
 *  text), 44 px, and `aria-pressed` says which way it is set. */
export function PasswordEye({
  visible,
  onToggle,
}: {
  visible: boolean;
  onToggle: () => void;
}) {
  const locale = useLocale();
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-pressed={visible}
      aria-label={t(locale, "auth.togglePassword")}
      title={t(locale, "auth.togglePassword")}
      className="grid h-11 w-11 place-items-center rw-radius-sm rw-dim transition hover:rw-strong rw-focus-ring"
    >
      {visible ? <Icon name="action.eyeOff" /> : <Icon name="action.eye" />}
    </button>
  );
}

const RULES: { key: "length" | "notNumeric" | "varied"; label: MessageKey }[] = [
  { key: "length", label: "auth.rule.length" },
  { key: "notNumeric", label: "auth.rule.notNumeric" },
  { key: "varied", label: "auth.rule.varied" },
];

/** The password rules, ticked live as the person types. Each line carries a
 *  mark as well as a colour (WCAG 1.4.1). Only what the page can judge
 *  locally is listed; the server's own refusals (common password, too
 *  similar to the handle) come back as a note on the field. */
export function PasswordRules({ value }: { value: string }) {
  const locale = useLocale();
  const state = passwordRules(value);
  return (
    <ul aria-label={t(locale, "auth.rulesLabel")} className="-mt-2 flex flex-col gap-1">
      {RULES.map(({ key, label }) => {
        // Nothing is "met" until something is typed: an empty field is not a
        // password that is not only digits.
        const met = value.length > 0 && state[key];
        return (
          <li
            key={key}
            className={`flex items-center gap-2 text-theme-xs ${met ? "rw-ok-ink" : "rw-dim"}`}
          >
            <span aria-hidden className="w-3 text-center">
              {met ? "✓" : "○"}
            </span>
            <span>{t(locale, label)}</span>
          </li>
        );
      })}
    </ul>
  );
}

const TONE: Record<Exclude<Strength, 0>, "bad" | "warn" | "ok"> = {
  1: "bad",
  2: "bad",
  3: "warn",
  4: "ok",
  5: "ok",
};

/** Five-level strength bar. Colour is never the only carrier (WCAG 1.4.1):
 *  the level is written in words and the number of filled segments changes
 *  too. It blocks nothing — the acceptance rule lives on the server.
 *
 *  `refused` caps the bar at the lowest level for a password the server has
 *  already turned down, so the bar never calls it strong. */
export function StrengthBar({ value, refused = false }: { value: string; refused?: boolean }) {
  const locale = useLocale();
  const raw = strength(value);
  if (!raw) return null;
  const level = (refused ? 1 : raw) as Exclude<Strength, 0>;
  const tone = TONE[level];
  return (
    <p className="-mt-1 flex items-center gap-2" role="status" aria-live="polite">
      <span className="flex flex-1 gap-1" aria-hidden>
        {[1, 2, 3, 4, 5].map((step) => (
          <span
            key={step}
            className="h-1.5 flex-1 rw-radius-sm"
            style={{
              // Empty segments use `--rw-divider`: `--rw-line` is
              // transparent in `clay` and `neu`.
              background: step <= level ? `var(--rw-${tone}-ink)` : "var(--rw-divider)",
            }}
          />
        ))}
      </span>
      <span className={`text-theme-xs rw-${tone}-ink`}>
        {t(locale, `auth.strength${level}` as MessageKey)}
      </span>
    </p>
  );
}

/** Maps Django's English password-validator messages to a translated key.
 *  The server answers with `code: "invalid"` for every field error, so the
 *  text is the only thing to tell the reasons apart. */
export function passwordRefusalKey(text: string): MessageKey | null {
  const message = text.toLowerCase();
  if (message.includes("too common")) return "auth.pwCommon";
  if (message.includes("entirely numeric")) return "auth.pwNumeric";
  if (message.includes("too similar")) return "auth.pwSimilar";
  if (message.includes("too short")) return "auth.passwordHint";
  return null;
}
