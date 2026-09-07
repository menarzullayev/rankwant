"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { EmptyRow, TBody, TD, TH, THead, TR, Table } from "@/components/ui/Table";
import { useSession } from "@/context/SessionContext";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { getJson, type Assignment, type ClassroomDetail as Detail } from "@/lib/api";

export function ClassroomDetail({ slug }: { slug: string }) {
  const locale = DEFAULT_LOCALE;
  const { user, ready } = useSession();
  const [room, setRoom] = useState<Detail | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    if (!user) return;
    getJson<Detail>(`/classrooms/${slug}/`).then(setRoom).catch(() => setMissing(true));
    getJson<Assignment[]>(`/classrooms/${slug}/assignments/`).then(setAssignments).catch(() => {});
  }, [user, slug]);

  if (ready && !user) return <Card><p className="text-theme-sm text-gray-400">{t(locale, "auth.login")} →</p></Card>;
  if (missing) return <Card><p className="text-theme-sm text-gray-400">404</p></Card>;
  if (!room) return null;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">{room.name}</h1>
        <p className="mt-1 text-theme-sm text-gray-500 dark:text-gray-400">{room.description}</p>
        <div className="mt-2 flex flex-wrap gap-2">
          <Badge>@{room.owner}</Badge>
          <Badge>{room.member_count} {t(locale, "classroom.members").toLowerCase()}</Badge>
          {room.join_code && <Badge color="brand">{t(locale, "classroom.code")}: {room.join_code}</Badge>}
        </div>
      </header>

      <Card title={t(locale, "classroom.assignments")} bodyClassName="p-0">
        <ul className="divide-y divide-gray-100 dark:divide-[#232936]">
          {assignments.map((a) => (
            <li key={a.id} className="px-5 py-3">
              <p className="font-medium text-gray-800 dark:text-white/90">{a.title}</p>
              {a.description && <p className="text-theme-sm text-gray-500">{a.description}</p>}
              <div className="mt-2 flex flex-wrap gap-2">
                {a.problems.map((p) => (
                  <Link key={p} href={`/problems/${p}`} className="rounded border border-gray-200 px-2 py-0.5 text-theme-xs hover:border-brand-400 dark:border-[#232936]">{p}</Link>
                ))}
                {a.due_at && <span className="text-theme-xs text-gray-400">→ {new Date(a.due_at).toLocaleDateString(locale)}</span>}
              </div>
            </li>
          ))}
          {assignments.length === 0 && <li className="px-5 py-6 text-center text-theme-sm text-gray-400">{t(locale, "empty")}</li>}
        </ul>
      </Card>

      {room.members && (
        <Card title={t(locale, "classroom.members")} bodyClassName="p-0">
          <Table>
            <THead><TH>{t(locale, "standings.user")}</TH><TH>Rol</TH><TH align="right">Skills</TH></THead>
            <TBody>
              {room.members.map((m) => (
                <TR key={m.username}>
                  <TD><Link href={`/users/${m.username}`} className="font-medium hover:text-brand-500">{m.username}</Link></TD>
                  <TD className="text-gray-400">{m.role}</TD>
                  <TD align="right">{m.rating_skills}</TD>
                </TR>
              ))}
              {room.members.length === 0 && <EmptyRow colSpan={3}>{t(locale, "empty")}</EmptyRow>}
            </TBody>
          </Table>
        </Card>
      )}
    </div>
  );
}
