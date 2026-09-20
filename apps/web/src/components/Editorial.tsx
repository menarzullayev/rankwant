"use client";

import type { Route } from "next";
import { useState } from "react";

import { CodeCopy } from "@/components/kit/CopyControl";
import { Markdown } from "@/components/Markdown";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { ApiError, unlockEditorial, type EditorialState } from "@/lib/api";
import Link from "next/link";

/** Yechim tahlili — ADR-0013 spoyler darvozasi.
 *
 * Masalani yechgan odam bepul ko'radi; yechmagani Qvant sarflaydi.
 * Bu paywall emas: bepul yo'l — masalani yechish — har doim ochiq, va
 * u asosiy yo'l. Qvant faqat sabrsizlikni sotib oladi. */
export function Editorial({
  slug,
  text,
  state,
}: {
  slug: string;
  text: string;
  state: EditorialState;
}) {
  const { user, ready } = useSession();
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const [body, setBody] = useState(text);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function unlock() {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const result = await unlockEditorial(slug);
      setBody(result.editorial);
      setOpen(true);
    } catch (caught) {
      setError(
        caught instanceof ApiError && caught.status === 402
          ? fill(t(locale, "editorial.notEnough"), { price: state.price })
          : t(locale, "editorial.unlockFailed"),
      );
    } finally {
      setBusy(false);
    }
  }

  if (!ready) return null;

  if (!user) {
    return (
      <Card title={t(locale, "editorial.title")}>
        <p className="text-theme-sm rw-faint">
          {t(locale, "editorial.lockedTitle")}{" "}
          <Link href={"/login?tab=login" as Route} className="underline rw-accent-ink">
            {t(locale, "editorial.login")}
          </Link>
        </p>
      </Card>
    );
  }

  if (!body) {
    return (
      <Card title={t(locale, "editorial.title")}>
        <div className="space-y-3">
          <p className="text-theme-sm rw-faint">
            {t(locale, "editorial.lockedLead")}{" "}
            {fill(t(locale, "editorial.lockedBody"), { price: state.price })}
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="outline" onClick={unlock} disabled={busy}>
              {busy
                ? t(locale, "editorial.unlocking")
                : fill(t(locale, "editorial.unlockFor"), { price: state.price })}
            </Button>
            {error && <span className="text-theme-sm rw-bad-ink">{error}</span>}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card
      title={t(locale, "editorial.title")}
      action={
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          className="rw-radius-sm px-2.5 py-1 text-theme-sm font-medium rw-accent-ink transition rw-hover-accent"
        >
          {open ? t(locale, "editorial.hide") : t(locale, "editorial.show")}
        </button>
      }
    >
      {open ? (
        <CodeCopy text={body} filename={t(locale, "editorial.title")}>
          <Markdown>{body}</Markdown>
        </CodeCopy>
      ) : (
        <p className="text-theme-sm rw-faint">
          {state.access === "solved"
            ? t(locale, "editorial.solvedFree")
            : t(locale, "editorial.open")}{" "}
          {t(locale, "editorial.tryFirst")}
        </p>
      )}
    </Card>
  );
}
