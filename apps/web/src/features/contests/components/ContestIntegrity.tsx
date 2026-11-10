"use client";

import type { Route } from "next";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { numericStamp } from "@rankwant/shared/format";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t } from "@/i18n/messages";
import {
  ApiError,
  getJson,
  postJson,
  type IntegrityReport,
  type IntegrityRow,
} from "@/lib/api";

const TEXTAREA =
  "w-full rw-radius-sm border rw-line rw-field-bg p-2.5 text-theme-sm rw-strong outline-none rw-focus-line rw-fm-inp";

function Disqualify({
  slug,
  username,
  onDone,
}: {
  slug: string;
  username: string;
  onDone: () => void;
}) {
  const locale = useLocale();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send() {
    setBusy(true);
    setError(null);
    try {
      await postJson(`/contests/${slug}/disqualify/`, { username, reason });
      setOpen(false);
      onDone();
    } catch (e) {
      setError(e instanceof ApiError ? errorText(locale, e.code, e.message) : String(e));
    } finally {
      setBusy(false);
    }
  }

  if (!open) {
    return (
      <Button variant="outline" onClick={() => setOpen(true)}>
        {t(locale, "contest.fair.dq")}
      </Button>
    );
  }
  return (
    <div className="mt-2 space-y-2" data-dq-form="">
      <p className="text-theme-xs rw-dim">{fill(t(locale, "contest.fair.dqWhat"), { user: username })}</p>
      <textarea
        value={reason}
        onChange={(event) => setReason(event.target.value)}
        rows={2}
        maxLength={2000}
        aria-label={t(locale, "contest.fair.reason")}
        placeholder={t(locale, "contest.fair.reason")}
        className={TEXTAREA}
      />
      <div className="flex flex-wrap gap-2">
        <Button busy={busy} disabled={!reason.trim()} onClick={send}>
          {t(locale, "contest.fair.dqConfirm")}
        </Button>
        <Button variant="outline" onClick={() => setOpen(false)}>
          {t(locale, "contest.fair.cancel")}
        </Button>
      </div>
      {error && (
        <p className="text-theme-sm rw-bad-ink" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

function Signals({ row }: { row: IntegrityRow }) {
  const locale = useLocale();
  const minutes = Math.round(row.active_ms / 60_000);
  return (
    <p className="text-theme-xs rw-dim">
      {fill(t(locale, "contest.fair.signals"), {
        source: row.source_chars,
        pasted: row.pasted_chars,
        largest: row.largest_paste,
        blurs: row.blur_count,
        minutes,
      })}
    </p>
  );
}

/** «Halol o'yin» — for the jury once the contest is over (ADR-0055, part 4).
 *
 *  The attempts whose editor signals stand out, each with a link to the
 *  code and a disqualify button. Nothing here decides by itself.
 */
export function ContestIntegrity({ slug }: { slug: string }) {
  const locale = useLocale();
  const [data, setData] = useState<IntegrityReport | null>(null);

  const reload = useCallback(() => {
    getJson<IntegrityReport>(`/contests/${slug}/integrity/`)
      .then(setData)
      .catch(() => setData(null));
  }, [slug]);

  useEffect(() => {
    reload();
  }, [reload]);

  if (data === null) return null;
  const out = new Set(data.disqualified.map((row) => row.username));
  return (
    <section aria-label={t(locale, "contest.fair.title")} data-fair-report="">
      <Card title={t(locale, "contest.fair.title")}>
        <p className="mb-3 text-theme-xs rw-dim">{t(locale, "contest.fair.intro")}</p>
        {data.results.length === 0 ? (
          <p className="text-theme-sm rw-dim">{t(locale, "contest.fair.clean")}</p>
        ) : (
          <ul className="rw-divide divide-y">
            {data.results.map((row) => (
              <li key={row.attempt} className="space-y-1 py-3 text-theme-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-semibold rw-strong">{row.username}</span>
                  <span className="rw-chip rw-radius-sm px-1.5 text-theme-xs">{row.problem}</span>
                  {row.flags.map((flag) => (
                    <span key={flag} className="rw-warn-soft rw-warn-ink rounded-full px-2 text-theme-xs">
                      {t(locale, `contest.fair.flag.${flag}`)}
                    </span>
                  ))}
                  <Link
                    href={`/attempts/${row.attempt}` as Route}
                    className="text-theme-xs rw-accent-ink underline"
                  >
                    {fill(t(locale, "contest.fair.attempt"), { id: row.attempt })}
                  </Link>
                  <time className="text-theme-xs rw-dim" dateTime={row.created_at}>
                    {numericStamp(row.created_at)}
                  </time>
                </div>
                <Signals row={row} />
                {out.has(row.username) ? (
                  <p className="text-theme-xs font-semibold rw-bad-ink">{t(locale, "standings.dq")}</p>
                ) : (
                  <Disqualify slug={slug} username={row.username} onDone={reload} />
                )}
              </li>
            ))}
          </ul>
        )}
        {data.disqualified.length > 0 && (
          <div className="mt-4" data-dq-list="">
            <h3 className="mb-1 text-theme-sm font-semibold rw-strong">
              {t(locale, "contest.fair.disqualified")}
            </h3>
            <ul className="space-y-1 text-theme-sm">
              {data.disqualified.map((row) => (
                <li key={row.username}>
                  <strong>{row.username}</strong> — {row.reason}
                </li>
              ))}
            </ul>
          </div>
        )}
      </Card>
    </section>
  );
}
