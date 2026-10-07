"use client";

import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { useLocale } from "@/i18n/LocaleProvider";
import { fill, t } from "@/i18n/messages";
import { ApiError } from "@/lib/api";

import { answerInputsUrl, submitAnswerFiles } from "../api/problems";

/** The server's limits (ADR-0053), repeated here so an oversize upload is
 *  refused before it travels. The server checks again. */
const MAX_BYTES = 10 * 1024 * 1024;

const pad = (order: number) => String(order).padStart(2, "0");

/** The submit side of an `answer` problem: files instead of an editor.
 *
 *  One slot per test. A file picked in a slot is sent under that test's
 *  number whatever it is called on disk; files packed in a zip are matched
 *  by the number in their names. A slot left empty keeps the answer last
 *  sent for it — the server does that, the panel only says so. */
export function AnswerPanel({
  problem,
  tests,
  contest,
}: {
  problem: string;
  tests: number[];
  contest?: string;
}) {
  const locale = useLocale();
  const router = useRouter();
  const { user, ready } = useSession();
  const [files, setFiles] = useState<Record<number, File>>({});
  const [archive, setArchive] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const picked = Object.keys(files).length;
  const bytes =
    Object.values(files).reduce((sum, file) => sum + file.size, 0) + (archive?.size ?? 0);
  const canSubmit = ready && !!user && (picked > 0 || archive !== null) && !busy;

  function pick(order: number, file: File | undefined) {
    setError(null);
    setFiles((current) => {
      const next = { ...current };
      if (file) next[order] = file;
      else delete next[order];
      return next;
    });
  }

  async function submit() {
    if (!canSubmit) return;
    if (bytes > MAX_BYTES) {
      setError(t(locale, "answer.tooLarge"));
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const created = await submitAnswerFiles({ problem, contest, files, archive });
      router.push(`/attempts/${created.id}` as Route);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : t(locale, "answer.failed"));
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <Card title={t(locale, "answer.title")}>
        <div className="space-y-4">
          <p className="text-theme-sm rw-dim">{t(locale, "answer.hint")}</p>
          <div>
            {/* A file from the API, not a page: a plain link with `download`. */}
            <a
              href={answerInputsUrl(problem)}
              download
              className="inline-flex min-h-11 items-center rw-radius-sm border rw-line px-4 text-theme-sm font-medium rw-strong rw-hover-bg rw-focus-ring"
            >
              {t(locale, "answer.download")}
            </a>
          </div>

          <ul className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {tests.map((order) => {
              const file = files[order];
              return (
                <li key={order}>
                  <label className="flex min-h-14 cursor-pointer flex-col justify-center rw-radius-sm border rw-line px-3 py-2 rw-hover-bg focus-within:rw-focus-ring">
                    <span className="font-mono text-theme-sm font-semibold rw-strong">
                      {pad(order)}
                    </span>
                    <span className="truncate text-theme-xs rw-dim">
                      {file ? file.name : t(locale, "answer.noFile")}
                    </span>
                    <input
                      type="file"
                      className="sr-only"
                      aria-label={fill(t(locale, "answer.pick"), { order })}
                      onChange={(event) => pick(order, event.target.files?.[0])}
                    />
                  </label>
                </li>
              );
            })}
          </ul>

          <label className="block space-y-1">
            <span className="text-theme-xs rw-dim">{t(locale, "answer.zip")}</span>
            <input
              type="file"
              accept=".zip,application/zip"
              className="block w-full text-theme-sm rw-dim"
              onChange={(event) => {
                setError(null);
                setArchive(event.target.files?.[0] ?? null);
              }}
            />
          </label>

          <p className="text-theme-xs rw-faint">{t(locale, "answer.kept")}</p>

          {error ? (
            <p role="alert" className="text-theme-sm rw-strong">
              {error}
            </p>
          ) : null}

          <div className="flex flex-wrap items-center gap-3">
            <Button type="button" onClick={submit} disabled={!canSubmit}>
              {t(locale, "answer.submit")}
            </Button>
            {ready && !user ? (
              <span className="text-theme-xs rw-dim">{t(locale, "submit.signInToSubmit")}</span>
            ) : (
              <span className="text-theme-xs rw-faint">
                {fill(t(locale, "answer.count"), { picked, total: tests.length })}
              </span>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
