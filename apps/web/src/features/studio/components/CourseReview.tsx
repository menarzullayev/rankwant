"use client";

import type { Route } from "next";
import Link from "next/link";
import { useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t, type MessageKey } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import { courseStatus, staffCourses, textOf, type StaffCourse } from "../api/courses";

const ACCESS = ["free", "qvant", "paid"] as const;
type Access = (typeof ACCESS)[number];

const STATUS_KEY: Record<string, MessageKey> = {
  draft: "studio.status.draft",
  review: "studio.status.review",
  published: "studio.status.public",
};

function failure(locale: ReturnType<typeof useLocale>, error: unknown): string {
  if (!(error instanceof ApiError)) return String(error);
  const first = error.details ? Object.values(error.details)[0] : undefined;
  if (Array.isArray(first) && typeof first[0] === "string") return `${errorText(locale, error.code)} ${first[0]}`;
  return errorText(locale, error.code);
}

function Row({ initial }: { initial: StaffCourse }) {
  const locale = useLocale();
  const [course, setCourse] = useState(initial);
  const [access, setAccess] = useState<Access>((course.access as Access) ?? "free");
  const [qvant, setQvant] = useState(String(course.price_qvant ?? 0));
  const [uzs, setUzs] = useState(String(course.price_uzs ?? 0));
  const [reward, setReward] = useState(String(course.reward_qvant ?? 0));
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const title = textOf(course.texts, course.base_locale ?? "uz")?.title || course.slug;
  const status = courseStatus(course);

  async function act(name: string, write: () => Promise<StaffCourse>, done: MessageKey) {
    setBusy(name);
    setError("");
    setNote("");
    try {
      setCourse(await write());
      setNote(t(locale, done));
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy("");
    }
  }

  return (
    <li className="space-y-4 rw-radius border rw-line rw-surface p-5">
      <div className="flex flex-wrap items-center gap-2">
        <h2 className="text-theme-base font-semibold rw-strong">{title}</h2>
        <Badge color={status === "published" ? "success" : status === "review" ? "warning" : "neutral"}>
          {t(locale, STATUS_KEY[status] ?? "studio.status.draft")}
        </Badge>
      </div>
      <p className="text-theme-xs rw-dim">
        {fill(t(locale, "admin.courses.authors"), { names: course.authors.join(", ") || "—" })}
      </p>
      <Link
        href={`/studio/courses/${encodeURIComponent(course.slug)}` as Route}
        className="inline-flex min-h-11 items-center text-theme-sm rw-accent-ink rw-focus-ring"
      >
        {t(locale, "admin.courses.openStudio")}
      </Link>

      <form
        className="grid gap-3 sm:grid-cols-4"
        onSubmit={(event) => {
          event.preventDefault();
          void act(
            "price",
            () =>
              staffCourses.update(course.slug, {
                access,
                price_qvant: Number(qvant) || 0,
                price_uzs: Number(uzs) || 0,
                reward_qvant: Number(reward) || 0,
              }),
            "admin.courses.saved",
          );
        }}
      >
        <SelectField
          name={`access-${course.slug}`}
          label={t(locale, "course.filter.access")}
          options={ACCESS.map((value) => ({ value, label: t(locale, `course.access.${value}` as MessageKey) }))}
          value={access}
          onChange={(value) => setAccess(value as Access)}
        />
        <Field name={`qvant-${course.slug}`} type="number" min={0} label={t(locale, "admin.courses.priceQvant")} value={qvant} onChange={(e) => setQvant(e.target.value)} />
        <Field name={`uzs-${course.slug}`} type="number" min={0} label={t(locale, "admin.courses.priceUzs")} value={uzs} onChange={(e) => setUzs(e.target.value)} />
        <Field name={`reward-${course.slug}`} type="number" min={0} label={t(locale, "admin.courses.reward")} value={reward} onChange={(e) => setReward(e.target.value)} />
        <div className="sm:col-span-4">
          <Button type="submit" variant="outline" busy={busy === "price"}>
            {t(locale, "admin.courses.savePrice")}
          </Button>
        </div>
      </form>

      {status !== "published" && (
        <div className="space-y-3 border-t rw-divider pt-4">
          {course.gaps.length > 0 && (
            <p className="text-theme-sm rw-bad-ink">
              {t(locale, "admin.courses.gaps")}{" "}
              {course.gaps.map((gap) => t(locale, `studio.course.gap.${gap}` as MessageKey)).join("; ")}
            </p>
          )}
          <Button
            type="button"
            busy={busy === "publish"}
            disabled={course.gaps.length > 0}
            onClick={() => void act("publish", () => staffCourses.publish(course.slug), "admin.courses.publishedNote")}
          >
            {t(locale, "admin.courses.publish")}
          </Button>
          <label className="block">
            <span className="mb-1 block text-theme-sm font-medium rw-strong">{t(locale, "admin.courses.reason")}</span>
            <textarea
              value={reason}
              rows={3}
              maxLength={1000}
              onChange={(event) => setReason(event.target.value)}
              className="w-full rw-radius-sm border rw-line rw-field-bg p-2.5 text-theme-sm rw-strong outline-none rw-focus-line"
            />
          </label>
          <Button
            type="button"
            variant="outline"
            busy={busy === "back"}
            disabled={!reason.trim() || !course.review_requested_at}
            onClick={() =>
              void act("back", () => staffCourses.sendBack(course.slug, reason.trim()), "admin.courses.sentBack")
            }
          >
            {t(locale, "admin.courses.sendBack")}
          </Button>
        </div>
      )}
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      {note && (
        <p role="status" className="text-theme-sm rw-ok-ink">
          {note}
        </p>
      )}
    </li>
  );
}

/** Staff-content: the review queue first, every course on demand. */
export function CourseReview({ rows, queue }: { rows: StaffCourse[]; queue: boolean }) {
  const locale = useLocale();
  return (
    <div className="space-y-5">
      <header className="space-y-2">
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "admin.section.courses")}</h1>
        <p className="text-theme-sm rw-dim">{t(locale, "admin.courses.intro")}</p>
        <nav className="flex flex-wrap gap-2">
          {[
            { href: "/admin/courses?review=1", active: queue, key: "admin.courses.queue" as MessageKey },
            { href: "/admin/courses", active: !queue, key: "admin.courses.all" as MessageKey },
          ].map((tab) => (
            <Link
              key={tab.href}
              href={tab.href as Route}
              aria-current={tab.active ? "page" : undefined}
              className={`inline-flex min-h-11 items-center rounded-full border px-4 text-theme-sm rw-focus-ring ${
                tab.active ? "rw-accent-soft rw-accent-ink border-[var(--rw-accent)]" : "rw-line rw-dim rw-hover-bg"
              }`}
            >
              {t(locale, tab.key)}
            </Link>
          ))}
        </nav>
      </header>
      {rows.length === 0 ? (
        <p className="text-theme-sm rw-faint">{t(locale, queue ? "admin.courses.queueEmpty" : "course.empty")}</p>
      ) : (
        <ul className="space-y-4">
          {rows.map((row) => (
            <Row key={row.slug} initial={row} />
          ))}
        </ul>
      )}
    </div>
  );
}
