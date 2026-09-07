import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { QuizPlayer } from "@/components/QuizPlayer";
import { Badge } from "@/components/ui/Badge";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
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
        <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">{quiz.title}</h1>
        <div className="mt-2 flex gap-2">
          <Badge>{quiz.question_count} {t(DEFAULT_LOCALE, "quiz.questions")}</Badge>
          <Badge color="brand">+{quiz.reward_qvant} Qvant</Badge>
        </div>
        {quiz.description && (
          <p className="mt-2 text-theme-sm text-gray-500 dark:text-gray-400">{quiz.description}</p>
        )}
      </header>
      <QuizPlayer quiz={quiz} />
    </div>
  );
}
