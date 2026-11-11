"use client";

import { numericStamp } from "@rankwant/shared/format";
import type { Route } from "next";
import Link from "next/link";
import { useState } from "react";

import { useConfirm } from "@/components/overlay/OverlayHost";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { Verdict } from "@/components/ui/Verdict";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { postJson } from "@/lib/api";

import type { CoachStudent } from "../api";
import { failure } from "./failure";

/** The coach's panel: each student's progress, latest attempts and the
 *  problems recommended to them, with a form to recommend one more. */
export function MyStudents({ rows, onChange }: { rows: CoachStudent[]; onChange: () => void }) {
  const locale = useLocale();
  return (
    <Card title={t(locale, "coaching.students")} bodyClassName="p-0">
      <ul className="divide-y rw-divide">
        {rows.map((row) => (
          <StudentRow key={row.link} row={row} onChange={onChange} />
        ))}
      </ul>
    </Card>
  );
}

function StudentRow({ row, onChange }: { row: CoachStudent; onChange: () => void }) {
  const locale = useLocale();
  const confirm = useConfirm();
  const [problem, setProblem] = useState("");
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function recommend(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!problem.trim()) return;
    setBusy(true);
    setError("");
    try {
      await postJson(`/coaching/${row.link}/recommend/`, { problem: problem.trim(), note });
      setProblem("");
      setNote("");
      onChange();
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(false);
    }
  }

  async function end(origin: HTMLElement) {
    const question = fill(t(locale, "coaching.endStudentConfirm"), { user: row.username });
    const label = t(locale, "coaching.end");
    if (!(await confirm(question, { danger: true, kind: "popover", origin, confirmLabel: label })))
      return;
    try {
      await postJson(`/coaching/${row.link}/end/`, {});
      onChange();
    } catch (err) {
      setError(failure(locale, err));
    }
  }

  return (
    <li className="space-y-3 px-5 py-4">
      <div className="flex flex-wrap items-center gap-2">
        <Link href={`/users/${row.username}`} className="font-medium rw-strong rw-link-hover">
          {row.display_name || row.username}
        </Link>
        <span className="text-theme-xs rw-faint">
          {fill(t(locale, "coaching.stats"), {
            solved: row.solved_count,
            skills: row.rating_skills,
            streak: row.streak,
          })}
        </span>
        {!row.can_view_attempts && <Badge>{t(locale, "coaching.noConsent")}</Badge>}
      </div>

      {row.recent.length > 0 && (
        <ul className="space-y-1">
          {row.recent.map((attempt) => (
            <li key={attempt.id} className="flex flex-wrap items-center gap-2 text-theme-sm">
              <Verdict verdict={attempt.verdict} />
              <Link
                href={`/attempts/${attempt.id}` as Route}
                className="min-w-0 rw-link-hover"
              >
                {attempt.problem_title}
              </Link>
              <span className="text-theme-xs rw-faint">
                {attempt.language} · {numericStamp(attempt.created_at)}
              </span>
            </li>
          ))}
        </ul>
      )}

      {row.recommended.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {row.recommended.map((item) => (
            <Link
              key={item.problem}
              href={`/problems/${encodeURIComponent(item.problem)}`}
              className={`rounded border rw-line px-2 py-0.5 text-theme-xs rw-hover-line ${item.solved ? "rw-ok-ink" : ""}`}
            >
              {item.solved ? "✓ " : ""}
              {item.problem_title}
            </Link>
          ))}
        </div>
      )}

      <form onSubmit={recommend} className="grid gap-2 md:grid-cols-[1fr_2fr_auto] md:items-end">
        <Field
          name="problem"
          label={t(locale, "coaching.recommendProblem")}
          hint={t(locale, "coaching.recommendHint")}
          value={problem}
          onChange={(event) => setProblem(event.target.value)}
        />
        <Field
          name="note"
          label={t(locale, "coaching.note")}
          value={note}
          onChange={(event) => setNote(event.target.value)}
          maxLength={300}
        />
        <Button type="submit" busy={busy} disabled={!problem.trim()}>
          {t(locale, "coaching.recommend")}
        </Button>
      </form>
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <Button variant="outline" onClick={(event) => void end(event.currentTarget)}>
        {t(locale, "coaching.end")}
      </Button>
    </li>
  );
}
