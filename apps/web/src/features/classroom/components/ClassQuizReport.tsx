"use client";

import { numericStamp } from "@rankwant/shared/format";
import Link from "next/link";
import { useEffect, useState } from "react";

import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { getJson } from "@/lib/api";

type Report = {
  quiz: string;
  title: string;
  students: {
    username: string;
    attempts: number;
    score: number | null;
    total: number;
    finished_at: string | null;
  }[];
  questions: { id: number; order: number; text: string; wrong: number; answered: number }[];
};

/** A class quiz's results: each student's best attempt, and the questions
 *  most of them got wrong. The owner only (decision 2026-11-10). */
export function ClassQuizReport({ slug, assignmentId }: { slug: string; assignmentId: number }) {
  const locale = useLocale();
  const [report, setReport] = useState<Report | null>(null);

  useEffect(() => {
    getJson<Report>(`/classrooms/${encodeURIComponent(slug)}/assignments/${assignmentId}/quiz/`)
      .then(setReport)
      .catch(() => {});
  }, [slug, assignmentId]);

  if (!report) return null;
  const hardest = [...report.questions].sort((a, b) => b.wrong - a.wrong);

  return (
    <div className="space-y-4">
      <Table>
        <THead>
          <TH>{t(locale, "standings.user")}</TH>
          <TH align="right">{t(locale, "quiz.result")}</TH>
          <TH align="right">{t(locale, "classroom.quiz.attempts")}</TH>
        </THead>
        <TBody>
          {report.students.map((row) => (
            <TR key={row.username}>
              <TD>
                <Link href={`/users/${row.username}`} className="font-medium rw-link-hover">
                  {row.username}
                </Link>
                {row.finished_at && (
                  <span className="ml-2 text-theme-xs rw-faint">{numericStamp(row.finished_at)}</span>
                )}
              </TD>
              <TD align="right" className="tabular-nums">
                {row.score === null ? (
                  <span className="rw-faint">{t(locale, "classroom.quiz.notTaken")}</span>
                ) : (
                  `${row.score} / ${row.total}`
                )}
              </TD>
              <TD align="right" className="tabular-nums">
                {row.attempts}
              </TD>
            </TR>
          ))}
          {report.students.length === 0 && (
            <EmptyRow colSpan={3}>{t(locale, "classroom.course.noStudents")}</EmptyRow>
          )}
        </TBody>
      </Table>
      {hardest.length > 0 && (
        <div>
          <p className="mb-2 text-theme-sm font-medium rw-strong">{t(locale, "classroom.quiz.questions")}</p>
          <ul className="space-y-1">
            {hardest.map((row) => (
              <li key={row.id} className="flex items-center gap-3 text-theme-sm">
                <span className="w-6 tabular-nums rw-faint">{row.order}.</span>
                <span className="min-w-0 flex-1 truncate rw-dim">{row.text}</span>
                <span className={`tabular-nums ${row.wrong > 0 ? "rw-bad-ink" : "rw-ok-ink"}`}>
                  {fill(t(locale, "classroom.quiz.wrong"), {
                    wrong: row.wrong,
                    answered: row.answered,
                  })}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
