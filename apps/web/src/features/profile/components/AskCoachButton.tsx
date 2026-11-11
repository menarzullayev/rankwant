"use client";

import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t } from "@/i18n/messages";
import { ApiError, postJson } from "@/lib/api";

/** Ask the profile's owner to coach the reader (ADR-0061 § 4). Signed-in
 *  readers only: a guest has nobody to be coached as. */
export function AskCoachButton({ username }: { username: string }) {
  const locale = useLocale();
  const { user } = useSession();
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  if (!user || user.username === username) return null;

  async function ask() {
    setBusy(true);
    setError("");
    try {
      await postJson("/coaching/", { coach: username });
      setSent(true);
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code, err.message) : String(err));
    } finally {
      setBusy(false);
    }
  }

  if (sent)
    return (
      <p role="status" className="self-center text-theme-sm rw-dim">
        {t(locale, "coaching.asked")}{" "}
        <Link href="/coaching" className="rw-accent-ink hover:underline">
          {t(locale, "coaching.title")}
        </Link>
      </p>
    );

  return (
    <>
      <Button variant="outline" busy={busy} onClick={() => void ask()}>
        {t(locale, "coaching.askThis")}
      </Button>
      {error && (
        <p role="alert" className="w-full text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
    </>
  );
}
