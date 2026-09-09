import type { Metadata } from "next";

import { Badge } from "@/components/ui/Badge";
import { ListCard } from "@/components/ui/ListCard";
import { getLocale } from "@/i18n/server";
import { t } from "@/i18n/messages";
import { api } from "@/lib/api";

export const dynamic = "force-dynamic";
export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await getLocale(), "nav.quizzes") };
}

export default async function QuizzesPage() {
  const locale = await getLocale();
  const data = await api.quizzes();
  return (
    <div className="space-y-6">
      <h1 className="text-title-sm font-bold rw-strong">
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
                  <Badge>
                    {q.question_count} {t(locale, "quiz.questions")}
                  </Badge>
                  <Badge color="brand">+{q.reward_qvant} Qvant</Badge>
                  {q.best_score !== null && (
                    <Badge color="success">
                      {t(locale, "quiz.best")}: {q.best_score}/
                      {q.question_count}
                    </Badge>
                  )}
                </>
              }
            />
          </li>
        ))}
      </ul>
      {data.count === 0 && (
        <p className="text-theme-sm rw-faint">{t(locale, "empty")}</p>
      )}
    </div>
  );
}
