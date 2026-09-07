import type { Metadata } from "next";

import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { DEFAULT_LOCALE, t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Testlar" };

export default async function QuizzesPage() {
  const locale = DEFAULT_LOCALE;
  const data = await api.quizzes();
  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold text-gray-800 dark:text-white/90">
        {t(locale, "nav.quizzes")}
      </h1>
      <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {data.results.map((q) => (
          <li key={q.slug}>
            <ListCard
              href={`/quizzes/${q.slug}`}
              title={q.title}
              summary={q.description}
              meta={
                <>
                  <Badge>{q.question_count} {t(locale, "quiz.questions")}</Badge>
                  <Badge color="brand">+{q.reward_qvant} Qvant</Badge>
                  {q.best_score !== null && (
                    <Badge color="success">
                      {t(locale, "quiz.best")}: {q.best_score}/{q.question_count}
                    </Badge>
                  )}
                </>
              }
            />
          </li>
        ))}
      </ul>
      {data.count === 0 && <p className="text-theme-sm text-gray-400">{t(locale, "empty")}</p>}
    </div>
  );
}
