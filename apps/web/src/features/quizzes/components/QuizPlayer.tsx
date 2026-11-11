"use client";

import { numericStamp } from "@rankwant/shared/format";
import { SignInGate } from "@/components/auth/SignInGate";
import { useCallback, useEffect, useRef, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { CodeSnippet } from "@/components/ui/CodeSnippet";
import { Field } from "@/components/ui/Field";
import { Markdown } from "@/components/ui/Markdown";
import { useSession } from "@/context/SessionContext";
import { inReaderAlphabet } from "@/i18n/alphabet";
import { useLocale } from "@/i18n/LocaleProvider";
import { errorText, fill, t } from "@/i18n/messages";
import {
  ApiError,
  getJson,
  postJson,
  type Question,
  type QuizAnswer,
  type QuizDetail,
  type QuizResult,
} from "@/lib/api";

type Review = QuizResult["review"][number];

function asList(value: unknown): number[] {
  return Array.isArray(value) ? value.filter((v): v is number => typeof v === "number") : [];
}

function clock(ms: number): string {
  const total = Math.max(0, Math.ceil(ms / 1000));
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

/** A number answer gets the phone's number keyboard. */
const INPUT_MODE: Partial<Record<Question["kind"], "decimal">> = { number: "decimal" };

/** Answers one question; each kind keeps its own input (ADR-0061 § 5). */
function QuestionCard({
  index,
  question,
  answer,
  review,
  locked,
  onAnswer,
}: {
  index: number;
  question: Question;
  answer: QuizAnswer | undefined;
  review: Review | undefined;
  locked: boolean;
  onAnswer: (value: QuizAnswer) => void;
}) {
  const locale = useLocale();
  const multiple = question.kind === "multiple";
  const chosenList = asList(answer);
  const rightList =
    review && review.correct_value !== null
      ? multiple
        ? asList(review.correct_value)
        : typeof review.correct_value === "number"
          ? [review.correct_value]
          : []
      : [];

  return (
    <Card title={`${index + 1}.`}>
      <Markdown lang="uz">{question.text}</Markdown>
      {question.code && (
        <div className="mt-3">
          <CodeSnippet code={question.code} language={question.code_language} />
        </div>
      )}
      {multiple && !locked && (
        <p className="mt-3 text-theme-xs rw-dim">{t(locale, "quiz.pickAll")}</p>
      )}
      {question.kind === "single" || multiple ? (
        <div className="mt-4 grid gap-2">
          {question.choices.map((choice) => {
            const chosen = multiple ? chosenList.includes(choice.id) : answer === choice.id;
            let tone = "rw-line ";
            if (review && review.correct_value !== null) {
              if (rightList.includes(choice.id)) tone = "border-success-500 rw-ok-soft ";
              else if (chosen) tone = "border-error-500 rw-bad-soft ";
            } else if (chosen) tone = "rw-accent-line rw-accent-soft ";
            return (
              <button
                key={choice.id}
                type="button"
                disabled={locked}
                aria-pressed={chosen}
                onClick={() =>
                  onAnswer(
                    multiple
                      ? chosen
                        ? chosenList.filter((id) => id !== choice.id)
                        : [...chosenList, choice.id]
                      : choice.id,
                  )
                }
                className={`rw-radius-sm border px-4 py-2.5 text-left text-theme-sm transition ${tone}`}
              >
                {multiple ? (chosen ? "☑ " : "☐ ") : ""}
                {inReaderAlphabet(choice.text, "uz")}
              </button>
            );
          })}
        </div>
      ) : (
        <div className="mt-4 max-w-sm">
          <Field
            name={`q${question.id}`}
            label={t(locale, question.kind === "number" ? "quiz.numberAnswer" : "quiz.textAnswer")}
            inputMode={INPUT_MODE[question.kind]}
            value={typeof answer === "string" || typeof answer === "number" ? String(answer) : ""}
            disabled={locked}
            onChange={(event) => onAnswer(event.target.value)}
          />
        </div>
      )}
      {review && review.correct_value !== null && !review.is_correct &&
        (question.kind === "number" || question.kind === "text") && (
          <p className="mt-3 text-theme-sm rw-ok-ink">
            {fill(t(locale, "quiz.rightAnswer"), { answer: String(review.correct_value) })}
          </p>
        )}
      {review?.explanation && <p className="mt-3 text-theme-sm rw-dim">{review.explanation}</p>}
    </Card>
  );
}

export function QuizPlayer({ quiz: initial }: { quiz: QuizDetail }) {
  const locale = useLocale();
  const { user, ready } = useSession();
  const [quiz, setQuiz] = useState(initial);
  const [answers, setAnswers] = useState<Record<number, QuizAnswer>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  const sent = useRef(false);
  const timed = quiz.time_limit_minutes !== null;
  const path = `/quizzes/${encodeURIComponent(quiz.slug)}/`;

  // The page is rendered on the server with the reader's state; a finished
  // one-attempt quiz shows its last result instead of a fresh form.
  useEffect(() => {
    if (user && initial.state.taken) {
      getJson<QuizResult>(`${path}result/`)
        .then(setResult)
        .catch(() => {});
    }
  }, [user, initial.state.taken, path]);

  const submit = useCallback(async () => {
    if (sent.current) return;
    sent.current = true;
    setBusy(true);
    setError("");
    try {
      setResult(await postJson<QuizResult>(`${path}submit/`, { answers }));
    } catch (e) {
      sent.current = false;
      setError(e instanceof ApiError ? errorText(locale, e.code, e.message) : String(e));
    } finally {
      setBusy(false);
    }
  }, [answers, locale, path]);

  const deadline = quiz.state.deadline ? Date.parse(quiz.state.deadline) : null;
  const submitRef = useRef(submit);
  useEffect(() => {
    submitRef.current = submit;
  }, [submit]);
  useEffect(() => {
    if (deadline === null || result) return;
    const timer = window.setInterval(() => {
      const tick = Date.now();
      setNow(tick);
      // At zero the page sends what it has; the server allows a short grace.
      if (tick >= deadline) void submitRef.current();
    }, 1000);
    return () => window.clearInterval(timer);
  }, [deadline, result]);

  async function start() {
    setBusy(true);
    setError("");
    try {
      await postJson(`${path}start/`, {});
      setQuiz(await getJson<QuizDetail>(path));
    } catch (e) {
      setError(e instanceof ApiError ? errorText(locale, e.code, e.message) : String(e));
    } finally {
      setBusy(false);
    }
  }

  // The questions are the working panel: a guest gets the card, not a
  // form whose answers would go nowhere.
  if (ready && !user) return <SignInGate reason="quiz" />;

  const review = new Map(result?.review.map((r) => [r.question_id, r]) ?? []);
  const locked = Boolean(result) || quiz.state.taken;

  return (
    <div className="space-y-4">
      {result && (
        <Card title={t(locale, "quiz.result")}>
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-title-sm font-bold rw-strong">
              {result.score} / {result.total}
            </span>
            {result.qvant_awarded > 0 && <Badge color="brand">+{result.qvant_awarded} Qvant</Badge>}
          </div>
          {result.answers_hidden && quiz.answers_after && (
            <p className="mt-2 text-theme-sm rw-dim">
              {fill(t(locale, "quiz.answersAfter"), { date: numericStamp(quiz.answers_after) })}
            </p>
          )}
        </Card>
      )}

      {quiz.state.taken && !result && (
        <p className="text-theme-sm rw-dim">{t(locale, "quiz.taken")}</p>
      )}

      {timed && !quiz.state.started && !quiz.state.taken && !result && (
        <Card title={t(locale, "quiz.start")}>
          <p className="text-theme-sm rw-dim">{t(locale, "quiz.startHint")}</p>
          <div className="mt-4">
            <Button busy={busy} onClick={() => void start()}>
              {t(locale, "quiz.start")}
            </Button>
          </div>
        </Card>
      )}

      {deadline !== null && !result && (
        <p
          role="timer"
          aria-live="off"
          className="sticky top-[var(--rw-header-h)] z-10 rw-radius-sm border rw-line rw-surface px-4 py-2 text-theme-sm font-semibold tabular-nums rw-strong"
        >
          {fill(t(locale, "quiz.timeLeft"), { time: clock(deadline - now) })}
        </p>
      )}

      {quiz.questions.map((question, index) => (
        <QuestionCard
          key={question.id}
          index={index}
          question={question}
          answer={answers[question.id]}
          review={review.get(question.id)}
          locked={locked}
          onAnswer={(value) => setAnswers((current) => ({ ...current, [question.id]: value }))}
        />
      ))}

      {error && (
        <p role="alert" className="text-theme-sm rw-bad-ink">
          {error}
        </p>
      )}
      {!locked && ready && quiz.questions.length > 0 && (
        <Button onClick={() => void submit()} disabled={busy}>
          {t(locale, "quiz.submit")}
        </Button>
      )}
    </div>
  );
}
