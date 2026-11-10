"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t } from "@/i18n/messages";
import { ApiError, getJson, postJson, type Assignment } from "@/lib/api";
import type { components } from "@/lib/api/generated/schema";

type CourseCard = components["schemas"]["CourseCard"];

const ACCESS_KEYS: Record<string, string> = {
  free: "course.access.free",
  qvant: "course.access.qvant",
  paid: "course.access.paid",
};

/** The teacher gives a published course to the class. A free course enrols
 *  every student; a Qvant or paid one is unlocked by each student (owner
 *  decision 2026-11-10), and the form says so before it is given. */
export function CourseAssignForm({
  slug,
  onCreated,
}: {
  slug: string;
  onCreated: (assignment: Assignment) => void;
}) {
  const locale = useLocale();
  const [courses, setCourses] = useState<CourseCard[] | null>(null);
  const [course, setCourse] = useState("");
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getJson<{ results: CourseCard[] }>("/courses/?page_size=100")
      .then((page) => setCourses(page.results))
      .catch(() => setCourses([]));
  }, []);

  const picked = courses?.find((c) => c.slug === course);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!picked) return;
    setBusy(true);
    setError("");
    try {
      const created = await postJson<Assignment>(`/classrooms/${encodeURIComponent(slug)}/assignments/`, {
        title: title.trim() || picked.title,
        course: picked.slug,
        due_at: due ? new Date(due).toISOString() : null,
      });
      onCreated(created);
      setCourse("");
      setTitle("");
      setDue("");
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code, err.message) : String(err));
    } finally {
      setBusy(false);
    }
  }

  if (courses === null) return null;
  if (courses.length === 0) {
    return <p className="text-theme-sm rw-faint">{t(locale, "classroom.course.none")}</p>;
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <SelectField
          name="course"
          label={t(locale, "classroom.course.pick")}
          placeholder={t(locale, "classroom.course.pickPlaceholder")}
          options={courses.map((c) => ({
            value: c.slug,
            label: [c.title, t(locale, ACCESS_KEYS[c.access] ?? "course.access.free")].join(" · "),
          }))}
          value={course}
          onChange={(value) => {
            setCourse(value);
            const next = courses.find((c) => c.slug === value);
            if (next && !title.trim()) setTitle(next.title);
          }}
        />
        <Field
          name="title"
          label={t(locale, "classroom.course.name")}
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          maxLength={200}
        />
        <Field
          name="due_at"
          type="datetime-local"
          label={t(locale, "classroom.course.due")}
          value={due}
          onChange={(event) => setDue(event.target.value)}
        />
      </div>
      {picked && (
        <p className="text-theme-sm rw-dim">
          {t(locale, picked.access === "free" ? "classroom.course.freeNote" : "classroom.course.pricedNote")}
        </p>
      )}
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <Button type="submit" busy={busy} disabled={!picked}>
        {t(locale, "classroom.course.submit")}
      </Button>
    </form>
  );
}
