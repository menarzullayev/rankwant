"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { t, errorText } from "@/i18n/messages";
import {
  ApiError,
  getJson,
  postJson,
  type Hackathon,
  type HackathonSubmission,
} from "@/lib/api";

export function HackathonEntries({ hackathon }: { hackathon: Hackathon }) {
  const locale = useLocale();
  const { user, ready } = useSession();
  const [entries, setEntries] = useState<HackathonSubmission[]>([]);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const load = () =>
    getJson<{ results: HackathonSubmission[] }>(
      `/hackathons/${hackathon.slug}/submissions/`,
    )
      .then((d) => setEntries(d.results))
      .catch(() => {});

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hackathon.slug, user]);

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setSaved(false);
    const f = Object.fromEntries(new FormData(e.currentTarget));
    try {
      await postJson(`/hackathons/${hackathon.slug}/submit/`, f);
      setSaved(true);
      await load();
    } catch (err) {
      setError(
        err instanceof ApiError
          ? errorText(locale, err.code, err.message)
          : String(err),
      );
    }
  }

  const mine = user
    ? entries.find((x) => x.username === user.username)
    : undefined;

  return (
    <div className="space-y-6">
      {ready && user && hackathon.accepts_submissions && (
        <Card title={t(locale, "hackathon.submit")}>
          <form onSubmit={submit} className="grid gap-3 md:grid-cols-2">
            <Field
              label={t(locale, "hackathon.projectName")}
              name="title"
              required
              defaultValue={mine?.title}
            />
            <Field
              label={t(locale, "hackathon.team")}
              name="team_name"
              defaultValue={mine?.team_name}
            />
            <Field
              label={t(locale, "hackathon.repo")}
              name="repo_url"
              type="url"
              required
              defaultValue={mine?.repo_url}
            />
            <Field
              label={t(locale, "hackathon.demo")}
              name="demo_url"
              type="url"
              defaultValue={mine?.demo_url}
            />
            <label className="block md:col-span-2">
              <span className="mb-1.5 block text-theme-sm font-medium rw-strong">
                Tavsif (Markdown)
              </span>
              <textarea
                name="description"
                required
                rows={5}
                defaultValue={mine?.description}
                className="w-full rw-radius-sm border rw-line rw-surface px-4 py-2 text-theme-sm outline-none rw-focus-line rw-field-bg rw-fm-inp"
              />
            </label>
            <div className="flex items-center gap-3 md:col-span-2">
              <Button type="submit">{t(locale, "hackathon.submit")}</Button>
              {saved && <Badge color="success">✓</Badge>}
              {error && (
                <span className="text-theme-sm rw-bad-ink">{error}</span>
              )}
            </div>
          </form>
        </Card>
      )}
      <Card title={t(locale, "hackathon.entries")} bodyClassName="p-0">
        <ul className="divide-y rw-divide">
          {entries.map((s) => (
            <li key={s.id} className="px-5 py-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-semibold rw-strong">{s.title}</span>
                {s.team_name && <Badge>{s.team_name}</Badge>}
                <span className="text-theme-xs rw-faint">@{s.username}</span>
                {s.score !== null && (
                  <Badge color="brand">
                    {t(locale, "hackathon.score")}: {s.score}/100
                  </Badge>
                )}
              </div>
              <p className="mt-1 text-theme-sm rw-dim">
                {s.description.slice(0, 240)}
              </p>
              <p className="mt-2 flex gap-3 text-theme-xs">
                <a
                  href={s.repo_url}
                  className="rw-accent-ink hover:underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  {t(locale, "hackathon.repo")}
                </a>
                {s.demo_url && (
                  <a
                    href={s.demo_url}
                    className="rw-accent-ink hover:underline"
                    target="_blank"
                    rel="noreferrer"
                  >
                    {t(locale, "hackathon.demo")}
                  </a>
                )}
              </p>
              {s.feedback && (
                <p className="mt-2 text-theme-sm rw-dim italic">{s.feedback}</p>
              )}
            </li>
          ))}
          {entries.length === 0 && (
            <li className="px-5 py-6 text-center text-theme-sm rw-faint">
              {hackathon.accepts_submissions
                ? t(locale, "hackathon.entriesAfterDeadline")
                : t(locale, "common.empty")}
            </li>
          )}
        </ul>
      </Card>
    </div>
  );
}
