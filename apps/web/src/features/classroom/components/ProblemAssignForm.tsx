"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { ApiError, postJson, type Assignment } from "@/lib/api";

import { failure } from "./failure";

/** The teacher gives the class problems. Each may be written as its address
 *  or its archive number (`#123`); the server refuses one the students
 *  could not open, by name. */
export function ProblemAssignForm({
  slug,
  onCreated,
}: {
  slug: string;
  onCreated: (assignment: Assignment) => void;
}) {
  const locale = useLocale();
  const [title, setTitle] = useState("");
  const [problems, setProblems] = useState("");
  const [due, setDue] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const list = problems
    .split(/[\s,]+/)
    .map((item) => item.trim())
    .filter(Boolean);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (list.length === 0) return;
    setBusy(true);
    setError("");
    try {
      const created = await postJson<Assignment>(
        `/classrooms/${encodeURIComponent(slug)}/assignments/`,
        {
          title: title.trim(),
          problems: list,
          due_at: due ? new Date(due).toISOString() : null,
        },
      );
      onCreated(created);
      setTitle("");
      setProblems("");
      setDue("");
    } catch (err) {
      const missing = err instanceof ApiError ? err.details.problems : undefined;
      setError(
        Array.isArray(missing) && missing.length > 0
          ? fill(t(locale, "classroom.problems.missing"), { items: missing.join(", ") })
          : failure(locale, err),
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <Field
          name="title"
          label={t(locale, "classroom.problems.title")}
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          maxLength={200}
          required
        />
        <Field
          name="due_at"
          type="datetime-local"
          label={t(locale, "classroom.course.due")}
          value={due}
          onChange={(event) => setDue(event.target.value)}
        />
        <div className="md:col-span-2">
          <Field
            name="problems"
            label={t(locale, "classroom.problems.list")}
            hint={t(locale, "classroom.problems.hint")}
            value={problems}
            onChange={(event) => setProblems(event.target.value)}
            required
          />
        </div>
      </div>
      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      <Button type="submit" busy={busy} disabled={list.length === 0 || !title.trim()}>
        {t(locale, "classroom.problems.submit")}
      </Button>
    </form>
  );
}
