"use client";

import { useEffect, useState } from "react";

import type { FieldStatus } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { getJson } from "@/lib/api";

/** Shorter names are not asked about: the server rejects them anyway. */
const MIN_LENGTH = 3;

/**
 * Live "free / taken" note for a handle being typed.
 *
 * Used by both sign-up steps, so the answer and its timing are the same
 * on each. One request goes out once typing pauses and the previous one is
 * cancelled; without that, "ali" sent four requests whose answers could
 * arrive out of order and leave the last one stale.
 *
 * `enabled: false` (an empty optional field, or a format already refused
 * locally) asks nothing and shows nothing.
 */
export function useUsernameCheck(
  value: string,
  enabled = true,
): FieldStatus | undefined {
  const locale = useLocale();
  const [result, setResult] = useState<{ for: string; status: FieldStatus }>();
  const name = value.trim();
  const active = enabled && name.length >= MIN_LENGTH;

  useEffect(() => {
    if (!active) return;
    const stop = new AbortController();
    const timer = setTimeout(() => {
      getJson<{ available: boolean; reason: string }>(
        `/auth/username-check/?u=${encodeURIComponent(name)}`,
        { signal: stop.signal },
      )
        .then((data) =>
          setResult({
            for: name,
            status: data.available
              ? { kind: "ok", text: t(locale, "auth.usernameFree") }
              : { kind: "bad", text: data.reason },
          }),
        )
        // A network failure says nothing: the server checks again on
        // submit, and a false "taken" would turn the person back for nothing.
        .catch(() => undefined);
    }, 400);
    return () => {
      clearTimeout(timer);
      stop.abort();
    };
  }, [active, name, locale]);

  if (!active) return undefined;
  // The answer is kept with the name it was for, so a reply to an earlier
  // keystroke is never shown beside a newer one.
  return result?.for === name
    ? result.status
    : { kind: "busy", text: t(locale, "auth.checking") };
}
