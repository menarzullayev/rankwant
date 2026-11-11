"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { getJson } from "@/lib/api";

type Row = { username: string; solved: number; total: number };

/** How many of an assignment's problems each student has solved. The owner
 *  only: reports stay with the owner (decision 2026-11-10). */
export function AssignmentProgress({ slug, assignmentId }: { slug: string; assignmentId: number }) {
  const locale = useLocale();
  const [rows, setRows] = useState<Row[] | null>(null);

  useEffect(() => {
    getJson<{ results: Row[] }>(
      `/classrooms/${encodeURIComponent(slug)}/assignments/${assignmentId}/progress/`,
    )
      .then((data) => setRows(data.results))
      .catch(() => setRows([]));
  }, [slug, assignmentId]);

  if (rows === null) return null;

  return (
    <Table>
      <THead>
        <TH>{t(locale, "standings.user")}</TH>
        <TH align="right">{t(locale, "classroom.progress")}</TH>
      </THead>
      <TBody>
        {rows.map((row) => (
          <TR key={row.username}>
            <TD>
              <Link href={`/users/${row.username}`} className="font-medium rw-link-hover">
                {row.username}
              </Link>
            </TD>
            <TD align="right" className={row.solved === row.total ? "rw-ok-ink" : undefined}>
              {row.solved} / {row.total}
            </TD>
          </TR>
        ))}
        {rows.length === 0 && (
          <EmptyRow colSpan={2}>{t(locale, "classroom.course.noStudents")}</EmptyRow>
        )}
      </TBody>
    </Table>
  );
}
