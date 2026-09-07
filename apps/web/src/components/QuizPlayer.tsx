"use client";

import { useState } from "react";

import { Markdown } from "@/components/Markdown";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useSession } from "@/context/SessionContext";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { ApiError, postJson, type QuizDetail, type QuizResult } from "@/lib/api";

export function QuizPlayer({ quiz }: { quiz: QuizDetail }) {
  const locale = DEFAULT_LOCALE;
  const { user, ready } = useSession();
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    setError("");
    try {
      setResult(await postJson<QuizResult>(`/quizzes/${quiz.slug}/submit/`, { answers }));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const review = new Map(result?.review.map((r) => [r.question_id, r]) ?? []);

  return (
    <div className="space-y-4">
      {result && (
        <Card title={t(locale, "quiz.result")}>
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-title-sm font-bold text-gray-800 dark:text-white/90">
              {result.score} / {result.total}
            </span>
            {result.qvant_awarded > 0 && <Badge color="brand">+{result.qvant_awarded} Qvant</Badge>}
          </div>
        </Card>
      )}

      {quiz.questions.map((q, i) => {
        const r = review.get(q.id);
        return (
          <Card key={q.id} title={`${i + 1}.`}>
            <Markdown>{q.text}</Markdown>
            <div className="mt-4 grid gap-2">
              {q.choices.map((c) => {
                const chosen = answers[q.id] === c.id;
                let tone = "border-gray-200 dark:border-[#232936]";
                if (r) {
                  if (c.id === r.correct) tone = "border-success-500 bg-success-50 dark:bg-success-500/12";
                  else if (chosen && !r.is_correct) tone = "border-error-500 bg-error-50 dark:bg-error-500/12";
                } else if (chosen) tone = "border-brand-500 bg-brand-50 dark:bg-brand-500/12";
                return (
                  <button
                    key={c.id}
                    type="button"
                    disabled={!!result}
                    onClick={() => setAnswers((a) => ({ ...a, [q.id]: c.id }))}
                    className={`rounded-lg border px-4 py-2.5 text-left text-theme-sm transition ${tone}`}
                  >
                    {c.text}
                  </button>
                );
              })}
            </div>
            {r?.explanation && (
              <p className="mt-3 text-theme-sm text-gray-500 dark:text-gray-400">{r.explanation}</p>
            )}
          </Card>
        );
      })}

      {error && <p className="text-theme-sm text-error-500">{error}</p>}
      {!result && ready && (
        user ? (
          <Button onClick={submit} disabled={busy}>{t(locale, "quiz.submit")}</Button>
        ) : (
          <p className="text-theme-sm text-gray-400">{t(locale, "auth.login")} →</p>
        )
      )}
    </div>
  );
}
