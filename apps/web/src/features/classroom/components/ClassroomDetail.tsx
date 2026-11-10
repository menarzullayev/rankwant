"use client";

import { numericDate } from "@rankwant/shared/format";
import { SignInGate } from "@/components/auth/SignInGate";
import type { Route } from "next";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import {
  EmptyRow,
  TBody,
  TD,
  TH,
  THead,
  TR,
  Table,
} from "@/components/ui/Table";
import { useSession } from "@/context/SessionContext";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import {
  getJson,
  type Assignment,
  type ClassroomDetail as Detail,
} from "@/lib/api";
import { isOn } from "@/lib/flags";

import { ClassCourseReport } from "./ClassCourseReport";
import { CourseAssignForm } from "./CourseAssignForm";

const ACCESS_KEYS: Record<string, string> = {
  free: "course.access.free",
  qvant: "course.access.qvant",
  paid: "course.access.paid",
};

export function ClassroomDetail({ slug }: { slug: string }) {
  const locale = useLocale();
  const { user, ready } = useSession();
  const [room, setRoom] = useState<Detail | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [missing, setMissing] = useState(false);
  const [open, setOpen] = useState<number | null>(null);

  useEffect(() => {
    if (!user) return;
    getJson<Detail>(`/classrooms/${slug}/`)
      .then(setRoom)
      .catch(() => setMissing(true));
    getJson<Assignment[]>(`/classrooms/${slug}/assignments/`)
      .then(setAssignments)
      .catch(() => {});
  }, [user, slug]);

  if (ready && !user)
    return <SignInGate reason="classroom" />;
  if (missing)
    return (
      <Card>
        <p className="text-theme-sm rw-faint">404</p>
      </Card>
    );
  if (!room) return null;
  // The owner's view carries the join code (ClassroomOwnerSerializer).
  const owner = Boolean(room.join_code);
  const coursesOpen = isOn("courses") || Boolean(user?.is_staff);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{room.name}</h1>
        <p className="mt-1 text-theme-sm rw-dim">{room.description}</p>
        <div className="mt-2 flex flex-wrap gap-2">
          <Badge>@{room.owner}</Badge>
          <Badge>
            {room.member_count} {t(locale, "classroom.members").toLowerCase()}
          </Badge>
          {room.join_code && (
            <Badge color="brand">
              {t(locale, "classroom.code")}: {room.join_code}
            </Badge>
          )}
        </div>
      </header>

      <Card title={t(locale, "classroom.assignments")} bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {assignments.map((a) => (
            <li key={a.id} className="px-5 py-3">
              {/* A course given under its own name needs no second title. */}
              {a.title !== a.course?.title && (
                <p className="font-medium rw-strong">{a.title}</p>
              )}
              {a.description && (
                <p className="text-theme-sm rw-dim">{a.description}</p>
              )}
              {a.course && (
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <Link
                    href={`/courses/${encodeURIComponent(a.course.slug)}` as Route}
                    className="font-medium rw-accent-ink hover:underline"
                  >
                    {inReaderAlphabet(a.course.title, a.course.locale)}
                  </Link>
                  <Badge>{t(locale, ACCESS_KEYS[a.course.access] ?? "course.access.free")}</Badge>
                  {a.course.access !== "free" && (
                    <span className="text-theme-xs rw-dim">
                      {t(locale, "classroom.course.pricedNote")}
                    </span>
                  )}
                </div>
              )}
              <div className="mt-2 flex flex-wrap gap-2">
                {a.problems.map((p) => (
                  <Link
                    key={p}
                    href={`/problems/${p}`}
                    className="rounded border rw-line px-2 py-0.5 text-theme-xs rw-hover-line"
                  >
                    {p}
                  </Link>
                ))}
                {a.due_at && (
                  <span className="text-theme-xs rw-faint">
                    → {numericDate(a.due_at)}
                  </span>
                )}
              </div>
              {owner && a.course && (
                <div className="mt-3 space-y-3">
                  <Button
                    variant="outline"
                    aria-expanded={open === a.id}
                    aria-controls={`class-course-${a.id}`}
                    onClick={() => setOpen(open === a.id ? null : a.id)}
                  >
                    {t(locale, "classroom.course.progress")}
                  </Button>
                  {open === a.id && (
                    <div id={`class-course-${a.id}`}>
                      <ClassCourseReport slug={slug} assignmentId={a.id} />
                    </div>
                  )}
                </div>
              )}
            </li>
          ))}
          {assignments.length === 0 && (
            <li className="px-5 py-6 text-center text-theme-sm rw-faint">
              {t(locale, "common.empty")}
            </li>
          )}
        </ul>
      </Card>

      {owner && coursesOpen && (
        <Card title={t(locale, "classroom.course.give")}>
          <CourseAssignForm
            slug={slug}
            onCreated={(created) => setAssignments((rows) => [created, ...rows])}
          />
        </Card>
      )}

      {room.members && (
        <Card title={t(locale, "classroom.members")} bodyClassName="p-0">
          <Table>
            <THead>
              <TH>{t(locale, "standings.user")}</TH>
              <TH>{t(locale, "col.role")}</TH>
              <TH align="right">Skills</TH>
            </THead>
            <TBody>
              {room.members.map((m) => (
                <TR key={m.username}>
                  <TD>
                    <Link
                      href={`/users/${m.username}`}
                      className="font-medium rw-link-hover"
                    >
                      {m.username}
                    </Link>
                  </TD>
                  <TD className="rw-faint">{m.role}</TD>
                  <TD align="right">{m.rating_skills}</TD>
                </TR>
              ))}
              {room.members.length === 0 && (
                <EmptyRow colSpan={3}>{t(locale, "common.empty")}</EmptyRow>
              )}
            </TBody>
          </Table>
        </Card>
      )}
    </div>
  );
}
