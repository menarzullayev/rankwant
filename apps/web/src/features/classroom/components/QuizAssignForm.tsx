"use client";

import type { Route } from "next";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { t } from "@/i18n/messages";
import { getJson, postJson, type Assignment } from "@/lib/api";

import { failure } from "./failure";

type MyQuiz = { slug: string; title: string };

/** The teacher gives the class one of their own quizzes (ADR-0061 § 5);
 *  quizzes are written in the studio. */
export function QuizAssignForm({
  slug,
  onCreated,
}: {
  slug: string;
  onCreated: (assignment: Assignment) => void;
}) {
  const locale = useLocale();
  const [quizzes, setQuizzes] = useState<MyQuiz[] | null>(null);
  const [quiz, setQuiz] = useState("");
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getJson<MyQuiz[]>("/quizzes/mine/")
      .then(setQuizzes)
      .catch(() => setQuizzes([]));
  }, []);

  const picked = quizzes?.find((q) => q.slug === quiz);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!picked) return;
    setBusy(true);
    setError("");
    try {
      const created = await postJson<Assignment>(
        `/classrooms/${encodeURIComponent(slug)}/assignments/`,
        {
          title: title.trim() || picked.title,
          quiz: picked.slug,
          due_at: due ? new Date(due).toISOString() : null,
        },
      );
      onCreated(created);
      setQuiz("");
      setTitle("");
      setDue("");
    } catch (err) {
      setError(failure(locale, err));
    } finally {
      setBusy(false);
    }
  }

  if (quizzes === null) return null;
  if (quizzes.length === 0) {
    return (
      <p className="text-theme-sm rw-faint">
        {t(locale, "classroom.quiz.none")}{" "}
        <Link href={"/studio/quizzes" as Route} className="rw-accent-ink hover:underline">
          {t(locale, "studio.nav.quizzes")}
        </Link>
      </p>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-3">
        <SelectField
          name="quiz"
          label={t(locale, "classroom.quiz.pick")}
          placeholder={t(locale, "classroom.course.pickPlaceholder")}
          options={quizzes.map((q) => ({ value: q.slug, label: q.title }))}
          value={quiz}
          onChange={(value) => {
            setQuiz(value);
            const next = quizzes.find((q) => q.slug === value);
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
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <Button type="submit" busy={busy} disabled={!picked}>
        {t(locale, "classroom.quiz.submit")}
      </Button>
    </form>
  );
}
