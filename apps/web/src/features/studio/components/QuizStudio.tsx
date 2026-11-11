"use client";

import type { Route } from "next";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t } from "@/i18n/messages";
import { ApiError, getJson, postJson } from "@/lib/api";
import { quotaFull, quotaOf, type Quota, type Quotas } from "@/lib/quotas";

import type { AuthorQuiz } from "../api/quizzes";

/** The teacher's quizzes: give one to a class from the class page
 *  (ADR-0061 § 5). The plan's `quizzes` quota counts every one. */
export function QuizStudio() {
  const locale = useLocale();
  const [rows, setRows] = useState<AuthorQuiz[] | null>(null);
  const [quota, setQuota] = useState<Quota | null>(null);
  const [title, setTitle] = useState("");
  const [slug, setSlug] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    void getJson<AuthorQuiz[]>("/quizzes/mine/")
      .then(setRows)
      .catch(() => setRows([]));
    void getJson<Quotas>("/me/quotas/")
      .then((all) => setQuota(quotaOf(all, "quizzes")))
      .catch(() => setQuota(null));
  }, []);
  useEffect(() => load(), [load]);

  async function create(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await postJson("/quizzes/mine/", { title: title.trim(), slug: slug.trim() });
      setTitle("");
      setSlug("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code, err.message) : String(err));
    } finally {
      setBusy(false);
    }
  }

  const full = quota !== null && quotaFull(quota);

  return (
    <div className="space-y-4">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{t(locale, "studio.nav.quizzes")}</h1>
        <p className="mt-1 max-w-2xl text-theme-sm rw-dim">{t(locale, "studio.quizzes.intro")}</p>
      </header>

      <Card title={t(locale, "studio.quizzes.new")}>
        <form onSubmit={create} className="grid gap-3 md:grid-cols-[2fr_1fr_auto] md:items-end">
          <Field
            name="title"
            label={t(locale, "admin.label.text.name")}
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            required
            maxLength={200}
          />
          <Field
            name="slug"
            label={t(locale, "admin.label.text.slug")}
            value={slug}
            onChange={(event) => setSlug(event.target.value)}
            required
            pattern="[a-z0-9\-]+"
          />
          <Button type="submit" busy={busy} disabled={full}>
            {t(locale, "studio.quizzes.new")}
          </Button>
        </form>
        {quota && quota.limit !== null && (
          <p className={`mt-2 text-theme-xs ${full ? "rw-bad-ink" : "rw-faint"}`}>
            {fill(t(locale, full ? "studio.quizzes.full" : "studio.quizzes.count"), {
              count: quota.used,
              limit: quota.limit,
            })}
          </p>
        )}
        {error && (
          <p role="alert" className="mt-2 text-theme-sm rw-bad-ink">
            {error}
          </p>
        )}
      </Card>

      <Card bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {(rows ?? []).map((row) => (
            <li key={row.slug} className="flex flex-wrap items-center gap-3 px-5 py-3">
              <Link
                href={`/studio/quizzes/${encodeURIComponent(row.slug)}` as Route}
                className="min-w-0 flex-1 font-medium rw-strong rw-link-hover"
              >
                {row.title}
              </Link>
              <Badge>{fill(t(locale, "studio.quizzes.questionCount"), { count: row.questions.length })}</Badge>
              {row.attempt_count > 0 && (
                <Badge color="info">
                  {fill(t(locale, "studio.quizzes.attempts"), { count: row.attempt_count })}
                </Badge>
              )}
            </li>
          ))}
          {rows !== null && rows.length === 0 && (
            <li className="px-5 py-6 text-center text-theme-sm rw-faint">
              {t(locale, "studio.quizzes.empty")}
            </li>
          )}
        </ul>
      </Card>
    </div>
  );
}
