"use client";

import { useState } from "react";

import { SignInGate } from "@/components/auth/SignInGate";
import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t } from "@/i18n/messages";
import { ApiError, postJson, type ContestViewer } from "@/lib/api";

/** The visitor's own line on a contest page: register, or be told what
 *  they are here (ADR-0055, part 2).
 *
 *  An insider — author, tester, jury, organizer — is told they take part
 *  unrated; before the start a tester is told the problems are open to
 *  them and what they send counts nowhere.
 */
export function ContestEntry({
  slug,
  viewer,
  signedIn,
  finished,
}: {
  slug: string;
  viewer: ContestViewer | null;
  signedIn: boolean;
  finished: boolean;
}) {
  const locale = useLocale();
  const [registered, setRegistered] = useState(viewer?.registered ?? false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!signedIn) {
    return finished ? null : <SignInGate reason="contest" />;
  }

  async function register() {
    setBusy(true);
    setError(null);
    try {
      await postJson(`/contests/${slug}/register/`, {});
      setRegistered(true);
    } catch (e) {
      setError(e instanceof ApiError ? errorText(locale, e.code, e.message) : String(e));
    } finally {
      setBusy(false);
    }
  }

  const role = viewer?.role ?? "";
  // A finished contest has nothing to register for; only an insider has
  // something to be told.
  if (finished && !role) return null;
  return (
    <section
      aria-labelledby="contest-entry"
      data-contest-entry={role || "participant"}
      className="space-y-3 rw-radius border rw-line rw-surface p-5"
    >
      {role && (
        <div className="space-y-1">
          <h2 id="contest-entry" className="text-theme-base font-semibold rw-strong">
            {t(locale, `contest.insider.title.${role}`)}
          </h2>
          <p className="text-theme-sm rw-dim">
            {t(locale, viewer?.testing ? "contest.insider.testing" : "contest.insider.unrated")}
          </p>
        </div>
      )}
      {!role && (
        <h2 id="contest-entry" className="sr-only">
          {t(locale, "contest.entry.title")}
        </h2>
      )}
      {!finished &&
        (registered ? (
          <p className="text-theme-sm font-medium rw-ok-ink" role="status">
            {t(locale, "contest.entry.registered")}
          </p>
        ) : (
          <div className="flex flex-wrap items-center gap-3">
            <Button onClick={register} busy={busy}>
              {t(locale, "contest.entry.register")}
            </Button>
            {role && (
              <span className="text-theme-xs rw-dim">{t(locale, "contest.entry.unratedNote")}</span>
            )}
          </div>
        ))}
      {error && (
        <p className="text-theme-sm rw-bad-ink" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}
