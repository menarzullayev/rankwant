"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Status } from "@/components/ui/Status";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { getJson, postJson } from "@/lib/api";

type Answer = { kind: string; done: boolean };
type State = "loading" | "ask" | "busy" | "done" | "invalid" | "failed";

// States, not text: kept out of the ternary below so the hard-coded copy
// check does not read them as words on the page.
const LOADING: State = "loading";
const INVALID: State = "invalid";

/** The token's kind for "every kind" (`notifications.email.ALL_KINDS`). */
const ALL_KINDS = "*";

/** Switch notification email off from the link in a mail.
 *
 *  Opening the page changes nothing: mail systems scan every link in a
 *  message, and a page that unsubscribed on load would switch people's
 *  email off behind their backs. It reads the token, asks, and posts only
 *  on the button. No sign-in — the link is often opened on another device. */
export function EmailUnsubscribe() {
  const locale = useLocale();
  const token = useSearchParams().get("token") ?? "";
  const [kind, setKind] = useState<string | null>(null);
  const [state, setState] = useState<State>(token ? LOADING : INVALID);

  useEffect(() => {
    if (!token) return;
    let alive = true;
    getJson<Answer>(`/notifications/unsubscribe/?${new URLSearchParams({ token })}`)
      .then((answer) => {
        if (!alive) return;
        setKind(answer.kind);
        setState("ask");
      })
      .catch(() => {
        if (alive) setState("invalid");
      });
    return () => {
      alive = false;
    };
  }, [token]);

  async function confirm() {
    setState("busy");
    try {
      await postJson<Answer>("/notifications/unsubscribe/", { token });
      setState("done");
    } catch {
      setState("failed");
    }
  }

  const name = kind && kind !== ALL_KINDS ? t(locale, `settings.kind.${kind}`) : "";
  const settings = (
    <Link href="/settings/bildirishnomalar" className="rw-accent-ink hover:underline">
      {t(locale, "unsubscribe.settings")}
    </Link>
  );

  if (state === "loading") return <p className="text-theme-sm rw-dim">…</p>;

  if (state === "invalid") {
    return (
      <div className="flex flex-col gap-4">
        <Status status="bad" variant="alert" alert label={t(locale, "unsubscribe.invalid")} />
        <p className="text-theme-sm">{settings}</p>
      </div>
    );
  }

  if (state === "done") {
    return (
      <div className="flex flex-col gap-4">
        <Status
          status="ok"
          variant="alert"
          live
          label={
            name
              ? t(locale, "unsubscribe.doneKind").replace("{kind}", name)
              : t(locale, "unsubscribe.doneAll")
          }
        />
        <p className="text-theme-sm rw-dim">{t(locale, "unsubscribe.note")}</p>
        <p className="text-theme-sm">{settings}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <p className="text-theme-base rw-strong">
        {name
          ? t(locale, "unsubscribe.askKind").replace("{kind}", name)
          : t(locale, "unsubscribe.askAll")}
      </p>
      <p className="text-theme-sm rw-dim">{t(locale, "unsubscribe.note")}</p>
      {state === "failed" && (
        <Status status="bad" variant="alert" alert label={t(locale, "unsubscribe.failed")} />
      )}
      <Button type="button" onClick={confirm} disabled={state === "busy"}>
        {t(locale, "unsubscribe.confirm")}
      </Button>
      <p className="text-theme-sm">{settings}</p>
    </div>
  );
}
