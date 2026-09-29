import Link from "next/link";
import type { Route } from "next";

import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Editorial } from "@/features/problems";
import { fill, t, type Locale } from "@/i18n/messages";
import type { ProblemDetail } from "@/lib/api";

/** Tahlil tab paneli — faqat mavjud tahlil ko'rsatiladi.
 *
 *  `editorial_state.available` bo'lmasa nashr qilinmagan/yashirin matn
 *  ochilmaydi — bo'sh holat chiziladi. `Editorial` ichida auth/paywall
 *  mantiqi allaqachon bor (kirmagan → login, yechmagan → Qvant),
 *  bu yerda qayta yozilmaydi.
 *
 *  Yetishmaydigan narsa yo'q: backend `ProblemDetail.editorial` +
 *  `editorial_state` ni beradi. Soxta matn qo'yilmaydi.
 */
export function ProblemEditorialPanel({
  problem,
  slug,
  locale,
}: {
  problem: ProblemDetail;
  slug: string;
  locale: Locale;
}) {
  return (
    <div className="min-w-0 space-y-6">
      <header>
        <h1 className="text-title-sm font-bold rw-strong">
          {problem.code !== null && (
            <span className="mr-2 font-mono text-theme-sm rw-faint tabular-nums">
              #{String(problem.code).padStart(4, "0")}
            </span>
          )}
          {problem.title}
        </h1>
      </header>

      {!problem.editorial_state.available ? (
        <Card>
          <EmptyState
            variant="card"
            title={t(locale, "editorial.lockedTitle")}
            hint={fill(t(locale, "problem.solvedAttempts"), {
              solved: problem.solved_count,
              attempts: problem.attempt_count,
            })}
            action={{
              label: t(locale, "problem.tab.statement"),
              href: `/problems/${slug}`,
            }}
          />
          <p className="mt-3 text-center text-theme-xs rw-faint">
            <Link
              href={`/problems/${slug}?tab=attempts` as Route}
              className="rw-accent-ink hover:underline"
            >
              {t(locale, "problem.tab.status")}
            </Link>
          </p>
        </Card>
      ) : (
        <Editorial
          slug={slug}
          text={problem.editorial}
          state={problem.editorial_state}
        />
      )}
    </div>
  );
}
