"use client";

import { useEffect, useState } from "react";

import { FormBox } from "@/components/form/FormKit";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { SelectField } from "@/components/ui/SelectField";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, t } from "@/i18n/messages";
import { ApiError, getJson, patchJson, type Paginated } from "@/lib/api";

import { KIND_KEYS, type AuthorQuestion, type AuthorQuiz } from "../api/quizzes";

/** `datetime-local` wants local time without a zone. */
function localInput(iso: string | null): string {
  if (!iso) return "";
  const date = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

/** One quiz: its settings and its questions, picked from the teacher's bank. */
export function QuizEditor({ slug }: { slug: string }) {
  const locale = useLocale();
  const [quiz, setQuiz] = useState<AuthorQuiz | null>(null);
  const [bank, setBank] = useState<AuthorQuestion[]>([]);
  const [order, setOrder] = useState<number[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [minutes, setMinutes] = useState("");
  const [oneAttempt, setOneAttempt] = useState(false);
  const [after, setAfter] = useState("");
  const [pick, setPick] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const path = `/quizzes/mine/${encodeURIComponent(slug)}/`;

  useEffect(() => {
    getJson<AuthorQuiz>(path)
      .then((row) => {
        setQuiz(row);
        setOrder(row.questions.map((q) => q.id));
        setTitle(row.title);
        setDescription(row.description);
        setMinutes(row.time_limit_minutes === null ? "" : String(row.time_limit_minutes));
        setOneAttempt(row.one_attempt);
        setAfter(localInput(row.answers_after));
      })
      .catch(() => setError("404"));
    getJson<Paginated<AuthorQuestion>>("/questions/mine/?page_size=100")
      .then((page) => setBank(page.results))
      .catch(() => setBank([]));
  }, [path]);

  if (!quiz) return error ? <p className="text-theme-sm rw-faint">{error}</p> : null;
  const fixed = quiz.attempt_count > 0;
  const byId = new Map(bank.map((q) => [q.id, q]));
  const free = bank.filter((q) => !order.includes(q.id));

  function move(index: number, delta: number) {
    setOrder((ids) => {
      const next = [...ids];
      const [item] = next.splice(index, 1);
      next.splice(index + delta, 0, item);
      return next;
    });
  }

  async function save() {
    setBusy(true);
    setMessage("");
    setError("");
    const body: Record<string, unknown> = {
      title: title.trim(),
      description,
      time_limit_minutes: minutes ? Number(minutes) : null,
      one_attempt: oneAttempt,
      answers_after: after ? new Date(after).toISOString() : null,
    };
    if (!fixed) body.question_ids = order;
    try {
      setQuiz(await patchJson<AuthorQuiz>(path, body));
      setMessage(t(locale, "studio.quizzes.saved"));
    } catch (err) {
      setError(err instanceof ApiError ? errorText(locale, err.code, err.message) : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-title-sm font-bold rw-strong">{quiz.title}</h1>

      <Card title={t(locale, "studio.quizzes.settings")}>
        <div className="grid gap-4 md:grid-cols-2">
          <Field
            name="title"
            label={t(locale, "admin.label.text.name")}
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            maxLength={200}
          />
          <Field
            name="time_limit_minutes"
            type="number"
            min={1}
            max={600}
            label={t(locale, "studio.quizzes.timeLimit")}
            value={minutes}
            onChange={(event) => setMinutes(event.target.value)}
          />
          <Field
            name="answers_after"
            type="datetime-local"
            label={t(locale, "studio.quizzes.answersAfter")}
            value={after}
            onChange={(event) => setAfter(event.target.value)}
          />
          <label className="flex items-center gap-3 self-end py-2 text-theme-sm rw-strong">
            <FormBox
              shape="switch"
              checked={oneAttempt}
              aria-label={t(locale, "studio.quizzes.oneAttempt")}
              onChange={(event) => setOneAttempt(event.target.checked)}
            />
            {t(locale, "studio.quizzes.oneAttempt")}
          </label>
          <div className="md:col-span-2">
            <Field
              name="description"
              label={t(locale, "admin.label.text.description")}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>
        </div>
      </Card>

      <Card title={t(locale, "studio.quizzes.questions")}>
        {fixed && <p className="mb-3 text-theme-sm rw-warn-ink">{t(locale, "studio.quizzes.fixed")}</p>}
        <ol className="space-y-2">
          {order.map((id, index) => {
            const question = byId.get(id);
            const text = question?.text ?? quiz.questions.find((q) => q.id === id)?.text ?? `#${id}`;
            return (
              <li key={id} className="flex flex-wrap items-center gap-2 rw-radius-sm border rw-line px-3 py-2">
                <span className="w-6 text-theme-xs tabular-nums rw-faint">{index + 1}.</span>
                <span className="min-w-0 flex-1 truncate text-theme-sm rw-strong">{text}</span>
                {question && <Badge>{t(locale, KIND_KEYS[question.kind])}</Badge>}
                {!fixed && (
                  <>
                    <Button variant="outline" disabled={index === 0} onClick={() => move(index, -1)}>
                      ↑
                    </Button>
                    <Button
                      variant="outline"
                      disabled={index === order.length - 1}
                      onClick={() => move(index, 1)}
                    >
                      ↓
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setOrder((ids) => ids.filter((x) => x !== id))}
                    >
                      {t(locale, "studio.quizzes.remove")}
                    </Button>
                  </>
                )}
              </li>
            );
          })}
        </ol>
        {!fixed && free.length > 0 && (
          <div className="mt-4 flex flex-wrap items-end gap-2">
            <div className="min-w-0 flex-1">
              <SelectField
                name="pick"
                label={t(locale, "studio.quizzes.addFromBank")}
                placeholder={t(locale, "classroom.course.pickPlaceholder")}
                options={free.map((q) => ({ value: String(q.id), label: q.text.slice(0, 80) }))}
                value={pick}
                onChange={setPick}
              />
            </div>
            <Button
              variant="outline"
              disabled={!pick}
              onClick={() => {
                setOrder((ids) => [...ids, Number(pick)]);
                setPick("");
              }}
            >
              +
            </Button>
          </div>
        )}
      </Card>

      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      {message && (
        <p role="status" className="text-theme-sm rw-ok-ink">
          {message}
        </p>
      )}
      <Button busy={busy} onClick={() => void save()}>
        {t(locale, "studio.quizzes.save")}
      </Button>
    </div>
  );
}
