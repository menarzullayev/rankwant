import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { QuizPlayer } from "@/features/quizzes";
import { Badge } from "@/components/ui/Badge";
import { getLocale } from "@/i18n/server";
import { fill, t } from "@/i18n/messages";
import { ApiError, type QuizDetail } from "@/lib/api";
import { getWithSession } from "@/lib/api.server";

type Props = { params: Promise<{ slug: string }> };
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    return { title: (await getWithSession<QuizDetail>(`/quizzes/${slug}/`)).title };
  } catch {
    return { title: "404" };
  }
}

export default async function QuizPage({ params }: Props) {
  const locale = await getLocale();
  const { slug } = await params;
  let quiz;
  try {
    // With the session: a teacher's quiz opens only for its class, and the
    // reader's state (started, taken) comes with it (ADR-0061 § 5).
    quiz = await getWithSession<QuizDetail>(`/quizzes/${slug}/`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{quiz.title}</h1>
        <div className="mt-2 flex flex-wrap gap-2">
          <Badge>
            {quiz.question_count} {t(locale, "quiz.questions")}
          </Badge>
          {quiz.is_class ? (
            <Badge>{t(locale, "quiz.classQuiz")}</Badge>
          ) : (
            quiz.reward_qvant > 0 && <Badge color="brand">+{quiz.reward_qvant} Qvant</Badge>
          )}
          {quiz.time_limit_minutes !== null && (
            <Badge>{fill(t(locale, "quiz.timeLimit"), { minutes: quiz.time_limit_minutes })}</Badge>
          )}
          {quiz.one_attempt && <Badge>{t(locale, "quiz.oneAttempt")}</Badge>}
        </div>
        {quiz.description && (
          <p className="mt-2 text-theme-sm rw-dim">{quiz.description}</p>
        )}
      </header>
      <QuizPlayer quiz={quiz} />
    </div>
  );
}
