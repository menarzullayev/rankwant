"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { GuestPrompt } from "@/components/auth/SignInPopover";
import { Button } from "@/components/ui/Button";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import { REPORT_REASONS, deleteEntry, reportEntry, voteEntry, type EntryDetail } from "../api";

const ACTION =
  "inline-flex min-h-9 items-center rw-radius-sm px-2 text-theme-sm font-medium rw-dim rw-hover-bg rw-focus-ring";

function scoreClass(score: number): string {
  if (score > 0) return "rw-ok-ink";
  if (score < 0) return "rw-bad-ink";
  return "rw-faint";
}

type Mode = "" | "report" | "delete";

/** Vote, report, edit and delete under an entry (decisions ⑤⑥). */
export function EntryActions({ entry, signedIn }: { entry: EntryDetail; signedIn: boolean }) {
  const locale = useLocale();
  const router = useRouter();
  const [score, setScore] = useState(entry.score);
  const [mine, setMine] = useState(entry.my_vote);
  const [mode, setMode] = useState<Mode>("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const flip = (next: Mode) => setMode((current) => (current === next ? "" : next));

  async function run(work: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await work();
    } catch (caught) {
      setError(caught instanceof ApiError ? errorText(locale, caught.code, caught.message) : String(caught));
    } finally {
      setBusy(false);
    }
  }

  const vote = (value: -1 | 1) =>
    run(async () => {
      const res = await voteEntry(entry.id, mine === value ? 0 : value);
      setScore(res.score);
      setMine(res.my_vote);
    });

  const voteButton = (value: -1 | 1) => {
    const label = t(locale, value > 0 ? "discussion.voteUp" : "discussion.voteDown");
    const glyph = value > 0 ? "▲" : "▼";
    if (!signedIn)
      return (
        <GuestPrompt
          reason="vote"
          trigger={(props) => (
            <button {...props} aria-label={label} className={ACTION}>
              {glyph}
            </button>
          )}
        />
      );
    return (
      <button
        type="button"
        aria-label={label}
        aria-pressed={mine === value}
        disabled={busy || entry.mine}
        onClick={() => void vote(value)}
        className={`${ACTION} ${mine === value ? "rw-accent-ink" : ""}`}
      >
        {glyph}
      </button>
    );
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-1">
        {voteButton(1)}
        <span className={`min-w-8 text-center font-bold tabular-nums ${scoreClass(score)}`}>
          {score > 0 ? `+${score}` : score}
        </span>
        {voteButton(-1)}
        {entry.mine ? (
          <>
            <Link href={`/blogs/${entry.id}/edit` as Route} className={ACTION}>
              {t(locale, "discussion.edit")}
            </Link>
            <button type="button" className={ACTION} onClick={() => flip("delete")}>
              {t(locale, "discussion.delete")}
            </button>
          </>
        ) : signedIn ? (
          <button type="button" className={ACTION} onClick={() => flip("report")}>
            {t(locale, "discussion.report")}
          </button>
        ) : (
          <GuestPrompt
            reason="report"
            trigger={(props) => (
              <button {...props} className={ACTION}>
                {t(locale, "discussion.report")}
              </button>
            )}
          />
        )}
        {note && <span className="text-theme-xs rw-ok-ink">{note}</span>}
      </div>

      {mode === "delete" && (
        <div className="flex flex-wrap items-center gap-2 text-theme-sm rw-dim">
          <span>{t(locale, "blogs.deleteConfirm")}</span>
          <Button
            variant="outline"
            busy={busy}
            onClick={() =>
              void run(async () => {
                await deleteEntry(entry.id);
                router.push("/blogs" as Route);
                router.refresh();
              })
            }
          >
            {t(locale, "discussion.delete")}
          </Button>
          <Button variant="outline" onClick={() => setMode("")}>
            {t(locale, "discussion.cancel")}
          </Button>
        </div>
      )}

      {mode === "report" && (
        <fieldset className="flex flex-wrap items-center gap-2 text-theme-xs">
          <legend className="sr-only">{t(locale, "discussion.reportTitle")}</legend>
          <span className="rw-dim">{t(locale, "discussion.reportTitle")}</span>
          {REPORT_REASONS.map((reason) => (
            <Button
              key={reason}
              variant="outline"
              busy={busy}
              onClick={() =>
                void run(async () => {
                  await reportEntry(entry.id, reason);
                  setMode("");
                  setNote(t(locale, "discussion.reported"));
                })
              }
            >
              {t(locale, `discussion.reason.${reason}`)}
            </Button>
          ))}
        </fieldset>
      )}

      {error && (
        <p role="alert" className="text-theme-xs rw-bad-ink">
          {error}
        </p>
      )}
    </div>
  );
}
