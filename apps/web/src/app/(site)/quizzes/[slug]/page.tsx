import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { QuizPlayer } from "@/features/quizzes";
import { Badge } from "@/components/ui/Badge";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api, ApiError } from "@/lib/api";

type Props = { params: Promise<{ slug: string }> };
export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    return { title: (await api.quiz(slug)).title };
  } catch {
    return { title: "404" };
  }
}

export default async function QuizPage({ params }: Props) {
  const locale = await getLocale();
  const { slug } = await params;
  let quiz;
  try {
    quiz = await api.quiz(slug);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">{quiz.title}</h1>
        <div className="mt-2 flex gap-2">
          <Badge>
            {quiz.question_count} {t(locale, "quiz.questions")}
          </Badge>
          <Badge color="brand">+{quiz.reward_qvant} Qvant</Badge>
        </div>
        {quiz.description && (
          <p className="mt-2 text-theme-sm rw-dim">{quiz.description}</p>
        )}
      </header>
      <QuizPlayer quiz={quiz} />
    </div>
  );
}
