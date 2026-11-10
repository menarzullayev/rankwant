"use client";

import { useCallback, useEffect, useState } from "react";

import { numericStamp } from "@rankwant/shared/format";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Checkbox, SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t } from "@/i18n/messages";
import {
  ApiError,
  getJson,
  postJson,
  type Clarification,
  type ClarificationList,
} from "@/lib/api";

const QUICK = ["yes", "no", "read_statement", "no_comment"] as const;

/** While the contest runs the list is re-read this often. */
const POLL_MS = 30_000;

const TEXTAREA =
  "w-full rw-radius-sm border rw-line rw-field-bg p-2.5 text-theme-sm rw-strong outline-none rw-focus-line rw-fm-inp";

function failure(locale: ReturnType<typeof useLocale>, e: unknown): string {
  if (!(e instanceof ApiError)) return String(e);
  if (e.code === "question_too_soon" && e.retryAfter) {
    return fill(t(locale, "contest.qa.waitSeconds"), { seconds: e.retryAfter });
  }
  return errorText(locale, e.code, e.message);
}

/** The answer as the reader sees it: a quick answer in their own language,
 *  then whatever the jury wrote. */
function AnswerText({ row }: { row: Clarification }) {
  const locale = useLocale();
  return (
    <p className="whitespace-pre-wrap">
      {row.answer_code && (
        <strong className="mr-1">{t(locale, `contest.qa.quick.${row.answer_code}`)}</strong>
      )}
      {row.answer}
    </p>
  );
}

function ProblemTag({ row }: { row: Clarification }) {
  const locale = useLocale();
  return (
    <span className="mr-2 inline-flex min-w-7 items-center justify-center rw-radius-sm rw-chip px-1.5 text-theme-xs font-semibold rw-dim-2">
      {row.problem ?? t(locale, "contest.qa.general")}
    </span>
  );
}

function ModeratorAnswer({
  slug,
  row,
  onDone,
}: {
  slug: string;
  row: Clarification;
  onDone: () => void;
}) {
  const locale = useLocale();
  const [text, setText] = useState("");
  const [isPublic, setPublic] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send(code: string) {
    setBusy(true);
    setError(null);
    try {
      await postJson(`/contests/${slug}/clarifications/${row.id}/answer/`, {
        answer: text,
        answer_code: code,
        public: isPublic,
      });
      onDone();
    } catch (e) {
      setError(failure(locale, e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mt-2 space-y-2" data-qa-answer-form="">
      <div className="flex flex-wrap gap-2">
        {QUICK.map((code) => (
          <Button key={code} variant="outline" busy={busy} onClick={() => send(code)}>
            {t(locale, `contest.qa.quick.${code}`)}
          </Button>
        ))}
      </div>
      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        rows={2}
        maxLength={1000}
        aria-label={t(locale, "contest.qa.answerLabel")}
        placeholder={t(locale, "contest.qa.answerPlaceholder")}
        className={TEXTAREA}
      />
      <div className="flex flex-wrap items-center gap-3">
        <Checkbox checked={isPublic} onChange={(event) => setPublic(event.target.checked)}>
          {t(locale, "contest.qa.makePublic")}
        </Checkbox>
        <Button busy={busy} disabled={!text.trim()} onClick={() => send("")}>
          {t(locale, "contest.qa.answer")}
        </Button>
      </div>
      {error && (
        <p className="text-theme-sm rw-bad-ink" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

function Compose({
  slug,
  letters,
  started,
  kind,
  questionsLeft,
  onDone,
}: {
  slug: string;
  letters: string[];
  started: boolean;
  kind: "ask" | "announce";
  questionsLeft?: number;
  onDone: () => void;
}) {
  const locale = useLocale();
  const [problem, setProblem] = useState("");
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const ask = kind === "ask";
  // Before the start the problems are closed: only the contest itself.
  const options = [
    { value: "", label: t(locale, "contest.qa.general") },
    ...(started ? letters.map((letter) => ({ value: letter, label: letter })) : []),
  ];

  async function send() {
    setBusy(true);
    setError(null);
    try {
      await postJson(
        ask ? `/contests/${slug}/clarifications/` : `/contests/${slug}/announcements/`,
        ask ? { problem: problem || null, question: text } : { problem: problem || null, text },
      );
      setText("");
      onDone();
    } catch (e) {
      setError(failure(locale, e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-2" data-qa-compose={kind}>
      <h3 className="text-theme-sm font-semibold rw-strong">
        {t(locale, ask ? "contest.qa.askTitle" : "contest.qa.announceTitle")}
      </h3>
      <SelectField
        label={t(locale, "contest.qa.problem")}
        options={options}
        value={problem}
        onChange={setProblem}
        size="sm"
      />
      {ask && <p className="text-theme-xs rw-dim">{t(locale, "contest.qa.askHint")}</p>}
      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        rows={3}
        maxLength={1000}
        aria-label={t(locale, ask ? "contest.qa.askTitle" : "contest.qa.announceTitle")}
        className={TEXTAREA}
      />
      <div className="flex flex-wrap items-center gap-3">
        <Button busy={busy} disabled={!text.trim()} onClick={send}>
          {t(locale, ask ? "contest.qa.send" : "contest.qa.announce")}
        </Button>
        {ask && questionsLeft !== undefined && (
          <span className="text-theme-xs rw-dim">
            {fill(t(locale, "contest.qa.left"), { count: questionsLeft })}
          </span>
        )}
        {!ask && <span className="text-theme-xs rw-dim">{t(locale, "contest.qa.announceNote")}</span>}
      </div>
      {error && (
        <p className="text-theme-sm rw-bad-ink" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

/** «Savol-javob» on a contest page (ADR-0055, part 3).
 *
 *  Announcements on top; the public answers; the visitor's own questions;
 *  for the jury, the questions waiting for an answer.
 */
export function ContestClarifications({
  slug,
  initial,
  letters,
  started,
  finished,
}: {
  slug: string;
  initial: ClarificationList | null;
  letters: string[];
  started: boolean;
  finished: boolean;
}) {
  const locale = useLocale();
  const [data, setData] = useState<ClarificationList | null>(initial);

  const reload = useCallback(() => {
    getJson<ClarificationList>(`/contests/${slug}/clarifications/`)
      .then(setData)
      .catch(() => undefined);
  }, [slug]);

  useEffect(() => {
    if (finished) return;
    const timer = setInterval(reload, POLL_MS);
    return () => clearInterval(timer);
  }, [finished, reload]);

  if (data === null) return null;
  const announcements = data.results.filter((row) => row.is_announcement);
  const waiting = data.moderator ? data.results.filter((row) => !row.answered_at) : [];
  const mine = data.results.filter((row) => row.mine && !row.is_announcement);
  const answered = data.results.filter(
    (row) => !row.is_announcement && !row.mine && row.answered_at,
  );
  const empty =
    announcements.length + waiting.length + mine.length + answered.length === 0 &&
    !data.can_ask &&
    !data.moderator;
  if (empty) return null;

  return (
    <section id="clarifications" aria-labelledby="clarifications-title" className="scroll-mt-20">
      <Card title={t(locale, "contest.qa.title")}>
        <h2 id="clarifications-title" className="sr-only">
          {t(locale, "contest.qa.title")}
        </h2>
        <div className="space-y-6">
          {announcements.length > 0 && (
            <ul className="space-y-2" data-qa-announcements="">
              {announcements.map((row) => (
                <li key={row.id} className="rw-radius-sm rw-warn-soft px-3 py-2 text-theme-sm rw-warn-ink">
                  <div className="mb-1 flex flex-wrap items-center text-theme-xs font-semibold">
                    <ProblemTag row={row} />
                    {/* Digits only: the same on the server and in every browser. */}
                    <time dateTime={row.created_at}>{numericStamp(row.created_at)}</time>
                  </div>
                  <AnswerText row={row} />
                </li>
              ))}
            </ul>
          )}

          {waiting.length > 0 && (
            <div data-qa-waiting="">
              <h3 className="mb-2 text-theme-sm font-semibold rw-strong">
                {fill(t(locale, "contest.qa.waiting"), { count: waiting.length })}
              </h3>
              <ul className="rw-divide divide-y">
                {waiting.map((row) => (
                  <li key={row.id} className="py-3 text-theme-sm">
                    <p className="whitespace-pre-wrap font-medium rw-strong">
                      <ProblemTag row={row} />
                      {row.question}
                    </p>
                    <p className="mt-1 text-theme-xs rw-dim">{row.author}</p>
                    <ModeratorAnswer slug={slug} row={row} onDone={reload} />
                  </li>
                ))}
              </ul>
            </div>
          )}

          {[
            { key: "mine", rows: mine, title: "contest.qa.mine" },
            { key: "answered", rows: answered, title: "contest.qa.answered" },
          ]
            .filter((group) => group.rows.length > 0)
            .map((group) => (
              <div key={group.key} data-qa-list={group.key}>
                <h3 className="mb-2 text-theme-sm font-semibold rw-strong">
                  {t(locale, group.title)}
                </h3>
                <ul className="rw-divide divide-y">
                  {group.rows.map((row) => (
                    <li key={row.id} className="py-3 text-theme-sm">
                      <p className="whitespace-pre-wrap font-medium rw-strong">
                        <ProblemTag row={row} />
                        {row.question}
                      </p>
                      {row.answered_at ? (
                        <div className="mt-2 rw-radius-sm rw-ok-soft px-3 py-2 rw-ok-ink">
                          {row.is_public && (
                            <span className="mb-1 block text-theme-xs font-semibold">
                              {t(locale, "contest.qa.public")}
                            </span>
                          )}
                          <AnswerText row={row} />
                        </div>
                      ) : (
                        <p className="mt-1 text-theme-xs italic rw-dim">
                          {t(locale, "contest.qa.pending")}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}

          {data.can_ask && (
            <Compose
              slug={slug}
              letters={letters}
              started={started}
              kind="ask"
              questionsLeft={data.questions_left}
              onDone={reload}
            />
          )}
          {data.moderator && (
            <Compose slug={slug} letters={letters} started={started} kind="announce" onDone={reload} />
          )}
        </div>
      </Card>
    </section>
  );
}
