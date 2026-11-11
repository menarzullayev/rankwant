"use client";

import { numericDate } from "@rankwant/shared/format";
import { SignInGate } from "@/components/auth/SignInGate";
import type { Route } from "next";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { useConfirm } from "@/components/overlay/OverlayHost";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import {
  getJson,
  postJson,
  type Assignment,
  type ClassroomDetail as Detail,
} from "@/lib/api";
import { isOn } from "@/lib/flags";

import { AssignmentProgress } from "./AssignmentProgress";
import { ClassCourseReport } from "./ClassCourseReport";
import { ClassQuizReport } from "./ClassQuizReport";
import { ClassroomSettings } from "./ClassroomSettings";
import { CourseAssignForm } from "./CourseAssignForm";
import { failure } from "./failure";
import { JoinRequests } from "./JoinRequests";
import { MembersCard } from "./MembersCard";
import { ProblemAssignForm } from "./ProblemAssignForm";
import { QuizAssignForm } from "./QuizAssignForm";
import { RoleBadge } from "./RoleBadge";

const ACCESS_KEYS: Record<string, string> = {
  free: "course.access.free",
  qvant: "course.access.qvant",
  paid: "course.access.paid",
};

export function ClassroomDetail({ slug }: { slug: string }) {
  const locale = useLocale();
  const router = useRouter();
  const confirm = useConfirm();
  const { user, ready } = useSession();
  const [room, setRoom] = useState<Detail | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [missing, setMissing] = useState(false);
  const [open, setOpen] = useState<string | null>(null);
  const [error, setError] = useState("");

  const loadRoom = useCallback(() => {
    void getJson<Detail>(`/classrooms/${slug}/`)
      .then(setRoom)
      .catch(() => setMissing(true));
  }, [slug]);

  useEffect(() => {
    if (!user) return;
    loadRoom();
    getJson<Assignment[]>(`/classrooms/${slug}/assignments/`)
      .then(setAssignments)
      .catch(() => {});
  }, [user, slug, loadRoom]);

  if (ready && !user) return <SignInGate reason="classroom" />;
  if (missing)
    return (
      <Card>
        <p className="text-theme-sm rw-faint">404</p>
      </Card>
    );
  if (!room) return null;
  const owner = room.my_role === "owner";
  const manager = owner || room.my_role === "assistant";
  const coursesOpen = isOn("courses") || Boolean(user?.is_staff);
  const toggle = (key: string) => setOpen(open === key ? null : key);
  const added = (created: Assignment) => setAssignments((rows) => [created, ...rows]);

  async function leave(origin: HTMLElement) {
    if (!(await confirm(t(locale, "classroom.leaveConfirm"), {
        danger: true,
        kind: "popover",
        origin,
        confirmLabel: t(locale, "classroom.leave"),
      })))
      return;
    try {
      await postJson(`/classrooms/${encodeURIComponent(slug)}/leave/`, {});
      router.push("/classroom");
    } catch (err) {
      setError(failure(locale, err));
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{room.name}</h1>
        {room.description && <p className="mt-1 text-theme-sm rw-dim">{room.description}</p>}
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Badge>@{room.owner}</Badge>
          <Badge>{fill(t(locale, "classroom.students"), { count: room.member_count })}</Badge>
          <RoleBadge role={room.my_role} />
        </div>
      </header>

      {owner && <ClassroomSettings room={room} onChange={setRoom} />}

      {manager && (room.join_mode === "approval" || (room.pending_count ?? 0) > 0) && (
        <JoinRequests slug={slug} onDecided={loadRoom} />
      )}

      <Card title={t(locale, "classroom.assignments")} bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {assignments.map((a) => (
            <li key={a.id} className="px-5 py-3">
              {/* A course given under its own name needs no second title. */}
              {a.title !== a.course?.title && <p className="font-medium rw-strong">{a.title}</p>}
              {a.description && <p className="text-theme-sm rw-dim">{a.description}</p>}
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
              {a.quiz && (
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <Link
                    href={`/quizzes/${encodeURIComponent(a.quiz.slug)}` as Route}
                    className="font-medium rw-accent-ink hover:underline"
                  >
                    {a.quiz.title}
                  </Link>
                  {a.quiz.time_limit_minutes !== null && (
                    <Badge>
                      {fill(t(locale, "quiz.timeLimit"), { minutes: a.quiz.time_limit_minutes })}
                    </Badge>
                  )}
                  {a.quiz.one_attempt && <Badge>{t(locale, "quiz.oneAttempt")}</Badge>}
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
                  <span className="text-theme-xs rw-faint">→ {numericDate(a.due_at)}</span>
                )}
              </div>
              {owner && (a.course || a.quiz || a.problems.length > 0) && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {a.problems.length > 0 && (
                    <Button
                      variant="outline"
                      aria-expanded={open === `p${a.id}`}
                      aria-controls={`class-problems-${a.id}`}
                      onClick={() => toggle(`p${a.id}`)}
                    >
                      {t(locale, "classroom.progress")}
                    </Button>
                  )}
                  {a.quiz && (
                    <Button
                      variant="outline"
                      aria-expanded={open === `q${a.id}`}
                      aria-controls={`class-quiz-${a.id}`}
                      onClick={() => toggle(`q${a.id}`)}
                    >
                      {t(locale, "classroom.quiz.results")}
                    </Button>
                  )}
                  {a.course && (
                    <Button
                      variant="outline"
                      aria-expanded={open === `c${a.id}`}
                      aria-controls={`class-course-${a.id}`}
                      onClick={() => toggle(`c${a.id}`)}
                    >
                      {t(locale, "classroom.course.progress")}
                    </Button>
                  )}
                </div>
              )}
              {open === `p${a.id}` && (
                <div id={`class-problems-${a.id}`} className="mt-3">
                  <AssignmentProgress slug={slug} assignmentId={a.id} />
                </div>
              )}
              {open === `q${a.id}` && (
                <div id={`class-quiz-${a.id}`} className="mt-3">
                  <ClassQuizReport slug={slug} assignmentId={a.id} />
                </div>
              )}
              {open === `c${a.id}` && (
                <div id={`class-course-${a.id}`} className="mt-3">
                  <ClassCourseReport slug={slug} assignmentId={a.id} />
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

      {owner && (
        <Card title={t(locale, "classroom.problems.give")}>
          <ProblemAssignForm slug={slug} onCreated={added} />
        </Card>
      )}

      {owner && (
        <Card title={t(locale, "classroom.quiz.give")}>
          <QuizAssignForm slug={slug} onCreated={added} />
        </Card>
      )}

      {owner && coursesOpen && (
        <Card title={t(locale, "classroom.course.give")}>
          <CourseAssignForm slug={slug} onCreated={added} />
        </Card>
      )}

      {room.members && (
        <MembersCard slug={slug} members={room.members} owner={owner} onChange={loadRoom} />
      )}

      {!owner && room.my_role && (
        <div className="space-y-2">
          {error && (
            <p role="alert" className="text-theme-sm rw-bad-ink">
              {error}
            </p>
          )}
          <Button variant="outline" onClick={(e) => void leave(e.currentTarget)}>
            {t(locale, "classroom.leave")}
          </Button>
        </div>
      )}
    </div>
  );
}
